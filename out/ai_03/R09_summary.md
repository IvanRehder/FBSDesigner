# R09 — Initiate Takeover Request (input)

**Modalities:** Touch and Keyboard

## Function
F-09.1 — Enable the pilot to issue a UAV takeover request: convert the pilot's intent into a valid, correctly-addressed takeover request directed at a target UAV and hand it to the aircraft for forwarding. Includes F-09.3 (guard against erroneous takeover requests) folded in as an embedded deliberateness gate ensuring no unintended request is transmitted.

## Behaviour
Be-09.1.1 (Touch-only): pilot touch-selects the target UAV on the takeover panel roster and taps REQUEST TAKEOVER; request commits only after a second deliberate confirm actuation. Be-09.1.2 (Keyboard-only): pilot selects the target UAV via rotary/OSS roster cycling (or UCP alphanumeric direct-ID entry) and issues REQUEST via a dedicated OSS; commit requires a second discrete confirm actuation, fully completable with zero touch input. Be-09.1.3 (Mixed): pilot selects via one modality and confirms via the other (e.g. touch-select then bezel CONFIRM OSS, or OSS-cycle then touch-confirm), satisfying modality-complete redundancy. In all three the F-09.3 gate is realized as the same dual-input press-and-confirm system reused from R03/R04/R05.

## Structure
S-09.1.3.1 — Single WAD takeover panel overlay listing teamed UAVs (tail/ID, controlling operator, status), with both input rails live simultaneously: roster row touch-select AND rotary-knob/OSS select (plus UCP alphanumeric direct-ID entry), REQUEST available as both an on-panel touch button and a bezel REQUEST OSS, and commit via the reused R03/R04/R05 dual-input CONFIRM/CANCEL control. This single structure satisfies Be-09.1.1, Be-09.1.2, and Be-09.1.3.
