# R19 — Initiate Handover Request (input)

**Modalities:** Touch and Keyboard

## Function
F-19.1 — Dispatch a control-handover request to a selected UAV: the pilot signals intent to transfer the currently-managed UAV back to the UAV Pilot, initiating the handover negotiation (8.1.1). Response awareness (8.1.7) defers to the R08 notification stack.

## Behaviour
Be-19.1.1 (Touch-only): press-hold on the UAV glyph/map or detail panel surfaces an option ring with a HANDOVER segment, tap to dispatch. Be-19.1.2 (Keyboard-only): bezel OSS dedicated HANDOVER button with UAV pre-selected via rotary/UCP, single press dispatches. Be-19.1.3 (Mixed): UAV Detail/Status Panel exposes a HANDOVER row reachable by touch tap or bezel OSS confirm. All three modality-complete, mirroring R09.

## Structure
S-19.1.1 (dedicated HANDOVER button — bezel OSS + WAD touch affordance); S-19.1.2 (HANDOVER option-ring segment anchored to the UAV glyph); S-19.1.3 (HANDOVER row in the reused UAV Detail/Status Panel, R12 chassis). All reused from R09/R10/R17 with only the HANDOVER action binding added; response/ack via R08 notification stack, no new structure.
