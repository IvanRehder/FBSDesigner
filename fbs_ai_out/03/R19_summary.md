# R19 — Initiate Handover Request (input)

**Modalities:** Touch and Keyboard

## Function
F-19.1 — Issue a deliberate, validated handover request for a selected UAV (mirror of R09, reversed direction): let the pilot mark intent to relinquish a specific UAV and dispatch that request to the UAV Pilot, guarded against accidental triggering.

## Behaviour
Be-19.1.1 — Fully redundant Touch/Keyboard target selection followed by a reused dual-input confirm gate before request dispatch. Either modality alone completes the full task; no sub-step is modality-locked.

## Structure
S-19.1.1.1 — A WAD handover-panel overlay, sibling to the R09 takeover panel: touch-selectable UAV target control + bezel/keyboard equivalent, plus the shared dual-input press-and-confirm gate (pattern reused from R03/R04/R09/R10). Cloned as an independent panel with its own live state — selection and confirm-gate patterns reused, live state not shared with the takeover panel.
