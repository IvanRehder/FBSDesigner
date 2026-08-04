# R04 — Stop Using Autopilot (input)

**Modalities:** Touch and Keyboard

## Function
F-04.1 — Autopilot Disengagement (control transfer to manual): The HMI's purpose is to hand flight authority back from autopilot to the pilot; after invocation, the aircraft is under manual control. This is the direct teleology of use case 1.4 — the artefact exists to release automation.

## Behaviour
Be-04.1.2 — Keyboard-only pathway: Pilot presses a dedicated bezel OSS (or UCP key) mapped to AP disengage. Discrete physical actuation, no display targeting required — suited when hands/eyes are loaded and the pilot wants a tactile, glance-free release. Full task completable by keyboard alone.

## Structure
S-04.1.2.3 — Bezel rotary detent (mode selector): A rotary switch on the WAD bezel with MANUAL / AP positions; turning to MANUAL sends the manual-control command and disengages the autopilot, with mode indicated by knob position (self-evident state). Reconcile with R03 into a single shared AP mode control.
