---
name: analyze-kicad-schematic
description: >-
  Analyzes KiCad schematic files (.kicad_sch) and generates structured markdown
  reports containing component catalogs, power rails audit, connectivity netlists,
  and unconnected/no-connect pin checks. Use this skill when reviewing, auditing,
  or troubleshooting KiCad schematic designs.
---

# KiCad Schematic Analyzer

This skill provides automated analysis of KiCad 7/8+ schematic (`.kicad_sch`) files using `kicad-cli`. It generates comprehensive Markdown reports summarizing design metadata, component catalogs (with footprints, datasheets, MPNs, and LCSC part numbers), power rail connections, netlists, and unconnected pins.

## Prerequisites

- **uv** (recommended) or **Python 3.6+**
- **KiCad CLI (`kicad-cli`)**: Must be installed and available in `PATH`.
  - macOS: Usually located in `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` or installed via Homebrew / symlinked to `/usr/local/bin/kicad-cli`.
  - Linux: Included with KiCad packages (`kicad`).
  - Windows: Located in `C:\Program Files\KiCad\<version>\bin\kicad-cli.exe`.

## Tool Script

The analysis script is located at:
- [`scripts/analyze_schematic.py`](./scripts/analyze_schematic.py)

## Usage

### 1. Run Analysis and Output to stdout

```bash
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py path/to/design.kicad_sch
```

*Or using standard Python 3:*
```bash
python3 .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py path/to/design.kicad_sch
```

### 2. Save Analysis directly to a Markdown File

```bash
uv run --isolated .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py path/to/design.kicad_sch -o path/to/report.md
```

*Or using standard Python 3:*
```bash
python3 .agents/skills/analyze-kicad-schematic/scripts/analyze_schematic.py path/to/design.kicad_sch -o path/to/report.md
```

## Report Sections & Review Guide

The generated report contains the following sections:

1. **Metadata Summary**:
   - Design source file, date, and KiCad tool version used to generate the netlist.
2. **Component Catalog**:
   - Lists each component reference designator (e.g. `R1`, `C1`, `U1`), value, library symbol, footprint, description, datasheet link, MPN, and manufacturer/LCSC part numbers.
   - Use this to verify Bill of Materials (BOM) completeness, footprint assignments, and component ratings.
3. **Power Rails Audit**:
   - Identifies power nets (`+12V`, `-12V`, `GND`, `VCC`, `VDD`, etc.) and all component pins attached to each rail.
   - Use this to verify decoupling capacitors, power pin connections, reverse-polarity protection, and ensure no IC power pins are omitted.
4. **Connectivity Netlist**:
   - Complete signal netlist mapping all interconnected pins with pin functions and pin types.
   - Use this to trace signal paths, verify input/output protection resistors, feedback loops, and bus connections.
5. **Unconnected & No-Connect Pins**:
   - Flags physical component pins that are missing from nets or explicitly marked as no-connect.
   - Use this to catch floating pins, unconnected op-amp stages, or missing terminations.

## Limitations

- **Single-Sheet Designs**: The script currently validates single-sheet schematics. If a multi-sheet hierarchical schematic is detected, the script will output an error and exit.
