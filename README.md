# Buffered-Mult

A 3-channel active buffered mult (multiple) circuit designed for Eurorack modular synthesizers. View this in [KiCanvas](https://kicanvas.org/?repo=https%3A%2F%2Fgithub.com%2Fdomesticmouse%2FBuffered-Mult).

## Purpose

In modular synthesis, a **multiple** is used to split a single signal (such as control voltage, gates/triggers, or audio) and route it to multiple destinations simultaneously.

While passive multiples simply wire jacks together in parallel, they cause **voltage droop** when splitting precise voltages like 1V/Octave pitch CV across multiple inputs due to impedance loading. This results in out-of-tune oscillators and pitch tracking errors.

This **buffered mult circuit** solves that problem by using active operational amplifiers configured as unity-gain buffers:

- **1:1 Voltage Precision:** Maintains accurate voltage levels (essential for 1V/Oct pitch CV) across all outputs without signal drop.
- **Impedance Isolation:** High input impedance presents virtually no load to the source signal, while low output impedance cleanly drives downstream module inputs.
- **Channel Isolation:** Prevents attached modules from loading or interfering with each other.

---

## Specifications

### Dimensions
- **Height:** 3U (Eurorack format)
- **Width:** 6HP
- **Faceplate:** Complete mechanical specifications and KiCad panel design are available in [`faceplate/README.md`](faceplate/README.md).

See Exploding Shed's [Eurorack Dimensions Guide](https://www.exploding-shed.com/synth-diy-guides/standards-of-eurorack/eurorack-dimensions/) for sizing a 6hp module.

### Inputs
- **3× 3.5 mm mono input jacks:**
  - Input 2 is normalled to Input 1.
  - Input 3 is normalled to Input 2.
- **Cascading Normalling Routing:**
  - **1 Input patched (Input 1):** Functions as a **1×9** mult (1 input split to 9 outputs).
  - **2 Inputs patched (Inputs 1 & 2):** Functions as **1×3** (Input 1) and **1×6** (Input 2) mults.
  - **3 Inputs patched (Inputs 1, 2 & 3):** Functions as **3 independent 1×3** mults.
- **100 kΩ pulldown resistors** (`R1`–`R3`) on inputs to prevent floating inputs when unpatched.
- **Input ESD & RF Filtering:** 1 kΩ series resistors (`R16`–`R18`) and 100 pF capacitors (`C9`–`C11`) provide high-frequency noise filtering and ESD protection.

### Outputs
- **9× 3.5 mm mono output jacks:** 3 dedicated buffered outputs for each of the 3 input channels.
- **1 kΩ Short-Circuit Protection:** Output series resistors (`R7`–`R15`) protect op-amps during cable insertion/patching shorts while maintaining stability under capacitive cable loads.
- **Bipolar LED Indication:** Opposing-polarity LED pairs (`D1`–`D6`) driven by dedicated active op-amp constant-current stages (`R4`–`R6`) indicate positive (+) and negative (-) voltage states without loading signal lines.

---

## Circuit & Physical Design

- **TL074 Quad Operational Amplifiers:** Configured as high-impedance unity-gain buffers (`U1`, `U2`, `U3`).
- **Active Visual Feedback:** 4th op-amp stage on each TL074 drives bipolar indicator LEDs in a constant-current feedback arrangement.
- **Power Connector:** Standard 2×5-pin IDC header (`J1`) for Eurorack ±12V power connection.
- **Power Filtering & Decoupling:** Bulk 10 µF electrolytic capacitors (`C7`, `C8`) on power entry rails plus 100 nF ceramic decoupling capacitors (`C1`–`C6`) per IC package.
- **Reverse Power Protection:** MBR0520 Schottky diodes (`D7`, `D8`) protect against reverse ribbon cable insertion.
- **Two-Sided Board Layout:** All SMT components on top layer (`F.Cu`); through-hole jacks and LEDs on bottom layer (`B.Cu`) for front panel mounting.

---

## Verification & Fabrication

- **KiCad Electrical Rules Check (ERC):** 0 Errors, 0 Warnings on main board schematic.
- **KiCad Design Rules Check (DRC):** 0 Track / Clearance Errors on main board and faceplate PCB.
- **JLCPCB Automated Assembly Ready:** Complete Gerber ZIP, SMT BOM (`BOM-Buffered-Mult.csv`), and Centroid CPL (`CPL-Buffered-Mult.csv`) generated in [`jlcpcb/production_files/`](jlcpcb/production_files/).
- **Faceplate Fabrication:** Complete KiCad project, panel Gerber files, and drill specs in [`faceplate/`](faceplate/).

## License

BufferedMult is open source and available under the [Apache License 2.0](LICENSE).

## Disclaimer

This is not an official Google product.
