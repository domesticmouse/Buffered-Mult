# KiCad Schematic Design Report: Buffered-Mult.kicad_sch

- **Date:** 2026-07-31T11:27:42
- **KiCad Tool Version:** Eeschema 10.0.4
- **Design Source:** Buffered-Mult.kicad_sch

## Component Catalog

- **C1**
  - **Value:** `100nF`
  - **Library Part:** `Device:C`
  - **Description:** Unpolarized capacitor
- **C2**
  - **Value:** `100nF`
  - **Library Part:** `Device:C`
  - **Description:** Unpolarized capacitor
- **C3**
  - **Value:** `100nF`
  - **Library Part:** `Device:C`
  - **Description:** Unpolarized capacitor
- **C4**
  - **Value:** `100nF`
  - **Library Part:** `Device:C`
  - **Description:** Unpolarized capacitor
- **C5**
  - **Value:** `100nF`
  - **Library Part:** `Device:C`
  - **Description:** Unpolarized capacitor
- **C6**
  - **Value:** `100nF`
  - **Library Part:** `Device:C`
  - **Description:** Unpolarized capacitor
- **D1**
  - **Value:** `LED`
  - **Library Part:** `Device:LED`
  - **Description:** Light emitting diode
- **D2**
  - **Value:** `LED`
  - **Library Part:** `Device:LED`
  - **Description:** Light emitting diode
- **D3**
  - **Value:** `LED`
  - **Library Part:** `Device:LED`
  - **Description:** Light emitting diode
- **D4**
  - **Value:** `LED`
  - **Library Part:** `Device:LED`
  - **Description:** Light emitting diode
- **D5**
  - **Value:** `LED`
  - **Library Part:** `Device:LED`
  - **Description:** Light emitting diode
- **D6**
  - **Value:** `LED`
  - **Library Part:** `Device:LED`
  - **Description:** Light emitting diode
- **J1**
  - **Value:** `Eurorack PWR`
  - **Library Part:** `Connector_Generic:Conn_02x05_Odd_Even`
  - **Description:** Generic connector, double row, 02x05, odd/even pin numbering scheme (row 1 odd numbers, row 2 even numbers), script generated (kicad-library-utils/schlib/autogen/connector/)
- **J2**
  - **Value:** `INPUT1`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J3**
  - **Value:** `INPUT2`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J4**
  - **Value:** `INPUT3`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J5**
  - **Value:** `OUTPUT1-1`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J6**
  - **Value:** `OUTPUT1-2`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J7**
  - **Value:** `OUTPUT1-3`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J8**
  - **Value:** `OUTPUT2-1`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J9**
  - **Value:** `OUTPUT2-2`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J10**
  - **Value:** `OUTPUT2-3`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J11**
  - **Value:** `OUTPUT3-1`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J12**
  - **Value:** `OUTPUT3-2`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **J13**
  - **Value:** `OUTPUT3-3`
  - **Library Part:** `Connector_Audio:AudioJack2_SwitchT`
  - **Description:** Audio Jack, 2 Poles (Mono / TS), Switched T Pole (Normalling)
- **R1**
  - **Value:** `100K`
  - **Library Part:** `Device:R`
  - **Description:** Resistor
- **R2**
  - **Value:** `100K`
  - **Library Part:** `Device:R`
  - **Description:** Resistor
- **R3**
  - **Value:** `100K`
  - **Library Part:** `Device:R`
  - **Description:** Resistor
- **U1**
  - **Value:** `TL074`
  - **Library Part:** `Amplifier_Operational:TL074`
  - **Description:** Quad Low-Noise JFET-Input Operational Amplifiers, DIP-14/SOIC-14
  - **Datasheet:** [http://www.ti.com/lit/ds/symlink/tl071.pdf](http://www.ti.com/lit/ds/symlink/tl071.pdf)
- **U2**
  - **Value:** `TL074`
  - **Library Part:** `Amplifier_Operational:TL074`
  - **Description:** Quad Low-Noise JFET-Input Operational Amplifiers, DIP-14/SOIC-14
  - **Datasheet:** [http://www.ti.com/lit/ds/symlink/tl071.pdf](http://www.ti.com/lit/ds/symlink/tl071.pdf)
- **U3**
  - **Value:** `TL074`
  - **Library Part:** `Amplifier_Operational:TL074`
  - **Description:** Quad Low-Noise JFET-Input Operational Amplifiers, DIP-14/SOIC-14
  - **Datasheet:** [http://www.ti.com/lit/ds/symlink/tl071.pdf](http://www.ti.com/lit/ds/symlink/tl071.pdf)

## Power Rails Audit

### Net: +12V
- **C1** - Pin 1 / passive
- **C3** - Pin 1 / passive
- **C5** - Pin 1 / passive
- **J1** - Pin 10 (Pin_10_10) / passive
- **J1** - Pin 9 (Pin_9_9) / passive
- **U1** - Pin 4 (V+_4) / power_in
- **U2** - Pin 4 (V+_4) / power_in
- **U3** - Pin 4 (V+_4) / power_in

### Net: -12V
- **C2** - Pin 2 / passive
- **C4** - Pin 2 / passive
- **C6** - Pin 2 / passive
- **J1** - Pin 1 (Pin_1_1) / passive
- **J1** - Pin 2 (Pin_2_2) / passive
- **U1** - Pin 11 (V-_11) / power_in
- **U2** - Pin 11 (V-_11) / power_in
- **U3** - Pin 11 (V-_11) / power_in

### Net: GND
- **C1** - Pin 2 / passive
- **C2** - Pin 1 / passive
- **C3** - Pin 2 / passive
- **C4** - Pin 1 / passive
- **C5** - Pin 2 / passive
- **C6** - Pin 1 / passive
- **J1** - Pin 3 (Pin_3_3) / passive
- **J1** - Pin 4 (Pin_4_4) / passive
- **J1** - Pin 5 (Pin_5_5) / passive
- **J1** - Pin 6 (Pin_6_6) / passive
- **J1** - Pin 7 (Pin_7_7) / passive
- **J1** - Pin 8 (Pin_8_8) / passive
- **J2** - Pin S / passive
- **J2** - Pin TN / passive
- **J3** - Pin S / passive
- **J4** - Pin S / passive
- **J5** - Pin S / passive
- **J6** - Pin S / passive
- **J7** - Pin S / passive
- **J8** - Pin S / passive
- **J9** - Pin S / passive
- **J10** - Pin S / passive
- **J11** - Pin S / passive
- **J12** - Pin S / passive
- **J13** - Pin S / passive
- **R1** - Pin 2 / passive
- **R2** - Pin 2 / passive
- **R3** - Pin 2 / passive

## Connectivity Netlist

### Net: INPUT1
- **J2** - Pin T / passive
- **J3** - Pin TN / passive
- **R1** - Pin 1 / passive
- **U1** - Pin 10 (+_10) / input
- **U1** - Pin 12 (+_12) / input
- **U1** - Pin 3 (+_3) / input
- **U1** - Pin 5 (+_5) / input

### Net: INPUT2
- **J3** - Pin T / passive
- **J4** - Pin TN / passive
- **R2** - Pin 1 / passive
- **U2** - Pin 10 (+_10) / input
- **U2** - Pin 12 (+_12) / input
- **U2** - Pin 3 (+_3) / input
- **U2** - Pin 5 (+_5) / input

### Net: INPUT3
- **J4** - Pin T / passive
- **R3** - Pin 1 / passive
- **U3** - Pin 10 (+_10) / input
- **U3** - Pin 12 (+_12) / input
- **U3** - Pin 3 (+_3) / input
- **U3** - Pin 5 (+_5) / input

### Net: Net-(D1-A)
- **D1** - Pin 2 (A_2) / passive
- **D2** - Pin 1 (K_1) / passive
- **U1** - Pin 13 (-_13) / input

### Net: Net-(D1-K)
- **D1** - Pin 1 (K_1) / passive
- **D2** - Pin 2 (A_2) / passive
- **U1** - Pin 14 / output

### Net: Net-(D3-A)
- **D3** - Pin 2 (A_2) / passive
- **D4** - Pin 1 (K_1) / passive
- **U2** - Pin 13 (-_13) / input

### Net: Net-(D3-K)
- **D3** - Pin 1 (K_1) / passive
- **D4** - Pin 2 (A_2) / passive
- **U2** - Pin 14 / output

### Net: Net-(D5-A)
- **D5** - Pin 2 (A_2) / passive
- **D6** - Pin 1 (K_1) / passive
- **U3** - Pin 13 (-_13) / input

### Net: Net-(D5-K)
- **D5** - Pin 1 (K_1) / passive
- **D6** - Pin 2 (A_2) / passive
- **U3** - Pin 14 / output

### Net: OUTPUT1-1
- **J5** - Pin T / passive
- **U1** - Pin 1 / output
- **U1** - Pin 2 (-_2) / input

### Net: OUTPUT1-2
- **J6** - Pin T / passive
- **U1** - Pin 6 (-_6) / input
- **U1** - Pin 7 / output

### Net: OUTPUT1-3
- **J7** - Pin T / passive
- **U1** - Pin 8 / output
- **U1** - Pin 9 (-_9) / input

### Net: OUTPUT2-1
- **J8** - Pin T / passive
- **U2** - Pin 1 / output
- **U2** - Pin 2 (-_2) / input

### Net: OUTPUT2-2
- **J9** - Pin T / passive
- **U2** - Pin 6 (-_6) / input
- **U2** - Pin 7 / output

### Net: OUTPUT2-3
- **J10** - Pin T / passive
- **U2** - Pin 8 / output
- **U2** - Pin 9 (-_9) / input

### Net: OUTPUT3-1
- **J11** - Pin T / passive
- **U3** - Pin 1 / output
- **U3** - Pin 2 (-_2) / input

### Net: OUTPUT3-2
- **J12** - Pin T / passive
- **U3** - Pin 6 (-_6) / input
- **U3** - Pin 7 / output

### Net: OUTPUT3-3
- **J13** - Pin T / passive
- **U3** - Pin 8 / output
- **U3** - Pin 9 (-_9) / input

## Unconnected & No-Connect Pins

- **J5** - Pin TN [Explicit No-Connect] (passive+no_connect)
- **J6** - Pin TN [Explicit No-Connect] (passive+no_connect)
- **J7** - Pin TN [Explicit No-Connect] (passive+no_connect)
- **J8** - Pin TN [Explicit No-Connect] (passive+no_connect)
- **J9** - Pin TN [Explicit No-Connect] (passive+no_connect)
- **J10** - Pin TN [Explicit No-Connect] (passive+no_connect)
- **J11** - Pin TN [Explicit No-Connect] (passive+no_connect)
- **J12** - Pin TN [Explicit No-Connect] (passive+no_connect)
- **J13** - Pin TN [Explicit No-Connect] (passive+no_connect)
