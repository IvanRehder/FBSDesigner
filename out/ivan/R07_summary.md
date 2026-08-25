# R07 — Report Surveillance Event (input)

**Modalities:** Touch and Keyboard

## Function
F-07.2 — Pilot reports a surveillance event with its classification to C2. The artefact exists so that C2 receives a typed/qualified event report as it happens; measurable effect: a classified event report is transmitted and acknowledged. The commit is the delivery mechanism; the classification gives the report its operational meaning.

## Behaviour
Be-07.2.1 — Classify-then-commit, map-anchored (R05 pattern extended). Press-and-hold on Map at the observed location → option ring appears → select event-type marker from ring → report auto-populates with type + location → commit/send. Keyboard path: bezel OSS to open report, UCP/rotary to step through event types, OSS to commit. Modality-complete: Touch (hold+tap) and Keyboard (bezel rotary + OSS) paths both complete the full task.

## Structure
S-07.2.1.1 — Map view (WAD), shared/reused from R05/R06. S-07.2.1.2 — Option ring (radial menu overlay at selected point), shared widget reused from R05. S-07.2.1.3 — Preset marker buttons, shared widget with surveillance event taxonomy as R07-specific content. S-07.2.1.4 — Marker glyph layer (committed event markers on map), shared layer reused from R05. S-07.2.1.5 — Input bindings: Touch (hold+tap) / Keyboard (bezel rotary + OSS), shared binding pattern reused from R05, both modality-complete. Note: entirely shared with R05/R06 except surveillance event taxonomy content; no new hardware or widgets.
