# R03 — Select Autopilot Mode (input)

**Modalities:** Touch and Keyboard

## Function
F-03.1 — Engage autopilot control authority: transfer flight control authority from manual to autopilot; the measurable effect is that the autopilot becomes the active controller.

## Behaviour
Be-03.1.3 — Mixed (either surface, redundant engage): both the WAD touch control and the bezel OSS are live simultaneously and map to the same engage action; either modality completes the full engage task independently, satisfying the modality-complete redundancy rule for Touch and Keyboard.

## Structure
S-03.1.3.1 — Dedicated AP-master widget + paired bezel OSS: a persistent 'AP' engage button on the WAD showing OFF/ARMED/ENGAGED state; one dedicated bezel OSS adjacent to it, hard-mapped to the same engage action and backlit to mirror state; both reflect engaged state via the R02 cue set (green/flashing). The OSS and AP button are shared structure with the disengage requirement (1.4) — same elements, opposite action.
