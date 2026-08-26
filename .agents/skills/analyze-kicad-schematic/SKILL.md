---
name: analyze-kicad-schematic
description: >-
  Analyzes KiCad schematic files (.kicad_sch) and generates structured markdown
  reports containing component catalogs, power rails audit, connectivity netlists,
  and unconnected/no-connect pin checks. Use this skill when reviewing, auditing,
  or troubleshooting KiCad schematic designs.
---

# KiCad Schematic Analyzer

This skill provides automated analysis of KiCad 7/8/9/10+ schematic (`.kicad_sch`) files using `kicad-cli`. It generates comprehensive Markdown reports summarizing design metadata, Electrical Rules Check (ERC) results, a consolidated Bill of Materials (BOM) table, detected circuit topologies & calculations (e.g. RC filters, op-amp feedback loops), power rail connections, netlists, and unconnected pins.

## Prerequisites

- **uv** (recommended) or **Python 3.6+**
- **KiCad CLI (`kicad-cli`)**: Auto-detected from system `PATH` or standard installation locations:
  - macOS: `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`, `/Applications/KiCad <version>/...`, Homebrew (`/opt/homebrew/bin/kicad-cli`).
  - Linux: `/usr/bin/kicad-cli`, `/usr/local/bin/kicad-cli`, Snap, Flatpak.
  - Windows: `C:\Program Files\KiCad\<version>\bin\kicad-cli.exe`.

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
   - Design source file, date, KiCad tool version, and hierarchical sheet structure.
2. **Electrical Rules Check (ERC)**:
   - Runs `kicad-cli sch erc` and filters out headless environment library noise while reporting true electrical violations, errors, and warnings.
3. **Bill of Materials (BOM) Summary**:
   - Compact table grouping components by value/type, footprint, LCSC/MPN part numbers, and reference ranges (e.g. `R4–R18`).
4. **Detected Circuit Topologies & Calculations**:
   - Automatically identifies functional subcircuits such as RC low-pass/high-pass filters (with calculated cutoff frequencies $f_c$) and op-amp stage configurations (voltage followers, active LED drivers, feedback loops).
5. **Power Rails Audit**:
   - Identifies power nets (`+12V`, `-12V`, `GND`, `VCC`, `VDD`, etc.) and all component pins attached to each rail.
6. **Signal Netlist**:
   - Complete signal netlist mapping all interconnected pins with pin functions and pin types.
7. **Unconnected & No-Connect Pins**:
   - Flags physical component pins that are missing from nets or explicitly marked as no-connect.

