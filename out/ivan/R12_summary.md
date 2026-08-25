# R12 — Expose UAV Status (input)

**Modalities:** Screen and Touch

## Function
F-12.1 — Pilot can call up (show) and dismiss (hide) the status panel of any connected UAV. Goal: control the visibility of the UAV information surface on demand — open it when wanted, close it back when done (show the tab/window/panel with the UAV's information).

## Behaviour
Be-12.1.1 + Be-12.1.2 (combined) — Pilot shows the UAV status panel via a persistent status control; hides it by re-pressing that same control (toggle) or via a dedicated close affordance on the panel itself. Two dismissal paths coexist. Modality-complete: Touch (tap control / tap X) or Keyboard (bezel toggle OSS / dismiss OSS); Screen renders the panel.

## Structure
S-12.1.[1+2].1 — Reused WAD UAV Detail/Status Panel (shared with R10/R11), with a persistent UAV Status tab/OSS to toggle the panel show/hide and a header close (X) control to dismiss it; panel body renders attitude/health/state. Modality-complete: Touch (tab / X) or Keyboard (bezel toggle OSS / dismiss OSS); Screen renders the panel.
