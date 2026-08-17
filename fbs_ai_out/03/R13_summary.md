# R13 — Communicate UAV Status (output)

**Modalities:** Screen and Audio-out

## Function
F-13.2 — Signal UAV status changes/transitions (event-driven notification): draw pilot attention on a UAV status delta (mode transition, link degrade/restore, health change, tracking lock acquired/lost), output-only via Screen and Audio-out. Complements R12 (values-on-demand) by signalling when the state changed.

## Behaviour
Be-13.2.3 — Mixed synchronized cue: on a UAV status delta, both channels fire together, criticality-graded (low-severity = silent visual marker; high-severity = audio earcon/TTS + persistent visual on WAD/HUD). Redundancy-complete: the pilot catches the event via either modality; audio draws attention off-visual-axis, visual marker carries detail and persists after the sound stops.

## Structure
S-13.2.3.3 — Hybrid delivery: a single change-detector on the R12 UAV status store drives both surfaces. High-tier deltas -> R08 tiered notification strip entry (WAD+HUD) + R08 audio (earcon/TTS, attention/acknowledgment) AND R12 pane changed-field highlight (detail-in-context); low-tier deltas -> R12 pane changed-field highlight only, silent, no strip. Audio owned solely by R08 (no competing tone sets). New logical component introduced: the change-detector on the R12 status store; everything else reuses R08 and R12.
