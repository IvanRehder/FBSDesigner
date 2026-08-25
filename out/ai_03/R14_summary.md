# R14 — Input Sensor Move (input)

**Modalities:** Wearable/HMD and Touch

## Function
F-14 — Designate a sensor aim-point. Convert a pilot-chosen POI/AOI (via head/gaze or touch) into a sensor slew-and-hold command. Measured by designation accuracy and slew-to-target success. Continuous manual steering (former F-14.2) deferred out-of-scope for this modality pair.

## Behaviour
Be-14.1 (Touch-only): Pilot taps the POI or drags a box for an AOI directly on the WAD Map; a designation marker drops, pilot confirms, system issues slew — full task completable on Touch alone. Be-14.2 (HMD): Pilot's HMD head-slaved/eye-refined reticle sits on the target in the visor overlay; commit issues the slew and in-visor ack (HMD-assisted, not HMD-alone-complete — accepted deviation). Be-14.3 (Mixed): HMD head/gaze provides coarse cue, Touch on WAD refines the exact point and commits, exploiting both fixed modalities for accuracy-under-time.

## Structure
S-14.1.1 (Be-14.1, Touch) — Map-embedded designation: WAD Map tap-to-drop POI / drag-box AOI, SENSOR AIM designation overlay layer, Touch/bezel CONFIRM SLEW gate (R09/R10 confirm pattern), in-pane slew-progress + ack indicator (R12 pattern); independently sufficient, carries requirement-level modality completeness. S-14.2.2 (Be-14.2, HMD) — In-visor head-slaved reticle with eye-tracked fine offset + in-visor slew/ack cue; commit via bezel OSS or single WAD tap; HMD-assisted, not HMD-alone-complete (accepted deviation). Be-14.3 Mixed realized by combination of the two structures above (reticle coarse-cue seeds Map marker, touch refines and commits) — no dedicated structure.
