# Buffered Mult Faceplate

This directory contains the mechanical specifications and KiCad panel files for the [Buffered Mult control board](../Buffered-Mult.kicad_pro) faceplate.

---

## Technical Specifications

### Panel Outer Dimensions
- **Format:** 3U Eurorack (6 HP width)
- **Height:** 128.50 mm (±0.20 mm tolerance)
- **Width:** 30.00 mm (incorporates standard -0.48 mm clearance against nominal 30.48 mm to prevent rail binding)
- **Thickness:** 1.60 mm (standard PCB FR4) or 2.00 mm aluminum

---

## Mechanical Clearance & Drill Specifications

### 1. Mounting Screw Slots
To allow minor horizontal alignment adjustments when mounting modules:
- **Screw Size:** M3 (3.0 mm)
- **Slot Shape:** Horizontal oval slot
- **Slot Dimensions:** 6.00 mm (width) × 3.20 mm (height)
- **Hole Center Spacing (Vertical):** 122.50 mm (3.00 mm margin from top and bottom panel edges)
- **Hole Center Spacing (Horizontal):** 7.50 mm from left and right edges (22.50 mm offset center-to-center)

### 2. Component Hole Diameters & Tolerances

| Component | Nominal Size | Recommended Drill Dia. | Clearance Margin | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **3.5mm Audio Jacks** | M6 Bushing (6.0 mm) | **6.10 mm – 6.20 mm** | +0.10 mm to +0.20 mm | Accommodates QingPu WQP-PJ398SM / Thonkiconn PJ301M threaded bushings and solder mask build-up. |
| **Indicator LEDs** | 3.0 mm THT LED | **3.20 mm** | +0.20 mm | Ensures smooth fit for 3mm flat-top LEDs or lightpipes without binding. |
| **Mounting Slots** | M3 Screws | **3.20 mm × 6.00 mm** | +0.20 mm | Standard Eurorack oval mounting slot. |

---

## Component Layout & Grid

The panel accommodates **3 identical channel groups** (Channel 1, Channel 2, Channel 3) vertically aligned.

### Per-Channel Grid Layout

| Position | Left Column | Right Column |
| :--- | :--- | :--- |
| **Top Row** | Positive LED Indicator (+) | Negative LED Indicator (-) |
| **Middle Row** | Channel Input Jack | Output Jack 1 |
| **Bottom Row** | Output Jack 2 | Output Jack 3 |

---

## KiCad Faceplate Design & Fabrication Guidelines

When designing the KiCad PCB faceplate (`faceplate.kicad_pcb`):

1. **Board Outline (Edge.Cuts):** Draw a exact 30.00 mm × 128.50 mm rectangle on `Edge.Cuts` with 0.5 mm fillet radii at the 4 outer corners.
2. **Copper & Mask Clearance:**
   - Keep copper traces and copper fills at least **0.50 mm away** from all board edges.
   - Add exposed unmasked copper rings connected to GND around mounting slots on front/back for ESD chassis grounding.
3. **Silkscreen Graphics:**
   - Use high-contrast silkscreen text (`F.Silkscreen` / `B.Silkscreen`).
   - Clearly label Channels (`CH 1`, `CH 2`, `CH 3`), Inputs (`IN`), Outputs (`1`, `2`, `3`), and LED polarities (`+`, `-`).
4. **Recommended PCB Fabrication Specs:**
   - **Material:** FR4, 1.6 mm thickness
   - **Solder Mask:** Black (Matte Black or Glossy Black)
   - **Silkscreen:** White
   - **Surface Finish:** HASL Lead-Free or ENIG (Electroless Nickel Immersion Gold)

---

## Reference Standards
* Exploding Shed [Eurorack Dimensions Guide](https://www.exploding-shed.com/synth-diy-guides/standards-of-eurorack/eurorack-dimensions/)
* Doepfer [Eurorack Mechanical Specifications](https://doepfer.de/a100_man/a100m_e.htm)
