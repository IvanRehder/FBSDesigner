# R14 — Input Sensor Move (input)

**Modalities:** Wearable/HMD and Touch

## Function
F-14.1 — Command sensor line-of-sight to a designated target/point/area (the pilot designates a destination/aimpoint and the system directs the UAV's ISR sensor there; continuous real-time steering is retained as an alternative behaviour to achieve this same aiming goal).

## Behaviour
Be-14.1.1 (Touch-only, discrete): Press-and-hold on Map/feed location → option ring appears → select 'Move Sensor Here' (POI/AOI variant) → commits slew; reuses R05/R07 press-hold→option-ring pattern. Be-14.1.2 (HMD-only, discrete): Gaze/head designates the aimpoint on the visor → confirm via HOTAS button or UCP keyboard press → commits slew. Be-14.1.3 (HMD-only, continuous): Head-slaved continuous steering — sensor aim follows head pointing while an engage condition is held; release stops. Be-14.1.4 (Touch-only, continuous): Rate-slew via TDC deflection (primary) or WAD swipe-drag on the feed — sensor slews proportional to input; release/center stops.

## Structure
S-14.1.*.1 — Map-anchored designation set: Map view + live-feed frame (WAD tappable surfaces), option ring (WAD overlay, reused from R05/R07 with 'Move Sensor Here/POI/AOI' segment), sensor-aimpoint glyph + footprint layer (WAD overlay), slew-complete ack via shared R08 notification stack — serves Be-14.1.1. S-14.1.*.2 — HMD designate-and-slew set: HMD visor reticle (in-visor output), head/eye-tracking (HMD input), HOTAS engage/confirm button or UCP key (commit for .2, hold-engage for .3), sensor-aimpoint glyph mirrored on WAD + HUD strip (reused from R13) — serves Be-14.1.2 and Be-14.1.3. S-14.1.*.3 — Continuous rate-slew set: TDC (rate deflection, hands-on-throttle), WAD swipe zone on feed frame (drag→rate slew alternative), rate/direction indicator (WAD overlay showing slew vector + moving footprint), shared sensor-aimpoint glyph layer — serves Be-14.1.4.
