# R03 — Select Autopilot Mode (input)

**Modalities:** Touch and Keyboard

## Function
F-03.1 — Engage autopilot control authority (transfer flight control from manual to autopilot as a discrete, deliberate act); F-03.3 — Arm autopilot for safe engagement (bring autopilot to a ready/armed state guarding against inadvertent activation), treated as a coupled arm→engage flow.

## Behaviour
Be-03.1.3 — Mixed pathway: the arm→engage interaction can start on one modality and finish on another (e.g. ARM via Touch, ENGAGE via bezel OSS, or vice versa). The armed state persists across modalities (state lives in the panel, not the input channel). Each fixed modality (Touch-only, Keyboard-only) can independently complete the full task; the cross-modality flow is provided mainly as quality-of-life rather than as a hard guard.

## Structure
S-03.1.3.2 — Single AP MODE press-and-confirm control on the reused R01 multi-input panel. One dual-addressable AP MODE control (Touch tap OR bezel OSS). First actuation = ARM (persistent highlight/state cue on panel, reusing R02 notification-strip logic). Second actuation on either modality = ENGAGE. No enforced modality-switch between actuations; task completable within one surface or across both. Armed state persists across modalities between the two actuations. Shared structures: R01 panel (host surface), R02 notification-strip logic (armed-state cue).
