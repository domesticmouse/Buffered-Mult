# Buffered-Mult

A buffered mult (multiple) circuit designed for Eurorack modular synthesizers.

## Purpose

In modular synthesis, a **multiple** is used to split a single signal (such as control voltage, gates/triggers, or audio) and route it to multiple destinations simultaneously.

While passive multiples simply wire jacks together in parallel, they cause **voltage droop** when splitting precise voltages like 1V/Octave pitch CV across multiple inputs due to impedance loading. This results in out-of-tune oscillators and pitch tracking errors.

This **buffered mult circuit** solves that problem by using active operational amplifiers configured as unity-gain buffers:

- **1:1 Voltage Precision:** Maintains accurate voltage levels (essential for 1V/Oct pitch CV) across all outputs without signal drop.
- **Impedance Isolation:** High input impedance presents virtually no load to the source signal, while low output impedance cleanly drives downstream module inputs.
- **Channel Isolation:** Prevents attached modules from loading or interfering with each other.

### Dimensions
Height: 3U  
Width: 4HP

### Inputs
Three 3.5mm mono input jacks. 
Second input is normalled to the first input.
Third input is normalled to the second input.
100k pulldown resistors on the inputs to prevent floating.

### Outputs
Three 3.5mm mono output jacks connected to each input.
A pair of LEDs to indicate signal + and - voltages.

### Circuit design

- TL074 Operational amplifiers configured as unity-gain buffers
- Opposing polarity LEDs to indicate + and - signal
- 2x5 pin IDC connector for +-12V power supply
- Power supply decoupling capacitors 
- Inverted power protection via schottky diodes
