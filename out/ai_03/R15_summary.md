# R15 — Input Search Pattern (input)

**Modalities:** Touch and Keyboard

## Function
F-15.2 — Parametric pattern specification: The HMI's purpose is to let the pilot select and dimension a named pattern type (e.g. raster/ladder, spiral, sector) with its defining parameters (leg spacing, orientation, extent). Goal = pick a pattern archetype and set its numeric parameters — pattern-centric, not area-centric.

## Behaviour
Be-15.2.1 (Touch-only): Pilot taps a pattern-type tile (raster/spiral/sector) from a WAD palette; selected pattern renders a live preview overlay on the map with draggable handles — drag to set orientation, edge handles to set extent, spacing slider for leg separation; TDC cursor is the throttle-resident equivalent; numeric values shown read-only while dragging; confirm via on-screen CONFIRM. Be-15.2.2 (Keyboard-only): Pilot steps pattern-type via bezel OSS (or rotary cycle), then enters each parameter as an explicit value — leg spacing, orientation (heading °), extent (length/width or radius) — on the UCP alphanumeric keypad/rotary encoders; field focus advances by OSS; CONFIRM via bezel OSS; no pointing required. Be-15.2.3 (Mixed): Pilot taps the pattern tile and coarse-drags extent/orientation on the map for fast spatial framing, then keys exact numeric values (spacing, heading) on UCP for precision; preview updates from whichever input touched a field last; single shared validation gate before CONFIRM; optional, not required. Be-15.2.1 and Be-15.2.2 are the two mandatory modality-complete paths; Be-15.2.3 is the value-add mixed path.

## Structure
S-15.2.*.3 — Hybrid docked form + linked map preview: Combines a docked parametric PATTERN panel (cloned from R11/R01 UAV PARAMS panel family) providing the pattern-type selector row and numeric fields (spacing, heading, extent) — each field multi-input via touch keypad, bezel OSS focus-step, and UCP/rotary keying — linked live to a map preview overlay on the R14 map surface with drag handles (orientation, extent, spacing) and editable numeric readout badges. Either surface edits the same shared pattern object; whichever was last touched updates the other. Single validation gate (leg-spacing/turn-radius/area-vs-UAV-envelope) with dual-input CONFIRM (on-screen or bezel OSS). Reuses R11/R01 panel family, R14 map + confirm-gate idiom, and the shared validation-gate pattern.
