# R11 — Input New UAV Parameters (input)

**Modalities:** Touch and Keyboard

## Function
F-11.1 — Pilot submits new UAV flight parameters: the pilot's intended parameter values (speed, altitude, heading) become the UAV's commanded targets. F-11.2 — Pilot is made aware the UAV accepted the new parameters: closure on the round-trip acknowledgment.

## Behaviour
F-11.1 → Be-11.1.1 Direct value entry (primary): pilot opens the UAV parameter panel, enters speed/altitude/heading values directly via numeric keypad (Touch) or UCP/bezel alphanumeric (Keyboard), commits; modality-complete on each path. Be-11.1.2 Step/increment adjustment (complement): pilot nudges each parameter up/down via on-screen steppers (Touch) or bezel rotary (Keyboard). Be-11.1.3 Preset parameter profiles: pilot selects a stored profile (e.g. loiter, transit) that populates all three values at once, then commits. F-11.2 → Be-11.2.1 Redundant ack notification (R08 reuse): on UAV acknowledgment, fire the shared R08 audio tone plus visual notification; modality-complete on output.

## Structure
S-11.1.1.1 — UAV Parameter Panel (WAD, R01 Setpoint-Panel component family re-instantiated with UAV param semantics): three parameter rows (speed / altitude / heading), each with numeric field + keypad (Touch, Be-11.1.1) and ± steppers (Touch, Be-11.1.2), plus a preset selector row (Touch, Be-11.1.3); bezel rotary maps to selected-row stepping and UCP alphanumeric to direct value entry (Keyboard path, all three behaviours); Commit/Send affordance via Touch OSS and bezel OSS; both paths modality-complete. S-11.2.1.1 — Ack via shared R08 notification stack: audio tone (shared Audio notify channel) + reusable multi-mode pop-up + notification-marker + messages-tab entry; parameter-accepted event routed into existing R08 components, no new structure.
