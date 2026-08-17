# R18 — Set Tracking Distance from TOI (input)

**Modalities:** Touch and Keyboard

## Function
F-18.1 — Specify a numeric standoff distance to the tracked TOI: the pilot inputs a discrete distance value that becomes the UAV's commanded range from the target; the panel surfaces the current commanded/actual range as context so that absolute entry also serves as an informed relative adjustment (no separate increment function — the displayed current value enables easy trimming).

## Behaviour
Be-18.1.1 (Keyboard-only): current range shown as a live readout; pilot enters a new distance via UCP alphanumeric keypad or steps the value up/down from the displayed current using the bezel rotary; envelope validation (min/max standoff) gates a CONFIRM before the command is sent. Be-18.1.2 (Touch-only): current range shown as a live readout; pilot taps a distance field to raise an on-screen numeric keypad, or uses touch +/− stepper buttons anchored to the current value, then taps CONFIRM. Be-18.1.3 (Mixed): interleaved input — touch to select the field, keyboard/rotary to enter or step the value, either modality to CONFIRM, allowing the pilot to start on one modality and commit on another mid-task. All three share one envelope-validation gate and one confirm semantics; rotary/stepper step-from-current provides effortless trim without a separate function.

## Structure
S-18.1.*.1 — DISTANCE row embedded in the R17 unified TOI panel (same panel holding designation + contact list for the tracked target). Elements: current-range live readout showing commanded + actual value; editable distance field (touch-tap raises on-screen numeric keypad; UCP keypad / bezel rotary to type or step; interleaved Mixed input); touch +/− steppers and rotary bound to step-from-current; shared envelope-validation gate. Constraint: the DISTANCE row is independently editable and committable while a track is active — an R18 distance-only CONFIRM issues a standalone distance-update command (UC 7.2.2–7.2.4) against the already-tracked TOI and does NOT re-trigger R17's track-command gate or re-designate the TOI. Two separate commit paths on the shared panel: R17 CONFIRM (track/designation) and R18 distance CONFIRM (distance-only update). Distance field stays live and re-editable for the duration of the track; current-range readout updates continuously.
