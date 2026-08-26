#!/usr/bin/env python3
"""
KiCad Schematic Analyzer & Query Tool
Parses a .kicad_sch file using kicad-cli and generates structured Markdown reports
or targeted query outputs for LLM engineering review.
"""

import argparse
import glob
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from contextlib import suppress

# Common power net name patterns
POWER_NET_PATTERNS = [
    r"^\+?\d+v\d*$",  # +12v, +5v, 3v3, etc.
    r"^-\d+v\d*$",  # -12v, -5v, etc.
    r"^gnd",  # gnd, ground, gnda, gndd
    r"^vcc",  # vcc, vcca, vccd
    r"^vdd",  # vdd
    r"^vss",  # vss
    r"^vee",  # vee
    r"^v\+$",  # V+
    r"^v-$",  # V-
    r"^power$",  # power
    r"^pwr",  # pwr, pwr_flag
]

# Benign ERC checks to ignore when running in headless / automated environments
BENIGN_ERC_CHECKS = {
    "lib_symbol_issues",
    "footprint_link_issues",
}


def find_kicad_cli():
    """
    Attempts to find the kicad-cli executable.
    Checks PATH first, then standard OS-specific installation directories.
    """
    # 1. Check if kicad-cli is in system PATH
    cli_path = shutil.which("kicad-cli")
    if cli_path and is_executable_kicad(cli_path):
        return cli_path

    # 2. Check platform-specific standard paths
    system = platform.system().lower()
    candidate_paths = []

    if system == "darwin":
        candidate_paths.extend(
            [
                "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
                "/Applications/KiCad 10.0/KiCad.app/Contents/MacOS/kicad-cli",
                "/Applications/KiCad 9.0/KiCad.app/Contents/MacOS/kicad-cli",
                "/Applications/KiCad 8.0/KiCad.app/Contents/MacOS/kicad-cli",
                "/Applications/KiCad 7.0/KiCad.app/Contents/MacOS/kicad-cli",
                os.path.expanduser(
                    "~/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
                ),
                "/opt/homebrew/bin/kicad-cli",
                "/usr/local/bin/kicad-cli",
            ]
        )
    elif system == "windows":
        candidate_paths.extend(glob.glob(r"C:\Program Files\KiCad\*\bin\kicad-cli.exe"))
        candidate_paths.extend(
            glob.glob(r"C:\Program Files (x86)\KiCad\*\bin\kicad-cli.exe")
        )
    else:  # Linux / Unix
        candidate_paths.extend(
            [
                "/usr/bin/kicad-cli",
                "/usr/local/bin/kicad-cli",
                "/snap/bin/kicad.kicad-cli",
                "/var/lib/flatpak/exports/bin/org.kicad.KiCad",
            ]
        )

    for path in candidate_paths:
        if os.path.isfile(path) and is_executable_kicad(path):
            return path

    return None


def is_executable_kicad(path):
    """Tests if a given binary path is a functioning kicad-cli."""
    try:
        res = subprocess.run(
            [path, "--version"], capture_output=True, text=True, timeout=5, check=False
        )
        return res.returncode == 0
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return False


def get_hierarchical_sheets(filepath):
    """
    Scans the .kicad_sch file for top-level (sheet ...) S-expressions.
    Returns a list of discovered sheet names/files for hierarchical designs.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as e:
        sys.stderr.write(f"Error reading schematic file: {e}\n")
        return []

    tokens = re.finditer(r'\(|\)|"([^"\\]*(?:\\.[^"\\]*)*)"|([^\s()]+)', content)

    depth = 0
    in_lib_symbols = False
    lib_symbols_depth = 0
    sheets = []

    for match in tokens:
        t = match.group(0)
        if t == "(":
            depth += 1
        elif t == ")":
            if in_lib_symbols and depth == lib_symbols_depth:
                in_lib_symbols = False
            depth -= 1
        else:
            if depth == 2:
                if t == "lib_symbols":
                    in_lib_symbols = True
                    lib_symbols_depth = 2
                elif t == "sheet" and not in_lib_symbols:
                    current_sheet_name = f"Sheet_{len(sheets) + 1}"
                    sheets.append(current_sheet_name)

    return sheets


def export_netlist(kicad_cli, sch_path, xml_path):
    """Runs kicad-cli to export the schematic netlist to XML."""
    cmd = [
        kicad_cli,
        "sch",
        "export",
        "netlist",
        "--format",
        "kicadxml",
        "-o",
        xml_path,
        sch_path,
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Failed to export netlist via kicad-cli:\n{e.stderr}\n")
        return False


def run_erc(kicad_cli, sch_path):
    """
    Runs kicad-cli sch erc and parses the electrical rules check report.
    Filters out environment/library noise (e.g. unmapped symbol libraries in headless mode).
    """
    temp_dir = tempfile.gettempdir()
    temp_rpt_fd, temp_rpt_path = tempfile.mkstemp(
        suffix=".rpt", prefix="kicad_sch_erc_", dir=temp_dir
    )
    os.close(temp_rpt_fd)

    cmd = [
        kicad_cli,
        "sch",
        "erc",
        "-o",
        temp_rpt_path,
        sch_path,
    ]

    violations = []
    erc_summary = {"total_raw": 0, "filtered": 0, "errors": 0, "warnings": 0}

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=False)
        if os.path.exists(temp_rpt_path):
            with open(temp_rpt_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            entry_regex = re.compile(
                r"^\[([a-zA-Z0-9_]+)\]:\s*(.*?)(?=\n\[|\n\s*\*\*|\Z)",
                re.MULTILINE | re.DOTALL,
            )
            for match in entry_regex.finditer(content):
                v_type = match.group(1).strip()
                block_body = match.group(2).strip()

                erc_summary["total_raw"] += 1
                if v_type in BENIGN_ERC_CHECKS:
                    erc_summary["filtered"] += 1
                    continue

                lines = [l.strip() for l in block_body.splitlines() if l.strip()]
                description = lines[0] if lines else ""
                severity = "warning"
                context = ""

                for l in lines[1:]:
                    if l.startswith(";"):
                        severity = l.lstrip(";").strip()
                    elif l.startswith("@"):
                        context = l.strip()

                if severity.lower() == "error":
                    erc_summary["errors"] += 1
                else:
                    erc_summary["warnings"] += 1

                violations.append(
                    {
                        "type": v_type,
                        "severity": severity,
                        "description": description,
                        "context": context,
                    }
                )

    except (subprocess.SubprocessError, OSError) as e:
        sys.stderr.write(f"Warning: Could not run ERC: {e}\n")
    finally:
        if os.path.exists(temp_rpt_path):
            with suppress(OSError):
                os.remove(temp_rpt_path)

    return violations, erc_summary


def parse_xml_netlist(xml_path):
    """Parses the exported XML netlist and returns structured data."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except (ET.ParseError, OSError) as e:
        sys.stderr.write(f"Error parsing XML netlist: {e}\n")
        sys.exit(1)

    # 1. Metadata
    metadata = {"source": "Unknown", "date": "Unknown", "tool": "Unknown"}
    design_elem = root.find("design")
    if design_elem is not None:
        source_elem = design_elem.find("source")
        if source_elem is not None:
            metadata["source"] = os.path.basename(source_elem.text)
        date_elem = design_elem.find("date")
        if date_elem is not None:
            metadata["date"] = date_elem.text
        tool_elem = design_elem.find("tool")
        if tool_elem is not None:
            metadata["tool"] = tool_elem.text

    # 2. Components
    components = {}
    for comp in root.findall(".//components/comp"):
        ref = comp.attrib.get("ref")
        if not ref:
            continue

        value = comp.find("value").text if comp.find("value") is not None else ""
        desc = (
            comp.find("description").text
            if comp.find("description") is not None
            else ""
        )

        libsource = comp.find("libsource")
        lib_part = ""
        if libsource is not None:
            lib = libsource.attrib.get("lib", "")
            part = libsource.attrib.get("part", "")
            lib_part = f"{lib}:{part}" if lib and part else part
            if not desc:
                desc = libsource.attrib.get("description", "")

        fields = {}
        fields_elem = comp.find("fields")
        if fields_elem is not None:
            for field in fields_elem.findall("field"):
                name = field.attrib.get("name", "").strip()
                val = field.text.strip() if field.text else ""
                if name and val:
                    fields[name] = val

        footprint = (
            comp.find("footprint").text if comp.find("footprint") is not None else ""
        )
        if not footprint:
            footprint = fields.get("Footprint", "")

        datasheet = (
            comp.find("datasheet").text if comp.find("datasheet") is not None else ""
        )
        if not datasheet:
            datasheet = fields.get("Datasheet", "")

        footprint = footprint.strip()
        datasheet = datasheet.strip()

        mpn = ""
        jlcpcb_lcsc_fields = {}
        for name, val in fields.items():
            name_lower = name.lower()
            if name_lower in ["mpn", "manufacturer part number", "mfg part number"]:
                mpn = val
            elif "jlcpcb" in name_lower or "lcsc" in name_lower:
                jlcpcb_lcsc_fields[name] = val

        physical_pins = set()
        for unit in comp.findall(".//units/unit"):
            pins_elem = unit.find("pins")
            if pins_elem is not None:
                for pin in pins_elem.findall("pin"):
                    num = pin.attrib.get("num")
                    if num:
                        physical_pins.add(num)

        components[ref] = {
            "value": value.strip() if value else "",
            "lib_part": lib_part.strip() if lib_part else "",
            "footprint": footprint,
            "description": desc.strip() if desc else "",
            "datasheet": datasheet,
            "mpn": mpn.strip() if mpn else "",
            "jlcpcb_lcsc": jlcpcb_lcsc_fields,
            "physical_pins": physical_pins,
        }

    # 3. Nets
    nets = []
    connected_pins = set()

    nets_elem = root.find("nets")
    if nets_elem is not None:
        for net in nets_elem.findall("net"):
            code = net.attrib.get("code", "")
            name = net.attrib.get("name", f"Net-{code}")

            nodes = []
            for node in net.findall("node"):
                node_ref = node.attrib.get("ref")
                node_pin = node.attrib.get("pin")
                pin_func = node.attrib.get("pinfunction", "")
                pin_type = node.attrib.get("pintype", "")

                if node_ref and node_pin:
                    nodes.append(
                        {
                            "ref": node_ref,
                            "pin": node_pin,
                            "function": pin_func,
                            "type": pin_type,
                        }
                    )
                    connected_pins.add((node_ref, node_pin))

            nets.append({"code": code, "name": name, "nodes": nodes})

    return metadata, components, nets, connected_pins


def natural_sort_key(s):
    """Sort key for alphanumeric strings (e.g. R1, R2, R10)."""
    return [
        int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)
    ]


def collapse_reference_list(refs):
    """
    Collapses a list of reference designators like ['R1', 'R2', 'R3', 'R5']
    into 'R1-R3, R5'.
    """
    if not refs:
        return ""

    prefix_map = {}
    for ref in refs:
        m = re.match(r"^([a-zA-Z_#]+)(\d+)$", ref)
        if m:
            pfx, num = m.group(1), int(m.group(2))
            prefix_map.setdefault(pfx, []).append(num)
        else:
            prefix_map.setdefault(ref, []).append(None)

    result_parts = []
    for pfx in sorted(prefix_map.keys(), key=natural_sort_key):
        nums = prefix_map[pfx]
        if None in nums:
            result_parts.append(pfx)
            continue

        nums = sorted(set(nums))
        ranges = []
        range_start = nums[0]
        prev = nums[0]

        for n in nums[1:]:
            if n == prev + 1:
                prev = n
            else:
                if prev == range_start:
                    ranges.append(f"{pfx}{range_start}")
                elif prev == range_start + 1:
                    ranges.append(f"{pfx}{range_start}, {pfx}{prev}")
                else:
                    ranges.append(f"{pfx}{range_start}–{pfx}{prev}")
                range_start = n
                prev = n

        if prev == range_start:
            ranges.append(f"{pfx}{range_start}")
        elif prev == range_start + 1:
            ranges.append(f"{pfx}{range_start}, {pfx}{prev}")
        else:
            ranges.append(f"{pfx}{range_start}–{pfx}{prev}")

        result_parts.extend(ranges)

    return ", ".join(result_parts)


def parse_resistor_value(val_str):
    """Parses a resistor string (e.g. 1k, 100K, 4.7k, 470R, 10M) to ohms."""
    if not val_str:
        return None
    s = val_str.strip().upper().replace("OHM", "").replace("Ω", "").replace("R", ".")
    m = re.match(r"^(\d+)([KMG])(\d*)$", s)
    if m:
        s = (
            f"{m.group(1)}.{m.group(3)}{m.group(2)}"
            if m.group(3)
            else f"{m.group(1)}{m.group(2)}"
        )

    multiplier = 1.0
    if "K" in s:
        multiplier = 1e3
        s = s.replace("K", "")
    elif "M" in s:
        multiplier = 1e6
        s = s.replace("M", "")

    s = s.rstrip(".")
    try:
        return float(s) * multiplier
    except ValueError:
        return None


def parse_capacitor_value(val_str):
    """Parses a capacitor string (e.g. 100nF, 10uF, 100pF, 0.1uF, 10uF/25V) to Farads."""
    if not val_str:
        return None
    s = val_str.split("/")[0].split(" ")[0].strip().upper().replace("F", "")

    multiplier = 1.0
    if "P" in s:
        multiplier = 1e-12
        s = s.replace("P", "")
    elif "N" in s:
        multiplier = 1e-9
        s = s.replace("N", "")
    elif "U" in s or "µ" in s:
        multiplier = 1e-6
        s = s.replace("U", "").replace("µ", "")
    elif "M" in s:
        multiplier = 1e-3
        s = s.replace("M", "")

    try:
        return float(s) * multiplier
    except ValueError:
        return None


def format_frequency(hz):
    """Formats frequency in Hz, kHz, MHz, or GHz."""
    if hz >= 1e9:
        return f"{hz / 1e9:.2f} GHz"
    elif hz >= 1e6:
        return f"{hz / 1e6:.2f} MHz"
    elif hz >= 1e3:
        return f"{hz / 1e3:.2f} kHz"
    else:
        return f"{hz:.2f} Hz"


def classify_nets(nets):
    """Classifies nets into power nets and signal nets."""
    power_nets = []
    signal_nets = []
    power_patterns_compiled = [re.compile(p, re.IGNORECASE) for p in POWER_NET_PATTERNS]

    for net in nets:
        is_power = False
        for pattern in power_patterns_compiled:
            if pattern.search(net["name"]):
                is_power = True
                break

        if not is_power:
            for node in net["nodes"]:
                if node["type"] in ["power_in", "power_out"]:
                    is_power = True
                    break

        if net["name"].startswith("unconnected-"):
            continue

        if is_power:
            power_nets.append(net)
        else:
            signal_nets.append(net)

    power_nets.sort(key=lambda x: x["name"])
    signal_nets.sort(key=lambda x: x["name"])
    return power_nets, signal_nets


def detect_circuit_topologies(components, nets, power_net_names):
    """
    Identifies common circuit topologies:
    1. RC low-pass / high-pass filters with cutoff frequencies on signal nets.
    2. Op-amp stage configurations (buffers, followers, constant-current drivers).
    """
    findings = []

    net_map = {n["name"]: n for n in nets}
    ref_to_nets = {}
    for net in nets:
        for node in net["nodes"]:
            ref_to_nets.setdefault(node["ref"], []).append(
                (node["pin"], net["name"], node["type"], node["function"])
            )

    # 1. Detect RC Filters on SIGNAL nets only (exclude GND and power rails)
    for net in nets:
        if net["name"] in power_net_names or net["name"].startswith("unconnected-"):
            continue

        resistors = [node for node in net["nodes"] if node["ref"].startswith("R")]
        capacitors = [node for node in net["nodes"] if node["ref"].startswith("C")]

        if resistors and capacitors:
            for r_node in resistors:
                for c_node in capacitors:
                    r_val = parse_resistor_value(
                        components.get(r_node["ref"], {}).get("value", "")
                    )
                    c_val = parse_capacitor_value(
                        components.get(c_node["ref"], {}).get("value", "")
                    )

                    if r_val and c_val and r_val > 0 and c_val > 0:
                        fc = 1.0 / (2.0 * math.pi * r_val * c_val)
                        findings.append(
                            f"- **RC Filter on net `{net['name']}`**: `{r_node['ref']}` ({components[r_node['ref']]['value']}) + "
                            f"`{c_node['ref']}` ({components[c_node['ref']]['value']}) $\\rightarrow$ "
                            f"Cutoff frequency $f_c \\approx$ **{format_frequency(fc)}**"
                        )

    # 2. Detect Op-Amp Configurations
    for ref, comp in sorted(components.items(), key=lambda x: natural_sort_key(x[0])):
        lib_part = comp["lib_part"].lower()
        val = comp["value"].lower()
        if (
            "tl07" in lib_part
            or "tl07" in val
            or "opamp" in lib_part
            or "operational" in lib_part
            or ref.startswith("U")
        ):
            pins = ref_to_nets.get(ref, [])
            pin_dict = {p[0]: p[1] for p in pins}

            quad_units = [
                ("A", "1", "2", "3"),
                ("B", "7", "6", "5"),
                ("C", "8", "9", "10"),
                ("D", "14", "13", "12"),
            ]
            for unit_name, out_pin, inv_pin, noninv_pin in quad_units:
                out_net = pin_dict.get(out_pin)
                inv_net = pin_dict.get(inv_pin)
                noninv_net = pin_dict.get(noninv_pin)

                if out_net and inv_net:
                    if out_net == inv_net:
                        findings.append(
                            f"- **Op-Amp Buffer / Voltage Follower**: `{ref}` (Unit {unit_name}, Pins {out_pin}/{inv_pin}/{noninv_pin}) "
                            f"configured with unity-gain feedback ($A_v = 1$) on net `{noninv_net}`."
                        )
                    else:
                        inv_nodes = net_map.get(inv_net, {}).get("nodes", [])
                        out_nodes = net_map.get(out_net, {}).get("nodes", [])
                        shared_diodes = {
                            n["ref"] for n in inv_nodes if n["ref"].startswith("D")
                        } & {n["ref"] for n in out_nodes if n["ref"].startswith("D")}
                        if shared_diodes:
                            d_list = ", ".join(
                                sorted(shared_diodes, key=natural_sort_key)
                            )
                            findings.append(
                                f"- **Active Constant-Current Diode/LED Driver**: `{ref}` (Unit {unit_name}) "
                                f"drives {d_list} in negative feedback loop referenced to `{inv_net}`."
                            )

    return findings


# --- Markdown Generation Functions for Targeted Queries ---


def generate_summary_markdown(metadata, components, nets, hierarchical_sheets):
    """Generates design metadata and high-level summary statistics."""
    lines = []
    lines.append(f"# Schematic Summary: {metadata['source']}")
    lines.append("")
    lines.append(f"- **Design Source:** {metadata['source']}")
    lines.append(f"- **Date:** {metadata['date']}")
    lines.append(f"- **KiCad Tool Version:** {metadata['tool']}")
    if hierarchical_sheets:
        lines.append(
            f"- **Hierarchical Sheets ({len(hierarchical_sheets)}):** {', '.join(hierarchical_sheets)}"
        )
    else:
        lines.append("- **Schematic Structure:** Single Sheet")
    lines.append(f"- **Total Components:** {len(components)}")
    lines.append(f"- **Total Nets:** {len(nets)}")
    return "\n".join(lines)


def generate_erc_markdown(erc_violations, erc_summary):
    """Generates Electrical Rules Check (ERC) Markdown report."""
    lines = []
    lines.append("## Electrical Rules Check (ERC)")
    lines.append("")
    if not erc_violations:
        lines.append("> [!NOTE]")
        lines.append("> **ERC Status: PASS (0 Electrical Violations)**")
        lines.append(
            f"> No electrical errors or warnings detected by `kicad-cli sch erc`. (Filtered {erc_summary.get('filtered', 0)} headless environment library warnings)."
        )
    else:
        lines.append("> [!WARNING]")
        lines.append(
            f"> **ERC Found {erc_summary['errors']} Error(s) and {erc_summary['warnings']} Warning(s):**"
        )
        lines.append("")
        for v in erc_violations:
            sev_badge = (
                "**[ERROR]**" if v["severity"].lower() == "error" else "*[WARNING]*"
            )
            lines.append(f"- {sev_badge} `{v['type']}`: {v['description']}")
            if v["context"]:
                lines.append(f"  - Context: `{v['context']}`")
    return "\n".join(lines)


def generate_bom_markdown(components):
    """Generates consolidated Bill of Materials (BOM) table."""
    lines = []
    lines.append("## Bill of Materials (BOM) Summary")
    lines.append("")
    lines.append(
        "| Qty | References | Value / Type | Footprint | LCSC / MPN | Description |"
    )
    lines.append("| :---: | :--- | :--- | :--- | :--- | :--- |")

    bom_groups = {}
    for ref, comp in components.items():
        lcsc_val = ", ".join(f"{v}" for k, v in comp["jlcpcb_lcsc"].items())
        mpn_val = comp["mpn"]
        part_id = lcsc_val or mpn_val or "-"

        # If it's a connector with functional label as value (e.g. Jack with value=INPUT1), use lib_part/footprint for grouping
        val_display = comp["value"]
        if comp["lib_part"].startswith("Connector") and comp["footprint"]:
            val_group = comp["lib_part"].split(":")[-1]
            val_display = val_group
        else:
            val_group = comp["value"]

        key = (val_group, val_display, comp["footprint"], part_id, comp["description"])
        bom_groups.setdefault(key, []).append(ref)

    sorted_groups = sorted(
        bom_groups.items(), key=lambda x: (natural_sort_key(x[1][0]), x[0][0])
    )
    for (val_group, val_disp, fp, part_id, desc), refs in sorted_groups:
        refs_sorted = sorted(refs, key=natural_sort_key)
        ref_str = collapse_reference_list(refs_sorted)
        fp_short = fp.split(":")[-1] if ":" in fp else fp
        lines.append(
            f"| **{len(refs)}** | `{ref_str}` | `{val_disp or '-'}` | `{fp_short or '-'}` | `{part_id}` | {desc or '-'} |"
        )
    return "\n".join(lines)


def generate_topologies_markdown(components, nets, power_net_names):
    """Generates detected circuit topologies report."""
    lines = []
    lines.append("## Detected Circuit Topologies & Calculations")
    lines.append("")
    topologies = detect_circuit_topologies(components, nets, power_net_names)
    if topologies:
        lines.extend(topologies)
    else:
        lines.append("*No recognizable analog/digital subcircuits detected.*")
    return "\n".join(lines)


def generate_power_markdown(power_nets):
    """Generates Power Rails Audit report."""
    lines = []
    lines.append("## Power Rails Audit")
    lines.append("")
    if not power_nets:
        lines.append("*No power rails identified.*")
    else:
        for net in power_nets:
            lines.append(f"### Net: `{net['name']}` ({len(net['nodes'])} connections)")
            if not net["nodes"]:
                lines.append("*(No connections)*")
            else:
                for node in sorted(
                    net["nodes"], key=lambda x: natural_sort_key(x["ref"])
                ):
                    func_str = f" ({node['function']})" if node["function"] else ""
                    type_str = f" / {node['type']}" if node["type"] else ""
                    lines.append(
                        f"- **{node['ref']}** - Pin {node['pin']}{func_str}{type_str}"
                    )
            lines.append("")
    return "\n".join(lines).rstrip()


def generate_nets_markdown(signal_nets, filter_net=None, filter_ref=None):
    """
    Generates signal netlist connectivity report, with optional filtering by net name or component ref.
    """
    lines = []
    title = "## Signal Netlist"
    if filter_net:
        title += f" (Filtered by net: '{filter_net}')"
    if filter_ref:
        title += f" (Filtered by component: '{filter_ref}')"

    lines.append(title)
    lines.append("")

    matching_nets = []
    for net in signal_nets:
        if filter_net and filter_net.lower() not in net["name"].lower():
            continue
        if filter_ref:
            has_ref = any(
                node["ref"].lower() == filter_ref.lower() for node in net["nodes"]
            )
            if not has_ref:
                continue
        matching_nets.append(net)

    if not matching_nets:
        lines.append("*No matching signal nets found.*")
    else:
        for net in matching_nets:
            lines.append(f"### Net: `{net['name']}`")
            if not net["nodes"]:
                lines.append("*(No connections)*")
            else:
                for node in sorted(
                    net["nodes"], key=lambda x: natural_sort_key(x["ref"])
                ):
                    func_str = f" ({node['function']})" if node["function"] else ""
                    type_str = f" / {node['type']}" if node["type"] else ""
                    lines.append(
                        f"- **{node['ref']}** - Pin {node['pin']}{func_str}{type_str}"
                    )
            lines.append("")

    return "\n".join(lines).rstrip()


def generate_unconnected_markdown(components, nets, connected_pins):
    """Generates Unconnected and No-Connect Pins report."""
    lines = []
    lines.append("## Unconnected & No-Connect Pins")
    lines.append("")

    unconnected_list = []
    for ref, comp in sorted(components.items(), key=lambda x: natural_sort_key(x[0])):
        for pin in sorted(comp["physical_pins"], key=natural_sort_key):
            if (ref, pin) not in connected_pins:
                unconnected_list.append((ref, pin, "Unconnected", "Not in netlist"))

    for net in nets:
        if net["name"].startswith("unconnected-"):
            for node in net["nodes"]:
                unconnected_list.append(
                    (node["ref"], node["pin"], "Explicit No-Connect", node["type"])
                )
        else:
            for node in net["nodes"]:
                if "no_connect" in node["type"]:
                    unconnected_list.append(
                        (node["ref"], node["pin"], "No-Connect Type", node["type"])
                    )

    seen = set()
    unique_unconnected = []
    for ref, pin, reason, ptype in unconnected_list:
        if (ref, pin) not in seen:
            seen.add((ref, pin))
            unique_unconnected.append((ref, pin, reason, ptype))

    unique_unconnected.sort(
        key=lambda x: (natural_sort_key(x[0]), natural_sort_key(x[1]))
    )

    if not unique_unconnected:
        lines.append("*All component pins are connected.*")
    else:
        for ref, pin, reason, ptype in unique_unconnected:
            type_str = f" ({ptype})" if ptype else ""
            lines.append(f"- **{ref}** - Pin {pin} [{reason}]{type_str}")

    return "\n".join(lines)


def generate_full_report(
    metadata,
    components,
    nets,
    connected_pins,
    hierarchical_sheets,
    erc_violations,
    erc_summary,
):
    """Combines all report sections into a comprehensive Markdown report."""
    power_nets, signal_nets = classify_nets(nets)
    power_net_names = {n["name"] for n in power_nets}

    sections = [
        generate_summary_markdown(
            metadata, components, nets, hierarchical_sheets
        ),
        generate_erc_markdown(erc_violations, erc_summary),
        generate_bom_markdown(components),
        generate_topologies_markdown(components, nets, power_net_names),
        generate_power_markdown(power_nets),
        generate_nets_markdown(signal_nets),
        generate_unconnected_markdown(components, nets, connected_pins),
    ]
    return "\n\n".join(sections)


def output_result(content, output_path=None):
    """Outputs Markdown string to stdout or writes to a file."""
    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(content + "\n")
            print(f"Output successfully saved to {output_path}")
        except OSError as e:
            sys.stderr.write(f"Error writing output file: {e}\n")
            sys.exit(1)
    else:
        print(content)


# --- Subcommand Handlers ---


def handle_summary(args, kicad_cli):
    """Handler for 'summary' query."""
    hierarchical_sheets = get_hierarchical_sheets(args.schematic)
    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="kicad_sch_net_", delete=True
    ) as temp_xml:
        if not export_netlist(kicad_cli, args.schematic, temp_xml.name):
            sys.exit(1)
        metadata, components, nets, _ = parse_xml_netlist(temp_xml.name)
        out = generate_summary_markdown(
            metadata, components, nets, hierarchical_sheets
        )
        output_result(out, args.output)


def handle_erc(args, kicad_cli):
    """Handler for 'erc' query."""
    erc_violations, erc_summary = run_erc(kicad_cli, args.schematic)
    out = generate_erc_markdown(erc_violations, erc_summary)
    output_result(out, args.output)


def handle_bom(args, kicad_cli):
    """Handler for 'bom' query."""
    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="kicad_sch_net_", delete=True
    ) as temp_xml:
        if not export_netlist(kicad_cli, args.schematic, temp_xml.name):
            sys.exit(1)
        _, components, _, _ = parse_xml_netlist(temp_xml.name)
        out = generate_bom_markdown(components)
        output_result(out, args.output)


def handle_topologies(args, kicad_cli):
    """Handler for 'topologies' / 'circuits' query."""
    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="kicad_sch_net_", delete=True
    ) as temp_xml:
        if not export_netlist(kicad_cli, args.schematic, temp_xml.name):
            sys.exit(1)
        _, components, nets, _ = parse_xml_netlist(temp_xml.name)
        power_nets, _ = classify_nets(nets)
        power_net_names = {n["name"] for n in power_nets}
        out = generate_topologies_markdown(components, nets, power_net_names)
        output_result(out, args.output)


def handle_power(args, kicad_cli):
    """Handler for 'power' query."""
    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="kicad_sch_net_", delete=True
    ) as temp_xml:
        if not export_netlist(kicad_cli, args.schematic, temp_xml.name):
            sys.exit(1)
        _, _, nets, _ = parse_xml_netlist(temp_xml.name)
        power_nets, _ = classify_nets(nets)
        out = generate_power_markdown(power_nets)
        output_result(out, args.output)


def handle_nets(args, kicad_cli):
    """Handler for 'nets' query."""
    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="kicad_sch_net_", delete=True
    ) as temp_xml:
        if not export_netlist(kicad_cli, args.schematic, temp_xml.name):
            sys.exit(1)
        _, _, nets, _ = parse_xml_netlist(temp_xml.name)
        _, signal_nets = classify_nets(nets)
        out = generate_nets_markdown(
            signal_nets, filter_net=args.net, filter_ref=args.ref
        )
        output_result(out, args.output)


def handle_unconnected(args, kicad_cli):
    """Handler for 'unconnected' query."""
    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="kicad_sch_net_", delete=True
    ) as temp_xml:
        if not export_netlist(kicad_cli, args.schematic, temp_xml.name):
            sys.exit(1)
        _, components, nets, connected_pins = parse_xml_netlist(temp_xml.name)
        out = generate_unconnected_markdown(components, nets, connected_pins)
        output_result(out, args.output)


def handle_report(args, kicad_cli):
    """Handler for 'report' / 'all' query (comprehensive report)."""
    hierarchical_sheets = get_hierarchical_sheets(args.schematic)
    erc_violations, erc_summary = run_erc(kicad_cli, args.schematic)

    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="kicad_sch_net_", delete=True
    ) as temp_xml:
        if not export_netlist(kicad_cli, args.schematic, temp_xml.name):
            sys.exit(1)
        metadata, components, nets, connected_pins = parse_xml_netlist(temp_xml.name)
        out = generate_full_report(
            metadata,
            components,
            nets,
            connected_pins,
            hierarchical_sheets,
            erc_violations,
            erc_summary,
        )
        output_result(out, args.output)


def main():
    parser = argparse.ArgumentParser(
        prog="analyze_schematic.py",
        description=(
            "KiCad Schematic Analyzer & Targeted Query CLI.\n"
            "Extracts targeted schematic data (BOM, ERC, Power, Nets, Topologies, Unconnected pins) "
            "or generates a full Markdown review report."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run --isolated analyze_schematic.py --help\n"
            "  uv run --isolated analyze_schematic.py summary path/to/design.kicad_sch\n"
            "  uv run --isolated analyze_schematic.py bom path/to/design.kicad_sch\n"
            "  uv run --isolated analyze_schematic.py erc path/to/design.kicad_sch\n"
            "  uv run --isolated analyze_schematic.py power path/to/design.kicad_sch\n"
            "  uv run --isolated analyze_schematic.py topologies path/to/design.kicad_sch\n"
            "  uv run --isolated analyze_schematic.py nets path/to/design.kicad_sch --ref U1\n"
            "  uv run --isolated analyze_schematic.py nets path/to/design.kicad_sch --net IN_A\n"
            "  uv run --isolated analyze_schematic.py unconnected path/to/design.kicad_sch\n"
            "  uv run --isolated analyze_schematic.py report path/to/design.kicad_sch -o report.md\n"
        ),
    )

    subparsers = parser.add_subparsers(
        title="Available Query Subcommands",
        dest="command",
        help="Run `analyze_schematic.py <command> --help` for specific query options.",
    )

    def add_common_args(sub_p):
        sub_p.add_argument(
            "schematic",
            help="Path to the KiCad .kicad_sch schematic file.",
        )
        sub_p.add_argument(
            "-o",
            "--output",
            help="Optional file path to save output Markdown instead of printing to stdout.",
        )

    # 1. summary
    p_summary = subparsers.add_parser(
        "summary",
        help="Design overview, sheet hierarchy, and metadata summary.",
        description="Extract design metadata (date, tool, source), sheet hierarchy, and overall counts.",
    )
    add_common_args(p_summary)
    p_summary.set_defaults(func=handle_summary)

    # 2. erc
    p_erc = subparsers.add_parser(
        "erc",
        help="Run Electrical Rules Check (ERC) and report errors/warnings.",
        description="Executes kicad-cli sch erc, filtering out headless environment library noise.",
    )
    add_common_args(p_erc)
    p_erc.set_defaults(func=handle_erc)

    # 3. bom
    p_bom = subparsers.add_parser(
        "bom",
        help="Consolidated Bill of Materials (BOM) table.",
        description="Generates a compact BOM table grouping parts by value, footprint, LCSC/MPN, and reference ranges.",
    )
    add_common_args(p_bom)
    p_bom.set_defaults(func=handle_bom)

    # 4. topologies / circuits
    p_topologies = subparsers.add_parser(
        "topologies",
        aliases=["circuits"],
        help="Detect analog/digital circuit topologies (filters, op-amps).",
        description="Detects RC filters (with calculated cutoff fc), op-amp voltage followers, active LED drivers, etc.",
    )
    add_common_args(p_topologies)
    p_topologies.set_defaults(func=handle_topologies)

    # 5. power
    p_power = subparsers.add_parser(
        "power",
        help="Audit power rails and all attached component pins.",
        description="Identifies power nets (+12V, -12V, GND, VCC, etc.) and lists every connected component pin.",
    )
    add_common_args(p_power)
    p_power.set_defaults(func=handle_power)

    # 6. nets
    p_nets = subparsers.add_parser(
        "nets",
        help="Inspect signal netlist connectivity with optional filters.",
        description="Lists signal nets and their connected pins. Allows filtering by net name or component reference.",
    )
    add_common_args(p_nets)
    p_nets.add_argument(
        "--net",
        help="Filter signal nets by name (substring match, case-insensitive).",
    )
    p_nets.add_argument(
        "--ref",
        help="Filter signal nets connected to a specific component reference (e.g. U1, J1, R5).",
    )
    p_nets.set_defaults(func=handle_nets)

    # 7. unconnected
    p_unconn = subparsers.add_parser(
        "unconnected",
        help="List unconnected and explicit no-connect component pins.",
        description="Finds physical pins that are missing from nets or explicitly marked as no-connect.",
    )
    add_common_args(p_unconn)
    p_unconn.set_defaults(func=handle_unconnected)

    # 8. report / all
    p_report = subparsers.add_parser(
        "report",
        aliases=["all"],
        help="Generate the full, comprehensive Markdown report (combining all sections).",
        description="Runs full analysis (Metadata, ERC, BOM, Topologies, Power Rails, Signal Netlist, Unconnected Pins).",
    )
    add_common_args(p_report)
    p_report.set_defaults(func=handle_report)

    # Legacy fallback / no subcommand support
    # If the user runs `analyze_schematic.py file.kicad_sch` without a subcommand,
    # or runs without args, show help or parse properly.
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # If first positional argument is a file ending in .kicad_sch (legacy usage), treat as 'report'
    if len(sys.argv) > 1 and sys.argv[1].endswith(".kicad_sch") and sys.argv[1] not in subparsers.choices:
        sys.argv.insert(1, "report")

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help(sys.stderr)
        sys.exit(1)

    sch_path = args.schematic
    if not os.path.isfile(sch_path):
        sys.stderr.write(f"Error: Schematic file '{sch_path}' not found.\n")
        sys.exit(1)

    # Discover kicad-cli binary
    kicad_cli = find_kicad_cli()
    if not kicad_cli:
        sys.stderr.write(
            "Error: 'kicad-cli' command not found in PATH or standard installation directories.\n"
            "Please ensure KiCad 7/8/9/10 is installed.\n"
        )
        sys.exit(1)

    args.func(args, kicad_cli)


if __name__ == "__main__":
    main()
