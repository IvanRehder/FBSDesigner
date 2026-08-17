# R12 — Expose UAV Status (input)

**Modalities:** Screen and Touch

## Function
F-12.1 — On-demand-invoked, continuously-updating UAV status exposure. The HMI is FOR letting the pilot invoke (pull) a UAV status surface on demand, which once open remains live — continuously reflecting the UAV's current state until dismissed. It combines the discrete request act with sustained awareness while active: expose a UAV's current status on pilot request and keep it current while exposed.

## Behaviour
Be-12.1.3 — Mixed selection-invoked, continuously-updating status panel. The pilot selects a UAV (via WAD touch or TDC cursor) to invoke its live status panel; the panel renders and refreshes continuously on Screen; dismiss via either Touch pathway. Binding 'which UAV' to 'show status' in one act.

## Structure
S-12.1.3.1 — Map-selected, R11-cloned docked status pane: (1) Map view (reused) as selection surface, with UAV icons as touch/TDC-selectable targets (redundant Touch pathways); (2) selecting a UAV icon opens/binds a docked UAV STATUS pane — a tiled WAD pane structurally cloned from R11's UAV PARAMS layout (same field grid, rendered read-only) with its own live-updating state reflecting the selected UAV; (3) pane continuously refreshes while open, selecting another icon re-targets it, and deselect / close affordance (touch target or bezel OSS) dismisses. Reuses Map view and R11 UAV PARAMS layout; consolidate shared status-output surface with R11 and R4.2.2 post-takeover monitoring.
