#!/usr/bin/env python3
"""
KiCad Schematic Analyzer
Parses a .kicad_sch file using kicad-cli and generates a structured Markdown report
suitable for LLM engineering review.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from contextlib import suppress

# Common power net name patterns
POWER_NET_PATTERNS = [
    r'^\+?\d+v\d*$',       # +12v, +5v, 3v3, etc.
    r'^-\d+v\d*$',        # -12v, -5v, etc.
    r'^gnd',              # gnd, ground, gnda, gndd
    r'^vcc',              # vcc, vcca, vccd
    r'^vdd',              # vdd
    r'^vss',              # vss
    r'^vee',              # vee
    r'^v\+$',             # V+
    r'^v-$',              # V-
    r'^power$',           # power
    r'^pwr',              # pwr, pwr_flag
]

def check_for_sheets(filepath):
    """
    Scans the .kicad_sch file for top-level (sheet ...) S-expressions.
    Returns True if a multi-sheet schematic is detected, False otherwise.
    Uses a parenthesis depth tracker to ignore sheets defined inside lib_symbols.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError as e:
        sys.stderr.write(f"Error reading schematic file: {e}\n")
        sys.exit(1)

    # Tokenizer regex: matches (, ), double-quoted strings (handling escapes), or non-space words
    tokens = re.finditer(r'\(|\)|"([^"\\]*(?:\\.[^"\\]*)*)"|([^\s()]+)', content)
    
    depth = 0
    in_lib_symbols = False
    lib_symbols_depth = 0
    
    for match in tokens:
        t = match.group(0)
        if t == '(':
            depth += 1
        elif t == ')':
            if in_lib_symbols and depth == lib_symbols_depth:
                in_lib_symbols = False
            depth -= 1
        else:
            # Check for top-level blocks directly inside (kicad_sch ...)
            if depth == 2:
                if t == 'lib_symbols':
                    in_lib_symbols = True
                    lib_symbols_depth = 2
                elif t == 'sheet' and not in_lib_symbols:
                    return True
                    
    return False

def check_kicad_cli():
    """
    Verifies that kicad-cli is installed and runs.
    """
    try:
        subprocess.run(['kicad-cli', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def export_netlist(sch_path, xml_path):
    """
    Runs kicad-cli to export the schematic netlist to XML.
    """
    cmd = ['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', xml_path, sch_path]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Failed to export netlist via kicad-cli:\n{e.stderr}\n")
        return False

def parse_xml_netlist(xml_path):
    """
    Parses the exported XML netlist and returns a structured dictionary.
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except (ET.ParseError, OSError) as e:
        sys.stderr.write(f"Error parsing XML netlist: {e}\n")
        sys.exit(1)

    # 1. Parse Metadata
    metadata = {
        'source': 'Unknown',
        'date': 'Unknown',
        'tool': 'Unknown'
    }
    design_elem = root.find('design')
    if design_elem is not None:
        source_elem = design_elem.find('source')
        if source_elem is not None:
            metadata['source'] = os.path.basename(source_elem.text)
        date_elem = design_elem.find('date')
        if date_elem is not None:
            metadata['date'] = date_elem.text
        tool_elem = design_elem.find('tool')
        if tool_elem is not None:
            metadata['tool'] = tool_elem.text

    # 2. Parse Components
    components = {}
    for comp in root.findall('.//components/comp'):
        ref = comp.attrib.get('ref')
        if not ref:
            continue

        value = comp.find('value').text if comp.find('value') is not None else ""
        desc = comp.find('description').text if comp.find('description') is not None else ""
        
        libsource = comp.find('libsource')
        lib_part = ""
        if libsource is not None:
            lib = libsource.attrib.get('lib', '')
            part = libsource.attrib.get('part', '')
            lib_part = f"{lib}:{part}" if lib and part else part
            if not desc:
                desc = libsource.attrib.get('description', '')

        # Gather fields
        fields = {}
        fields_elem = comp.find('fields')
        if fields_elem is not None:
            for field in fields_elem.findall('field'):
                name = field.attrib.get('name', '').strip()
                val = field.text.strip() if field.text else ""
                if name and val:
                    fields[name] = val

        # Handle footprint and datasheet (can be direct elements or fields)
        footprint = comp.find('footprint').text if comp.find('footprint') is not None else ""
        if not footprint:
            footprint = fields.get('Footprint', '')
            
        datasheet = comp.find('datasheet').text if comp.find('datasheet') is not None else ""
        if not datasheet:
            datasheet = fields.get('Datasheet', '')

        # Standard cleanups
        footprint = footprint.strip()
        datasheet = datasheet.strip()

        # Extract MPN & JLCPCB/LCSC fields
        mpn = ""
        jlcpcb_lcsc_fields = {}
        for name, val in fields.items():
            name_lower = name.lower()
            if name_lower in ['mpn', 'manufacturer part number', 'mfg part number']:
                mpn = val
            elif 'jlcpcb' in name_lower or 'lcsc' in name_lower:
                jlcpcb_lcsc_fields[name] = val

        # Get list of physical pins
        physical_pins = set()
        for unit in comp.findall('.//units/unit'):
            pins_elem = unit.find('pins')
            if pins_elem is not None:
                for pin in pins_elem.findall('pin'):
                    num = pin.attrib.get('num')
                    if num:
                        physical_pins.add(num)

        components[ref] = {
            'value': value.strip() if value else "",
            'lib_part': lib_part.strip() if lib_part else "",
            'footprint': footprint,
            'description': desc.strip() if desc else "",
            'datasheet': datasheet,
            'mpn': mpn.strip() if mpn else "",
            'jlcpcb_lcsc': jlcpcb_lcsc_fields,
            'physical_pins': physical_pins
        }

    # 3. Parse Nets
    nets = []
    connected_pins = set() # Set of (ref, pin)
    
    nets_elem = root.find('nets')
    if nets_elem is not None:
        for net in nets_elem.findall('net'):
            code = net.attrib.get('code', '')
            name = net.attrib.get('name', f"Net-{code}")
            
            nodes = []
            for node in net.findall('node'):
                node_ref = node.attrib.get('ref')
                node_pin = node.attrib.get('pin')
                pin_func = node.attrib.get('pinfunction', '')
                pin_type = node.attrib.get('pintype', '')
                
                if node_ref and node_pin:
                    nodes.append({
                        'ref': node_ref,
                        'pin': node_pin,
                        'function': pin_func,
                        'type': pin_type
                    })
                    connected_pins.add((node_ref, node_pin))
            
            nets.append({
                'code': code,
                'name': name,
                'nodes': nodes
            })

    return metadata, components, nets, connected_pins

def generate_markdown(metadata, components, nets, connected_pins):
    """
    Generates the final structured Markdown text.
    """
    lines = []
    
    # 4.1 Metadata Summary
    lines.append(f"# KiCad Schematic Design Report: {metadata['source']}")
    lines.append("")
    lines.append(f"- **Date:** {metadata['date']}")
    lines.append(f"- **KiCad Tool Version:** {metadata['tool']}")
    lines.append(f"- **Design Source:** {metadata['source']}")
    lines.append("")

    # 4.2 Component Catalog
    lines.append("## Component Catalog")
    lines.append("")
    # Sort components by reference designator naturally (e.g. C1, C2, R1, U1)
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
        
    for ref in sorted(components.keys(), key=natural_sort_key):
        comp = components[ref]
        lines.append(f"- **{ref}**")
        lines.append(f"  - **Value:** `{comp['value']}`")
        if comp['lib_part']:
            lines.append(f"  - **Library Part:** `{comp['lib_part']}`")
        if comp['footprint']:
            lines.append(f"  - **Footprint:** `{comp['footprint']}`")
        if comp['description']:
            lines.append(f"  - **Description:** {comp['description']}")
        if comp['datasheet'] and comp['datasheet'] != "~":
            lines.append(f"  - **Datasheet:** [{comp['datasheet']}]({comp['datasheet']})")
        if comp['mpn']:
            lines.append(f"  - **MPN:** `{comp['mpn']}`")
        for k, v in comp['jlcpcb_lcsc'].items():
            lines.append(f"  - **{k}:** `{v}`")
    lines.append("")

    # Identify Power Rails vs Signal Nets
    power_nets = []
    signal_nets = []
    
    power_patterns_compiled = [re.compile(p, re.IGNORECASE) for p in POWER_NET_PATTERNS]
    
    for net in nets:
        is_power = False
        # Rule 1: Check name matches pattern
        for pattern in power_patterns_compiled:
            if pattern.search(net['name']):
                is_power = True
                break
        
        # Rule 2: Check node pin types
        if not is_power:
            for node in net['nodes']:
                if node['type'] in ['power_in', 'power_out']:
                    is_power = True
                    break
        
        # Rule 3: Skip auto-generated unconnected nets
        if net['name'].startswith('unconnected-'):
            continue
            
        if is_power:
            power_nets.append(net)
        else:
            signal_nets.append(net)

    # Sort nets by name
    power_nets.sort(key=lambda x: x['name'])
    signal_nets.sort(key=lambda x: x['name'])

    # 4.3 Power Rails Audit
    lines.append("## Power Rails Audit")
    lines.append("")
    if not power_nets:
        lines.append("*No power rails identified.*")
        lines.append("")
    else:
        for net in power_nets:
            lines.append(f"### Net: {net['name']}")
            if not net['nodes']:
                lines.append("*(No connections)*")
            else:
                for node in sorted(net['nodes'], key=lambda x: natural_sort_key(x['ref'])):
                    func_str = f" ({node['function']})" if node['function'] else ""
                    type_str = f" / {node['type']}" if node['type'] else ""
                    lines.append(f"- **{node['ref']}** - Pin {node['pin']}{func_str}{type_str}")
            lines.append("")

    # 4.4 Connectivity Netlist
    lines.append("## Connectivity Netlist")
    lines.append("")
    if not signal_nets:
        lines.append("*No signal nets identified.*")
        lines.append("")
    else:
        for net in signal_nets:
            lines.append(f"### Net: {net['name']}")
            if not net['nodes']:
                lines.append("*(No connections)*")
            else:
                for node in sorted(net['nodes'], key=lambda x: natural_sort_key(x['ref'])):
                    func_str = f" ({node['function']})" if node['function'] else ""
                    type_str = f" / {node['type']}" if node['type'] else ""
                    lines.append(f"- **{node['ref']}** - Pin {node['pin']}{func_str}{type_str}")
            lines.append("")

    # 4.5 Unconnected / No-Connect Pins
    lines.append("## Unconnected & No-Connect Pins")
    lines.append("")
    
    unconnected_list = []
    
    # Check all physical pins from components
    for ref, comp in sorted(components.items(), key=lambda x: natural_sort_key(x[0])):
        for pin in sorted(comp['physical_pins'], key=natural_sort_key):
            if (ref, pin) not in connected_pins:
                unconnected_list.append((ref, pin, "Unconnected", "Not in netlist"))
                
    # Also check pins connected to explicit 'unconnected-' or 'no_connect' nets
    for net in nets:
        if net['name'].startswith('unconnected-'):
            for node in net['nodes']:
                unconnected_list.append((node['ref'], node['pin'], "Explicit No-Connect", node['type']))
        else:
            for node in net['nodes']:
                if 'no_connect' in node['type']:
                    unconnected_list.append((node['ref'], node['pin'], "No-Connect Type", node['type']))

    # Remove duplicates from unconnected_list
    seen = set()
    unique_unconnected = []
    for ref, pin, reason, ptype in unconnected_list:
        if (ref, pin) not in seen:
            seen.add((ref, pin))
            unique_unconnected.append((ref, pin, reason, ptype))

    # Sort
    unique_unconnected.sort(key=lambda x: (natural_sort_key(x[0]), natural_sort_key(x[1])))

    if not unique_unconnected:
        lines.append("*All component pins are connected.*")
        lines.append("")
    else:
        for ref, pin, reason, ptype in unique_unconnected:
            type_str = f" ({ptype})" if ptype else ""
            lines.append(f"- **{ref}** - Pin {pin} [{reason}]{type_str}")
        lines.append("")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Extract KiCad schematic metadata, components, and connectivity to Markdown for LLM analysis."
    )
    parser.add_argument(
        "schematic",
        help="Path to the KiCad .kicad_sch schematic file."
    )
    parser.add_argument(
        "-o", "--output",
        help="Optional path to save the generated Markdown report file."
    )
    
    args = parser.parse_args()

    sch_path = args.schematic

    # Validate file existence
    if not os.path.isfile(sch_path):
        sys.stderr.write(f"Error: Schematic file '{sch_path}' not found.\n")
        sys.exit(1)

    # 1. Multi-Sheet Pre-Check
    if check_for_sheets(sch_path):
        sys.stderr.write(
            "Error: Multi-sheet schematic detected. Please request the maintainer to update this script to support hierarchical multi-sheet designs.\n"
        )
        sys.exit(1)

    # 2. Verify kicad-cli accessibility
    if not check_kicad_cli():
        sys.stderr.write("Error: 'kicad-cli' command not found or not executable. Please verify it is in your system PATH.\n")
        sys.exit(1)

    # 3. Export XML netlist using a temp file
    temp_dir = tempfile.gettempdir()
    temp_xml_fd, temp_xml_path = tempfile.mkstemp(suffix=".xml", prefix="kicad_sch_net_", dir=temp_dir)
    os.close(temp_xml_fd)

    try:
        if not export_netlist(sch_path, temp_xml_path):
            sys.exit(1)

        # 4. Parse XML netlist
        metadata, components, nets, connected_pins = parse_xml_netlist(temp_xml_path)

        # 5. Generate Markdown
        markdown_content = generate_markdown(metadata, components, nets, connected_pins)

        # 6. Output to stdout or file
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as out_f:
                    out_f.write(markdown_content)
                print(f"Report successfully saved to {args.output}")
            except OSError as e:
                sys.stderr.write(f"Error writing output file: {e}\n")
                sys.exit(1)
        else:
            print(markdown_content)

    finally:
        # Cleanup temporary XML file
        if os.path.exists(temp_xml_path):
            with suppress(OSError):
                os.remove(temp_xml_path)

if __name__ == "__main__":
    main()
