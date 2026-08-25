# R04 — Stop Using Autopilot (input)

**Modalities:** Touch and Keyboard

## Function
- **F-04.1** — To terminate an active autopilot mode.
- **F-04.2** — To enable pilot selection of manual flight control.

(Both kept as distinct once given different Behaviours — otherwise F-04.2 collapses into F-04.1, same interaction possibilities.)

## Behaviour
- **Be-04.1** — Deactivate-by-re-press → realizes F-04.1. Re-press the active mode control to deselect.
- **Be-04.2** — One-shot disengage → realizes F-04.2. Single action on a dedicated MANUAL affordance.

Both modality-complete redundant. Design tension: re-press path reintroduces a deselection-ambiguity concern raised earlier against non-dedicated controls; accepted as secondary, MANUAL affordance is the robust primary.

## Structure
- **S-04.1** — Autopilot mode panel (WAD), shared w/ R03, active-mode re-tap-to-deselect. Touch / Be-04.1.
- **S-04.2** — Bezel mode buttons (OSS), shared w/ R03, re-press-to-deselect + dedicated MANUAL button. Keyboard / both Behaviours.
- **S-04.3** — Dedicated MANUAL touch button (WAD). Touch / Be-04.2.

All reused/extended from R03, no new hardware.
