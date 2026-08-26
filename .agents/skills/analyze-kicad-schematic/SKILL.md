---
name: analyze-kicad-schematic
description: >-
  Analyzes KiCad schematic files (.kicad_sch) and generates structured markdown
  reports or targeted query results (BOM, ERC, power rails, signal netlists,
  circuit topologies, unconnected pins). Use this skill when reviewing, auditing,
  or troubleshooting KiCad schematic designs.
---

# KiCad Schematic Analyzer

This skill provides automated analysis of KiCad 7/8/9/10+ schematic (`.kicad_sch`) files using `kicad-cli`. It supports **modular CLI subcommands** so you can query specific aspects of a schematic without polluting the context with monolithic reports, as well as generating full comprehensive Markdown reports.

## Prerequisites

- **uv** (preferred runtime) or **Python 3.6+**
- **KiCad CLI (`kicad-cli`)**: Auto-detected from system `PATH` or standard installation locations:
  - macOS: `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`, `/Applications/KiCad <version>/...`, Homebrew (`/opt/homebrew/bin/kicad-cli`).
  - Linux: `/usr/bin/kicad-cli`, `/usr/local/bin/kicad-cli`, Snap, Flatpak.
  - Windows: `C:\Program Files\KiCad\<version>\bin\kicad-cli.exe`.

## Tool Script

The analysis script is located at:
- [`scripts/analyze_schematic.py`](./scripts/analyze_schematic.py)

---

## Discovering Commands & Options (`--help`)

Always check `--help` using `uv run --isolated` to inspect available query subcommands or specific subcommand flags:

```bash
# View top-level help and list of subcommands
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py --help

# View help and filtering options for a specific subcommand
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py nets --help
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py bom --help
```

*(Fallback without uv: `python3 .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py --help`)*

---

## Targeted Query Subcommands

Instead of running a monolithic report, prefer running the specific subcommand relevant to the question being asked:

| Subcommand | Description | When to use |
| :--- | :--- | :--- |
| `summary` | Design overview, KiCad version, sheet hierarchy, total components/nets | Initial inspection or high-level sanity check |
| `erc` | Runs ERC check (`kicad-cli sch erc`) and reports true electrical errors/warnings | Checking electrical validity, unrouted nets, or conflicts |
| `bom` | Consolidated Bill of Materials table grouped by value, footprint, LCSC/MPN | Part counting, component lookup, sourcing reviews |
| `topologies` (or `circuits`) | Detects RC filters (with $f_c$), op-amp voltage followers, LED feedback drivers | Circuit function understanding, analog verification |
| `power` | Power rails audit (`+12V`, `-12V`, `GND`, etc.) and all connected pins | Power distribution inspection, ground connection audits |
| `nets` | Signal netlist connections with optional `--net` or `--ref` filters | Tracing specific signals or inspecting pins of a component |
| `unconnected` | Unconnected physical pins and explicit no-connect flags | Finding missed connections or unrouted pins |
| `report` (or `all`) | Full comprehensive report combining all sections | Generating a complete archival design review document |

---

## Usage Examples

### 1. Inspect Bill of Materials (BOM)
```bash
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py bom path/to/design.kicad_sch
```

### 2. Run Electrical Rules Check (ERC)
```bash
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py erc path/to/design.kicad_sch
```

### 3. Trace a Specific Net or Component Pins
```bash
# Filter signal nets connected to component U1
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py nets path/to/design.kicad_sch --ref U1

# Filter by net name (e.g. INPUT1)
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py nets path/to/design.kicad_sch --net INPUT1
```

### 4. Audit Power Rails & Decoupling
```bash
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py power path/to/design.kicad_sch
```

### 5. Check Unconnected / No-Connect Pins
```bash
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py unconnected path/to/design.kicad_sch
```

### 6. Detect Circuit Topologies & Filter Cutoffs
```bash
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py topologies path/to/design.kicad_sch
```

### 7. Generate Full Report to a File
```bash
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py report path/to/design.kicad_sch -o path/to/report.md
```
