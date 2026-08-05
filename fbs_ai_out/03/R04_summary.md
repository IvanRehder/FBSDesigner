# R04 — Stop Using Autopilot (input)

**Modalities:** Touch and Keyboard

## Function
F-04.1 — Relinquish automation authority to the pilot. Disengage the autopilot and return manual control on a deliberate command; error-resistance and post-disengagement state awareness fold in as Behaviour traits.

## Behaviour
Be-04.1.3 — Mixed dual-input (Touch/bezel) press-and-confirm disengage: pilot may initiate on one modality (Touch tap on AP MODE control, or bezel OSS press) and confirm on either; disengaged/manual state persists across both modalities; result of disengagement confirmed via the reused R02 alert channel.

## Structure
S-04.1.3.1 — Reused R03 AP MODE control on the R01-reused multi-input panel (WAD): same touch target + mapped bezel OSS, now toggling engaged→disengaged via press-and-confirm; disengaged/manual state rendered on the panel (Screen) and persisting across modalities; result feedback via reused R02 channel (notification strip + panel cue + audio ping). Only deltas from R03 are label/state text and confirm prompt wording.
