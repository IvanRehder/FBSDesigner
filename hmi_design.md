# HMI Design Document


## General


### R08 — Communicate Message (system->user) (output)

**Modalities:** Screen + Audio-out


**Function.** F-08.1: Deliver a discrete transactional message (acknowledgement/confirmation); transient, command-tied — make the pilot aware that a commanded action completed or was accepted. F-08.2: Present a persistent incoming message requiring pilot cognizance (C2 order / UAV-pilot response); content retained until acknowledged. F-08.3: Signal a capability/state change (e.g. data-link lost, autopilot condition reached) that alters what the pilot can do; awareness of a changed operating envelope. (F-08.3 shares the discrete state-change pattern with R02.)


**Behaviour.** Be-08.1.3 (F-08.1): attention audio confirmation callout synchronized with a transient visual banner that auto-decays after ~5 s; audio grabs attention, screen carries detail; each channel self-sufficient. Be-08.2.3 (F-08.2): distinct new-message audio cue on arrival + persistent visual message entry retained until acknowledged, with a preview showing the first words and full content retrievable on demand. Be-08.3.3 (F-08.3): distinct state-change audio signature at the moment of transition + a directed visual marker anchored to the changed screen/panel, with on-demand pop-up carrying the details of what changed; persistent visual state indicator holds the new steady state. All Behaviours are the combined Screen+Audio pathway. (Be-08.3.3 ≈ R02 Be-02.1, consolidate later.)


**Structure.** Consolidated. Audio (Audio system, shared notify channel with R02, distinct tone IDs): S-08.a Confirmation audio cue (Be-08.1.3); S-08.b New-message audio cue (Be-08.2.3); S-08.c State-change audio cue (Be-08.3.3). Visual (WAD Screen): S-08.d Pop-up component with 3 modes — transient(5s)/preview/on-demand (serves Be-08.1.3, Be-08.2.3, Be-08.3.3); S-08.e Notification marker component with 2 modes — generic-badge/directed-anchor (serves Be-08.2.3, Be-08.3.3); S-08.f Messages tab/screen, persistent message list, extends R06 order-output panel (Be-08.2.3). Input affordance: marker selection via Touch (WAD) or bezel OSS (Keyboard) — existing surfaces, no new element. Behaviour→Structure map: Be-08.1.3 = S-08.a + S-08.d(transient); Be-08.2.3 = S-08.b + S-08.d(preview) + S-08.e(generic) + S-08.f; Be-08.3.3 = S-08.c + S-08.d(on-demand) + S-08.e(directed) + shared R02 flag/audio pattern. Reuse flags: audio channel and state-change pattern shared with R02; Messages screen extends R06.


### R06 — Communicate Order (output)

**Modalities:** Screen + Audio-out


**Function.** F-06.1 — Convey the order's content to the pilot (comprehension of what is tasked): the pilot understands what the order is — type, target/area, parameters — not just that one arrived. Sustained readable/legible presentation the pilot can parse and reference while deciding/acting. Candidates dropped: arrival-awareness (folded into Behaviour as attention-capture, same pattern as R02) and persistent order-queue state (over-reach — the use cases describe a single inform step, no order-lifecycle management).


**Behaviour.** Be-06.1.1 — Full parallel presentation: on order arrival, complete order content rendered persistently on Screen AND spoken in full via templated TTS; either channel alone conveys the complete order. Orders are bounded and structured (type + target/area + few parameters), so the full readout is a short templated utterance, not open-ended narration — which keeps the verbose-TTS/comms concern realistic. Chosen over attention-cue+on-demand-readout and tiered summary-then-detail because comprehension of a safety-critical inbound order shouldn't be gated on a pilot re-request.


**Structure.** S-06.1.1.1 — Order Content Panel (WAD, Screen): persistent templated full-order display (type, target/AOI, parameters, timestamp); stacked overlay layer on the R05 Map/task surface (order anchors to POI/AOI). Always-complete Screen path. S-06.1.1.2 — Order TTS readout (cockpit audio, Audio-out): templated full-order speech on arrival, fixed slot structure; reuses R02's shared notify/audio-out channel. Always-complete Audio path. S-06.1.1.3 — HUD order flag (HUD, Screen): minimal eyes-out 'new order' indicator pointing to the WAD panel; supplementary (not a complete channel by itself), consistent with R02's dedicated HUD flag pattern. Complete-alone guarantee: WAD panel (Screen) OR TTS readout (Audio).


## Operate Aircraft


### R03 — Select Autopilot Mode (input)

**Modalities:** Touch + Keyboard


**Function.** Closing on **S-03.1 — Autopilot Mode Panel (WAD) + Bezel mode buttons.**

**R03 fully closed:**
- **F-03.1** — Engage an autopilot mode.
- **Be-03.1** — Direct mode selection (flat, one-shot).
- **S-03.1** — Autopilot Mode Panel (WAD, touch) + Bezel mode OSS/rotary (keyboard), one-shot engage.

Shared-structure notes carried forward: WAD panel shared with R02; bezel OSS block flagged as candidate for reuse with other discrete autopilot actions.

Ready for the next requirement.


**Behaviour.** We already closed the Behaviour for F-03.1 (Be-03.1) and its Structure (S-03.1). R03 is complete.

Do you want to:
- **Re-open R03's Behaviour** with fresh candidates (I'll relabel them Be-03.1.1, Be-03.1.2… tied explicitly to the F-03.1 index), or
- Move to the **next requirement**?

If re-opening, here are the candidates for F-03.1 (Engage an autopilot mode), Touch + Keyboard:

**Be-03.1.1 — Direct mode selection (flat, one-shot).**
Each mode is individually addressable; committing to one *is* engagement. Touch: tap the mode. Keyboard: dedicated OSS per mode, or rotary-step + commit button. One deliberate actuation engages. *(This is what we closed on.)*

**Be-03.1.2 — Default-engage then reselect.**
One actuation engages a predefined default mode; pilot changes mode afterward. Optimizes engage-speed under workload, defers discrimination. Distinct goal, but presumes a default mode the requirement doesn't specify.

**Be-03.1.3 — Confirm-guarded engagement.**
Selection is a proposal; a second distinct actuation (bezel confirm / second tap) commits it. Guards against accidental engagement — treats engaging automation as a safety-critical, deliberate act. Distinct goal (authority safety over speed).

Recommendation stays **Be-03.1.1** — matches the one-shot merged Function and satisfies redundancy cleanly.

Confirm the relabel to **Be-03.1.1**, or tell me to proceed to the next requirement.


**Structure.** Provide the next requirement and I'll proceed — ideally with:

- **Requirement ID + name** (e.g. R04)
- **Input/output nature**
- **Fixed modalities** for it
- **Intent** (one line)

I'll then state the intent back and propose candidate Functions (F-04.x).


### R01 — Input Autopilot Parameters (input)

**Modalities:** Touch + Keyboard


**Function.** F-01.1 — To make autopilot flight targets settable by the pilot. Goal: the pilot can commit specific numeric values (altitude/heading/speed) that become the autopilot's setpoints. Pure value-definition function; success = the intended values are held by the system as targets.


**Behaviour.** Be-01.1 (primary) — Direct value entry via WAD field: pilot selects the parameter and enters the numeric value. Touch: tap field, on-screen numeric keypad. Keyboard: UCP alphanumeric entry, or bezel rotary to step. Screen echoes committed target. Be-01.2 (complementary) — Increment/step adjustment from current value: Touch on-screen +/- or drag; Keyboard bezel rotary detents/OSS step buttons. Be-01.3 (complementary) — Select-from-preset/constrained pick: Touch tap list item; Keyboard bezel OSS or rotary scroll+select. Be-01.1 is primary because it alone guarantees full-range/full-resolution setting by either modality alone; Be-01.2/01.3 are complements, not independently modality-complete for the whole task.


**Structure.** S-01.1 Autopilot Setpoint Panel (WAD overlay): dedicated panel with Altitude/Heading/Speed fields, current + pending value, visual anchor and Touch surface, serves all three Behaviours. S-01.2 On-screen numeric keypad (WAD): realizes Be-01.1 via Touch. S-01.3 Field-adjacent step controls (WAD): realizes Be-01.2 via Touch. S-01.4 Preset list widget (WAD): realizes Be-01.3 via Touch. S-01.5 Bezel rotary + OSS: Keyboard path for stepping/select/pick (Be-01.2, Be-01.3). S-01.6 UCP alphanumeric entry: Keyboard path for absolute entry (Be-01.1). Redundancy check: Touch-only path = S-01.2/03/04 on S-01.1; Keyboard-only path = S-01.5+S-01.6; both complete the task independently.


### R04 — Stop Using Autopilot (input)

**Modalities:** Touch + Keyboard


**Function.** F-04.1 — To terminate an active autopilot mode. F-04.2 — To enable pilot selection of manual flight control. Both retained as distinct Functions once each was given a genuinely different Behaviour (re-press vs. one-shot MANUAL); before that, F-04.2 was assessed as collapsing into F-04.1 (same interaction possibilities) and was almost dropped as a rejected candidate.


**Behaviour.** Be-04.1 — Deactivate-by-re-press: pilot re-presses the currently-active mode control to deselect it; HMI forwards manual-control command; mode indicator clears on confirmation. Realizes F-04.1. Be-04.2 — One-shot disengage: pilot issues a single discrete action on a dedicated MANUAL affordance. Realizes F-04.2. Both modality-complete redundant (Touch alone / Keyboard alone / mixed). Design tension flagged: re-press/deselect (Be-04.1) carries the noise/vibration ambiguity originally raised against deselection-based control (favoring a dedicated MANUAL affordance instead) — accepted as secondary route, with the dedicated MANUAL (Be-04.2) as the robust primary.


**Structure.** S-04.1 — Autopilot mode panel (WAD), shared with R03; active-mode controls support re-tap-to-deselect. Touch path for Be-04.1. S-04.2 — Bezel mode buttons (OSS), shared with R03; active-mode OSS re-press-to-deselect + dedicated MANUAL button. Keyboard path, shared by both Behaviours. S-04.3 — Dedicated MANUAL touch button (WAD) on the mode panel, counterpart to the S-04.2 bezel MANUAL button. Touch path for Be-04.2. All reused/extended from R03; no new hardware.


### R02 — Notify Autopilot Reached (output)

**Modalities:** Screen + Audio-out


**Function.** Closed. Structure for Be-02.1 / F-02.1:

- **S-02.1 — AP Target/Current panel (WAD)** — shared with AP-set and AP-mode/state display.
- **S-02.2 — AP audio callout (Audio system)** — shared notify channel.
- **S-02.3 — AP "condition reached" flag (HUD)** — dedicated boolean indication.

R02 complete across all three layers.


**Behaviour.** Give me R03's details to start:

- **Requirement label + name** (e.g. R03: ...)
- **Direction** (input / output)
- **Fixed modalities** available for it
- **Intent** (one line)

I'll then state the intent back and propose candidate Functions (F-03.x).


**Structure.** We already closed the Structure for F-02.1 / Be-02.1 — three elements (S-02.1, S-02.2, S-02.3). R02 is fully complete across all layers.

Two possibilities:

1. **You want to re-open R02's Structure** with the fuller label scheme (S-02.<F>.<Be>.x). If so, I can restate the closed structures under that naming, but note we already settled the substance — nothing new to negotiate unless you want to reconsider the elements.

2. **You meant to start R03.** Your previous message just said "R03" without details. To begin R03 I need:
   - Requirement name
   - Direction (input/output)
   - Fixed modalities
   - Intent (one line)

Which do you want — re-label R02's structures, or provide R03's details?


## Conduct Intelligence and Reconnaissance


### R05 — Report Intelligence Data (input)

**Modalities:** Touch + Keyboard


**Function.** F-05.1 — To submit structured intelligence reports to C2. Candidates F-05.2 (quick-flag relay) and F-05.3 (delivery confirmation, output-side) were assessed and dropped: F-05.2 collapsed into F-05.1 once Behaviour simplified to preset-based marking; F-05.3 belongs to an output requirement, out of scope here.


**Behaviour.** Be-05.1 — Press-and-hold on the Map screen opens an option ring at that location; pilot selects a preset intelligence marker from the ring; selection commits the marker at that map location and sends it to C2. Modality-complete redundant: Touch alone (hold on WAD + tap) / Keyboard alone (bezel rotary step + OSS confirm) / mixed. Simpler than full free-text form authoring (initially proposed, then replaced by preset-based marking per designer request). Voice-annotated reporting was considered but rejected for this requirement — modalities are fixed to Touch/Keyboard only; voice belongs to a separate spin-off Function.


**Structure.** S-05.1.1 Map view (WAD) — reused, shared with R06/R07 (map-anchored tasks). S-05.1.2 Option ring — radial menu overlay at selected map point, shared mechanic with R06/R07. S-05.1.3 Preset marker buttons — intel-taxonomy entries in the ring. S-05.1.4 Marker glyph layer — committed markers rendered on map. S-05.1.5 Input bindings — Touch (hold+tap) / Keyboard (bezel rotary+OSS confirm), redundant. A touchpad was proposed as additional hardware and rejected — not in the fixed hardware baseline; cursor control without touching the screen maps to bezel rotary / UCP encoders instead.


## Conduct Surveillance


### R07 — Report Surveillance Event (input)

**Modalities:** Touch + Keyboard


**Function.** F-07.2 — Pilot reports a surveillance event with its classification to C2. The artefact exists so that C2 receives a typed/qualified event report as it happens; measurable effect: a classified event report is transmitted and acknowledged. The commit is the delivery mechanism; the classification gives the report its operational meaning.


**Behaviour.** Be-07.2.1 — Classify-then-commit, map-anchored (R05 pattern extended). Press-and-hold on Map at the observed location → option ring appears → select event-type marker from ring → report auto-populates with type + location → commit/send. Keyboard path: bezel OSS to open report, UCP/rotary to step through event types, OSS to commit. Modality-complete: Touch (hold+tap) and Keyboard (bezel rotary + OSS) paths both complete the full task.


**Structure.** S-07.2.1.1 — Map view (WAD), shared/reused from R05/R06. S-07.2.1.2 — Option ring (radial menu overlay at selected point), shared widget reused from R05. S-07.2.1.3 — Preset marker buttons, shared widget with surveillance event taxonomy as R07-specific content. S-07.2.1.4 — Marker glyph layer (committed event markers on map), shared layer reused from R05. S-07.2.1.5 — Input bindings: Touch (hold+tap) / Keyboard (bezel rotary + OSS), shared binding pattern reused from R05, both modality-complete. Note: entirely shared with R05/R06 except surveillance event taxonomy content; no new hardware or widgets.


## Perform UAV Tactical Takeover


### R09 — Initiate Takeover Request (input)

**Modalities:** Touch + Keyboard


**Function.** F-09.1 — Pilot issues a takeover request for a selected UAV. Enables the pilot to nominate a specific UAV and dispatch a control-transfer (takeover) request toward it (UC 4.1.1); the request action only, not the subsequent connection/monitoring.


**Behaviour.** F-09.1 carries all three complementary behaviours. Be-09.1.1 — Select-then-request (two-step, explicit): pilot selects the target UAV from a roster/map, then triggers a distinct REQUEST TAKEOVER action; two deliberate acts; request-pending state shown (R08 notification pattern). Touch: tap UAV glyph → tap REQUEST. Keyboard: bezel OSS steps/selects UAV → OSS commits request; UCP UAV-ID entry as alt selection. Be-09.1.2 — Direct action-on-object (selection + intent fused): pilot press-and-holds the UAV target (map glyph or roster row) → option ring appears → selects 'Takeover' → commits; reuses R05/R07 press-hold→option-ring→commit grammar. Touch: press-hold glyph → ring → Takeover → commit. Keyboard: OSS to focus UAV → OSS to open action menu → step to Takeover → commit. Be-09.1.3 — Request from a UAV-detail context: pilot opens the selected UAV's detail/status panel, then issues takeover from an in-panel button; selection implicit (open UAV). Touch: open panel → tap TAKEOVER. Keyboard: bezel OSS opens panel for focused UAV → OSS commits; UCP UAV-ID to open. All paths modality-complete in Touch and Keyboard.


**Structure.** S-09.1.1.1 (for Be-09.1.1) — UAV glyph layer on Map view (new; shared infrastructure for R10–R15) + dedicated REQUEST TAKEOVER button (WAD affordance shown when a UAV is selected) + request-pending marker (reuse R08 notification-marker) on selected glyph; UCP UAV-ID entry as alt Keyboard selection. S-09.1.2.1 (for Be-09.1.2) — same UAV glyph layer + option ring widget (reused from R05/R07) with new 'Takeover' segment + request-pending marker (reuse R08). S-09.1.3.1 (for Be-09.1.3) — new WAD UAV Detail/Status Panel (stacked layer; strong shared candidate reused/extended by R05 UAV-status, R06 ISR feed, R07 tracking, R08 handover status-hide) + in-panel TAKEOVER button + request-pending marker in panel header (reuse R08). Design decision: REQUEST TAKEOVER is ONE unified logical control surfaced across all three invocation contexts (dedicated button / ring segment / detail-panel button), sharing a single request-pending/notification back-end and a single UAV selection identity; the three structures differ only in invocation surface.


### R10 — Command Takeover (input)

**Modalities:** Touch + Keyboard


**Function.** F-10.1 — Execute the takeover command (commit to assume control): give the pilot a means to command the takeover procedure once the request acknowledgment is received, turning a granted request into an active control transfer by commanding connection with the UAV and assuming control (UC 4.2.2–4.2.3).


**Behaviour.** Be-10.1.1 — Single deliberate one-shot commit, state-gated on takeover-request confirmation: the COMMAND TAKEOVER affordance is inert/disabled until the R09 request acknowledgment is received (delivered via R08); once confirmed, the affordance becomes active and a single action (Touch tap or Keyboard bezel OSS press) transmits the takeover command (4.2.2–4.2.3). No separate confirm step — the prior acknowledgment is the gate. Each modality independently completes the full commit.


**Structure.** S-10.1.1.1 — Dedicated COMMAND TAKEOVER button: co-located with the R08 confirmation delivery (pop-up / messages-tab entry); Touch = single tap on WAD button, Keyboard = mapped bezel OSS press; rendered inert/greyed until R08 request-acknowledged event, active on ack, reverts after commit/timeout/link-loss; fastest lowest-workload commit. S-10.1.1.2 — Option-ring segment: R09 press-and-hold radial option ring on the UAV glyph (Map / UAV list) extended with a COMMAND TAKEOVER segment; Touch = press-and-hold on UAV → ring opens → select segment → release to commit, Keyboard = bezel rotary selects segment + OSS confirm; segment appears/enables only post-ack for that UAV; spatial/in-context commit. S-10.1.1.3 — UAV detail panel row: COMMAND TAKEOVER row within the selected-UAV detail panel; Touch = tap row, Keyboard = bezel rotary to focus row + OSS activate; row disabled until ack for that UAV, enabled post-ack; context-explicit commit that guards against wrong-UAV selection. Common: all three are the same takeover-command action, gated by the R08 request-acknowledged state, each independently modality-complete (Touch alone or Keyboard alone), all reused and extended from R09 surfaces with the post-ack COMMAND TAKEOVER state as a shared lifecycle control.


## Control UAVs


### R11 — Input New UAV Parameters (input)

**Modalities:** Touch + Keyboard


**Function.** F-11.1 — Pilot submits new UAV flight parameters: the pilot's intended parameter values (speed, altitude, heading) become the UAV's commanded targets. F-11.2 — Pilot is made aware the UAV accepted the new parameters: closure on the round-trip acknowledgment.


**Behaviour.** F-11.1 → Be-11.1.1 Direct value entry (primary): pilot opens the UAV parameter panel, enters speed/altitude/heading values directly via numeric keypad (Touch) or UCP/bezel alphanumeric (Keyboard), commits; modality-complete on each path. Be-11.1.2 Step/increment adjustment (complement): pilot nudges each parameter up/down via on-screen steppers (Touch) or bezel rotary (Keyboard). Be-11.1.3 Preset parameter profiles: pilot selects a stored profile (e.g. loiter, transit) that populates all three values at once, then commits. F-11.2 → Be-11.2.1 Redundant ack notification (R08 reuse): on UAV acknowledgment, fire the shared R08 audio tone plus visual notification; modality-complete on output.


**Structure.** S-11.1.1.1 — UAV Parameter Panel (WAD, R01 Setpoint-Panel component family re-instantiated with UAV param semantics): three parameter rows (speed / altitude / heading), each with numeric field + keypad (Touch, Be-11.1.1) and ± steppers (Touch, Be-11.1.2), plus a preset selector row (Touch, Be-11.1.3); bezel rotary maps to selected-row stepping and UCP alphanumeric to direct value entry (Keyboard path, all three behaviours); Commit/Send affordance via Touch OSS and bezel OSS; both paths modality-complete. S-11.2.1.1 — Ack via shared R08 notification stack: audio tone (shared Audio notify channel) + reusable multi-mode pop-up + notification-marker + messages-tab entry; parameter-accepted event routed into existing R08 components, no new structure.


### R12 — Expose UAV Status (input)

**Modalities:** Screen + Touch


**Function.** F-12.1 — Pilot can call up (show) and dismiss (hide) the status panel of any connected UAV. Goal: control the visibility of the UAV information surface on demand — open it when wanted, close it back when done (show the tab/window/panel with the UAV's information).


**Behaviour.** Be-12.1.1 + Be-12.1.2 (combined) — Pilot shows the UAV status panel via a persistent status control; hides it by re-pressing that same control (toggle) or via a dedicated close affordance on the panel itself. Two dismissal paths coexist. Modality-complete: Touch (tap control / tap X) or Keyboard (bezel toggle OSS / dismiss OSS); Screen renders the panel.


**Structure.** S-12.1.[1+2].1 — Reused WAD UAV Detail/Status Panel (shared with R10/R11), with a persistent UAV Status tab/OSS to toggle the panel show/hide and a header close (X) control to dismiss it; panel body renders attitude/health/state. Modality-complete: Touch (tab / X) or Keyboard (bezel toggle OSS / dismiss OSS); Screen renders the panel.


### R13 — Communicate UAV Status (output)

**Modalities:** Screen + Audio-out


**Function.** F-13.1 — Maintain continuous UAV status awareness (persistent, ambient display of link, mode, health, fuel, position/attitude summary); F-13.2 — Alert the pilot to UAV status changes/anomalies (event-driven, attention-capturing on transitions, degradation, faults).


**Behaviour.** Be-13.1.1 — Persistent multi-field status render: UAV status fields continuously displayed on Screen in a fixed panel, updating in place as new data arrives; no steady-state audio. Be-13.2.1 — Redundant alert on transition: on a status change/fault, fire a one-shot audio tone plus a visual highlight/flag on the changed field. Be-13.2.2 — Severity-graded alert: same as Be-13.2.1 but tone and visual treatment differentiated by severity tier (advisory/caution/warning).


**Structure.** S-13.1.1.1 — Extended R12 UAV Detail/Status Panel on WAD with live field set (link, mode, health, fuel, position/attitude summary), updating in place (shared with R12 visibility and R08 notifications); S-13.1.1.2 — HUD abbreviated always-on status strip (link/mode/health rollup) for head-up glance; S-13.2.x.1 — R08 notification stack, severity-parameterized: single tone for Be-13.2.1 / tiered tones for Be-13.2.2, plus field-level highlight/flag (colour-coded by severity) and reusable R08 pop-up/notification-marker (no new hardware); S-13.2.x.2 — HUD-escalated warning that pushes top-severity flags to the S-13.1.1.2 strip.


## Employ UAV for ISR Operations


### R16 — Expose ISR Sensor Data (input)

**Modalities:** Touch + Keyboard


**Function.** F-16.1 — Summon ISR sensor feed into view: the pilot obtains access to the ISR sensor data output on demand (make it present/visible). F-16.2 — Select which ISR data stream to expose: the pilot chooses among multiple ISR sources/sensors what to bring up.


**Behaviour.** Be-16.1.1 (Touch): one-shot summon/dismiss of the ISR feed via a 'ISR FEED' button on the UAV screen plus a WAD panel header control. Be-16.1.2 (Keyboard): bezel OSS / UCP soft-key toggle of the feed panel on/off. Be-16.2.1 (Touch): direct source selection via in-panel source tabs/list. Be-16.2.2 (Keyboard): bezel rotary/UCP up-down stepping through available sources. All pathways modality-complete; Mixed pathway dropped.


**Structure.** S-16.1.1.1 — ISR Feed Panel/Window on WAD (stacked overlay up to 8-source limit, reusing R12/R13 Detail/Status Panel chassis: header, close X, persistent toggle) + 'ISR FEED' button on UAV screen (Touch invocation) + WAD panel header X/re-summon control (Touch) + bezel OSS/UCP soft-key toggle (Keyboard). S-16.2.1.1 — in-panel source tab strip/list (Touch, one entry per sensor source, active highlighted) + bezel rotary (detented)/UCP up-down keys (Keyboard) reflected on the same tab strip. Reuse flags: panel chassis <- R12/R13; multi-surface invocation <- R09/R14; optional summon-ack <- R08.


### R14 — Input Sensor Move (input)

**Modalities:** Wearable/HMD + Touch


**Function.** F-14.1 — Command sensor line-of-sight to a designated target/point/area (the pilot designates a destination/aimpoint and the system directs the UAV's ISR sensor there; continuous real-time steering is retained as an alternative behaviour to achieve this same aiming goal).


**Behaviour.** Be-14.1.1 (Touch-only, discrete): Press-and-hold on Map/feed location → option ring appears → select 'Move Sensor Here' (POI/AOI variant) → commits slew; reuses R05/R07 press-hold→option-ring pattern. Be-14.1.2 (HMD-only, discrete): Gaze/head designates the aimpoint on the visor → confirm via HOTAS button or UCP keyboard press → commits slew. Be-14.1.3 (HMD-only, continuous): Head-slaved continuous steering — sensor aim follows head pointing while an engage condition is held; release stops. Be-14.1.4 (Touch-only, continuous): Rate-slew via TDC deflection (primary) or WAD swipe-drag on the feed — sensor slews proportional to input; release/center stops.


**Structure.** S-14.1.*.1 — Map-anchored designation set: Map view + live-feed frame (WAD tappable surfaces), option ring (WAD overlay, reused from R05/R07 with 'Move Sensor Here/POI/AOI' segment), sensor-aimpoint glyph + footprint layer (WAD overlay), slew-complete ack via shared R08 notification stack — serves Be-14.1.1. S-14.1.*.2 — HMD designate-and-slew set: HMD visor reticle (in-visor output), head/eye-tracking (HMD input), HOTAS engage/confirm button or UCP key (commit for .2, hold-engage for .3), sensor-aimpoint glyph mirrored on WAD + HUD strip (reused from R13) — serves Be-14.1.2 and Be-14.1.3. S-14.1.*.3 — Continuous rate-slew set: TDC (rate deflection, hands-on-throttle), WAD swipe zone on feed frame (drag→rate slew alternative), rate/direction indicator (WAD overlay showing slew vector + moving footprint), shared sensor-aimpoint glyph layer — serves Be-14.1.4.


### R15 — Input Search Pattern (input)

**Modalities:** Touch + Keyboard


**Function.** F-15.1 — Specify search-pattern geometry over a geographic area: the pilot delimits where coverage happens by defining the area/track shape (box, spiral, sector, polygon) anchored on the map. F-15.2 — Parameterize a search pattern's scan attributes: the pilot sets how the pattern is flown/scanned — leg spacing, orientation/heading, scan speed, overlap.


**Behaviour.** F-15.1: Be-15.1.1 (Touch-only) — tap to drop area vertices/corners and drag to size/rotate the shape with live geometry preview, then commit. Be-15.1.2 (Keyboard-only) — enter geometry numerically via UCP/bezel (anchor coords, dimensions, orientation), map echoes each value, commit via OSS. Be-15.1.3 (Mixed) — touch to place/rough-shape the area, keyboard to refine exact coords/dimensions of the same object; each path standalone-complete. F-15.2: Be-15.2.1 (Touch-only) — Setpoint-style panel with keypad entry, steppers and presets for each attribute, all by touch. Be-15.2.2 (Keyboard-only) — same attribute set via bezel rotary (step) + UCP alphanumeric (direct), field-by-field, commit via OSS. Be-15.2.3 (Mixed) — field-by-field mix on the Setpoint Panel (touch some fields, keyboard others); falls out of the same structure, not a separate design effort.


**Structure.** F-15.1 (Be-15.1.1/.1.2/.1.3): S-15.1.x.1 — Map-anchored geometry editor (recommended): Search-Area overlay layer on the shared Map view with draggable vertex/rotate handles (Touch) + two-way-bound Geometry Field strip via UCP alphanumeric + bezel rotary (Keyboard), binding between them serving Mixed; commit via OSS + on-panel button; reuses Map view and overlay/commit pattern (R05/R14). S-15.1.x.2 — Shape-type palette + parametric form (fallback): palette selects shape type (box/spiral/sector/ladder), Geometry Field strip drives dimensions, map shows result; weaker direct-manipulation touch story. F-15.2 (Be-15.2.1/.2.2/.2.3): S-15.2.x.1 — Re-instantiated Setpoint Panel (recommended, shared reuse from R01/R11) with search-pattern attribute set (leg spacing, orientation, scan speed, overlap %): keypad/steppers/presets (Touch), bezel rotary + UCP (Keyboard), field-by-field mix (Mixed), acknowledgment via shared R08 notification stack. S-15.2.x.2 — Inline attribute rows folded into the F-15.1 geometry panel: unified surface, single commit; diverges from Setpoint-Panel convention.


## Employ UAV for Target Tracking


### R17 — Command Track Target of Interest (TOI) (input)

**Modalities:** Touch + Keyboard


**Function.** F-17.1 — Designate the TOI: establish which target the UAV should track (spatial/identity selection of the target), reusing R14's target-selection surface. F-17.2 — Command the UAV to track the designated TOI: commit the tracking order, directing UAV sensors to lock/center on the specified target so the UAV enters tracking on that target.


**Behaviour.** F-17.1: Be-17.1.1 — Touch-only: pilot taps a target symbol on the Map/ISR feed to select it; press-hold on empty space drops a TOI marker (reuses R14 press-hold→option-ring pattern); selected target highlights as active TOI. Be-17.1.2 — Keyboard-only: pilot cycles detected tracks/contacts with a bezel rotary and confirms selection via OSS, or enters target coordinates/track-ID via UCP alphanumeric. F-17.2: Be-17.2.1 — Touch-only: with a TOI active, pilot selects TRACK from the option-ring or a dedicated on-screen TRACK button for one-shot commit. Be-17.2.2 — Keyboard-only: dedicated bezel TRACK OSS press commits tracking on the active TOI. Be-17.2.3 — Mixed: designate via Touch (tap target), commit via Keyboard (bezel TRACK OSS). Each modality alone stays modality-complete; Mixed is an offered convenience, not a required split.


**Structure.** S-17.1.1.1 — Map/ISR-anchored designation surface (serves Be-17.1.1 + Be-17.1.2): Map view + R16 ISR Feed Panel canvas, reused/extended track/contact glyph layer (tappable, highlights active TOI), press-hold→option-ring (shared R05/R14) for marker drop/designation, bezel rotary track-list cycle + bezel OSS confirm, UCP alphanumeric for track-ID/coordinate entry, TDC cursor-mediated pointing on WAD. S-17.2.1.1 — Tracking commit controls (serves Be-17.2.1/.2/.3): option-ring TRACK segment (Touch, on active TOI), dedicated bezel TRACK OSS (Keyboard commit), TOI detail/status row with inline TRACK affordance (reuses R12/R13 Detail Panel chassis). Shared acknowledgment: R08 notification stack (audio tone + visual pop-up/marker) for execution confirmation (7.1.7–7.1.10), no new element. Net-new to R17: only the TRACK commit affordance (ring segment + bezel OSS + detail row).


### R18 — Set Tracking Distance from TOI (input)

**Modalities:** Touch + Keyboard


**Function.** F-18.1 — Set the standoff distance value: the pilot establishes/adjusts the numeric standoff/tracking distance the UAV maintains from the target of interest (TOI), committing a scalar range parameter.


**Behaviour.** Be-18.1.1 (Touch-only direct + stepper): pilot opens the distance field, taps to reveal an on-screen keypad for direct entry or uses on-screen +/− steppers for incremental adjustment, then commits on-screen. Be-18.1.2 (Keyboard-only entry): pilot enters the value via UCP alphanumeric keypad or steps it with the bezel rotary, committing via bezel OSS. These form the modality-complete redundant pair; Be-18.1.3 (map-anchored radius ring) was logged as an optional complement but not carried.


**Structure.** S-18.1.3 — Setpoint Panel re-instantiated for a single 'Tracking Distance' field, using the same interaction grammar as the AP Parameters panel (R01/R11): Touch keypad + on-screen +/− steppers; Keyboard bezel rotary + UCP alphanumeric; commit via on-screen button or bezel OSS. PLUS an inline editable distance row embedded in the R17 tracking panel as a co-located quick-access surface. Acknowledgement reuses the shared R08 notification stack (7.2.7).


## Conduct UAV Control Handover


### R19 — Initiate Handover Request (input)

**Modalities:** Touch + Keyboard


**Function.** F-19.1 — Dispatch a control-handover request to a selected UAV: the pilot signals intent to transfer the currently-managed UAV back to the UAV Pilot, initiating the handover negotiation (8.1.1). Response awareness (8.1.7) defers to the R08 notification stack.


**Behaviour.** Be-19.1.1 (Touch-only): press-hold on the UAV glyph/map or detail panel surfaces an option ring with a HANDOVER segment, tap to dispatch. Be-19.1.2 (Keyboard-only): bezel OSS dedicated HANDOVER button with UAV pre-selected via rotary/UCP, single press dispatches. Be-19.1.3 (Mixed): UAV Detail/Status Panel exposes a HANDOVER row reachable by touch tap or bezel OSS confirm. All three modality-complete, mirroring R09.


**Structure.** S-19.1.1 (dedicated HANDOVER button — bezel OSS + WAD touch affordance); S-19.1.2 (HANDOVER option-ring segment anchored to the UAV glyph); S-19.1.3 (HANDOVER row in the reused UAV Detail/Status Panel, R12 chassis). All reused from R09/R10/R17 with only the HANDOVER action binding added; response/ack via R08 notification stack, no new structure.


### R20 — Command Handover (input)

**Modalities:** Touch + Keyboard


**Function.** F-20.1 — Command handover execution (confirmation-gated one-shot commit): the pilot issues the handover-execute command, offered only once the R19 handover request has been acknowledged; committing terminates own control of the UAV (mirrors R10 atop R09). Completion awareness (8.1.17–8.1.18) and status-hide (8.1.16) are handled by reuse of R08 notifications and the R12/R13 status panel rather than by new Functions.


**Behaviour.** Be-20.1.1 (Touch) — one-shot HANDOVER-EXECUTE commit affordance, armed only after R19 ack, surfaced on all three shared surfaces (dedicated command button, option-ring segment, UAV detail-panel row); a single tap commits, breaks the connection, and triggers the completion notification. Be-20.1.2 (Keyboard) — the same armed HANDOVER-EXECUTE action via bezel OSS / UCP discrete press. Both pathways are modality-complete and confirmation-gated; no distinct Mixed pathway (atomic action).


**Structure.** S-20.1.1.1 — Reused three-surface commit set with HANDOVER-EXECUTE binding: dedicated command button (WAD, shared R09/R10/R19) with armed HANDOVER-EXECUTE state; option-ring segment (shared press-hold ring, R05/R14/R17/R19) HANDOVER-EXECUTE segment; UAV detail-panel row (shared R12/R13/R16 chassis) HANDOVER-EXECUTE row; bezel OSS + UCP (Keyboard) mapped to the same armed action. Arming driven by R19-ack state; completion and status-hide via reused R08 notification stack and R12/R13 panel (8.1.16–8.1.18). Adds only the execute/commit armed-after-ack state atop R19's request binding.
