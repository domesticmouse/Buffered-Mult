Here is a detailed engineering review of the [Buffered-Mult.kicad_sch](Buffered-Mult.kicad_sch) schematic, highlighting design mistakes, missing components, and recommended fixes for a reliable Eurorack module.

---

### 🚨 Critical Design Mistakes (Must Fix)

#### 1. Missing Output Protection Resistors
* **Issue:** All 9 op-amp outputs (`OUTPUT1-1` through `OUTPUT3-3`) are connected directly to the output jack tip pins without any series resistors.
* **Why it's a problem:** In modular synth patch bays, patch cables are frequently plugged/unplugged, momentarily shorting output tips to ground or plugging outputs directly into other powered outputs. Connecting a TL074 output directly to ground or another output will draw excessive short-circuit current, cause signal distortion across other channels on the IC, and potentially destroy the op-amp.
* **Fix:** Add a **1 kΩ (or 470 Ω)** resistor in series between every op-amp output pin and its corresponding output jack tip (9 resistors total: `R4`–`R12`). 1 kΩ limits short-circuit current to safe levels while presenting negligible voltage drop to standard module input impedances (100 kΩ).

#### 2. Missing Current-Limiting Resistors for LEDs
* **Issue:** LEDs `D1` through `D6` are placed across the output signals without series current-limiting resistors.
* **Why it's a problem:** Standard LEDs have a forward voltage ($V_F$) of ~1.8V to 3.2V. Wiring an LED directly to an op-amp output node without a resistor will:
  1. Draw excessive current (>50–100 mA), overloading the op-amp output.
  2. Heavy-clip / clamp the control voltage to the LED's forward voltage (ruining 1V/Oct pitch CV and audio signals!).
  3. Burn out the LEDs.
* **Fix:** Place a **1 kΩ to 2.2 kΩ** resistor in series with each LED indicator pair.

#### 3. Missing Reverse-Polarity Power Protection
* **Issue:** Power header `J1` connects directly to the `+12V` and `-12V` power rails. There are no Schottky diodes on the power entry lines (despite being mentioned in the `README.md`).
* **Why it's a problem:** If a user accidentally plugs the Eurorack 10-pin power ribbon cable upside-down, `-12V` will be applied to the `+12V` pins and vice versa. Without protection, all ICs (`U1`, `U2`, `U3`) will instantly burn out.
* **Fix:** Add two **Schottky diodes** (e.g., `1N5817` or `MBR0520`) in series with the `+12V` and `-12V` input pins of `J1` (or parallel clamp diodes with PTC resettable fuses).

---

### ⚠️ Missing Components & Schematic Improvements

#### 4. Missing Bulk Power Supply Electrolytic Capacitors
* **Issue:** The schematic only contains six 100 nF ceramic capacitors (`C1`–`C6`) placed near the ICs.
* **Why it's needed:** 100 nF caps filter high-frequency digital/RF noise, but they cannot supply instantaneous current spikes or smooth out low-frequency power supply ripple from the Eurorack bus.
* **Fix:** Add **two 10 µF to 47 µF electrolytic capacitors** (25V minimum rating) at the power entry point `J1`:
  * One between `+12V` and `GND`.
  * One between `-12V` and `GND`.

#### 5. Unused Op-Amp Channel Termination
* **Issue:** 3 TL074 quad op-amps (`U1`, `U2`, `U3`) provide 12 total op-amp channels. Since the 3-channel mult only requires 9 outputs, **3 op-amp channels are unused**.
* **Why it's needed:** Leaving unused op-amp input pins floating in CMOS/JFET ICs causes them to pick up stray noise, oscillate at high frequencies, and draw excessive supply current.
* **Fix:** 
  * Connect the non-inverting input (`+`) of each unused op-amp channel to `GND`.
  * Wire the output pin directly to the inverting input (`-`) to configure them as grounded unity-gain buffers.
  * *(Alternative)* Replace one TL074 (Quad) with a **TL072 (Dual)** op-amp, reducing total IC count to 2× TL074 + 1× TL072 (10 channels total, 1 unused), saving PCB real estate and power.

#### 6. Optional: Input Protection & ESD Filtering
* **Recommendation:** Add a **1 kΩ series resistor** and a **100 pF ceramic capacitor** to GND at each input jack (`J2`, `J3`, `J4`) before the 100k pulldown resistors. This creates a low-pass RF noise filter and protects the TL074 JFET inputs from static ESD spikes when patch cables are inserted.

---

### 📋 Recommended Component Additions Summary

| Component | Quantity | Value / Part | Purpose |
| :--- | :--- | :--- | :--- |
| **Output Resistors** | 9 | 1 kΩ (0805 or axial) | Op-amp output short-circuit protection |
| **LED Series Resistors** | 3–6 | 1 kΩ – 2.2 kΩ | Current limiting & signal clamping prevention |
| **Reverse Power Diodes**| 2 | 1N5817 / MBR0520 | Reverse polarity power supply protection |
| **Bulk Electrolytic Caps**| 2 | 10 µF – 47 µF (25V) | Low-frequency power rail decoupling |
| **Input ESD/RF Resistors**| 3 | 1 kΩ | ESD protection on input jacks |

---

### Summary of Work
- Performed an engineering audit of [Buffered-Mult.kicad_sch](Buffered-Mult.kicad_sch).
- Identified critical missing protection components (output resistors, LED current limiters, reverse power diodes).
- Documented power rail decoupling requirements and proper termination for unused TL074 op-amp channels.
