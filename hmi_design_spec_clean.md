# HMI Design Spec — Clean

Naming: F-Rxx.n · Be-Rxx.n · S-Rxx.n (sequential, no sub-scheme mixing)

---

## General

### R08 — Communicate Message (system→user) (output) — Screen + Audio-out
- **F1** Deliver a transient transactional message (ack/confirmation).
- **F2** Present a persistent incoming message until acknowledged.
- **F3** Signal a capability/state change.
- **Be1** (F1) Audio callout + transient banner, auto-decays ~5s.
- **Be2** (F2) Distinct audio cue + persistent entry, preview + full-on-demand.
- **Be3** (F3) Distinct audio signature + directed marker, on-demand pop-up detail.
- **S1** Audio: 3 distinct tone IDs (shared channel w/ R02).
- **S2** Pop-up component, 3 modes: transient / preview / on-demand.
- **S3** Notification marker, 2 modes: generic-badge / directed-anchor.
- **S4** Messages tab (extends R06 panel).

### R06 — Communicate Order (output) — Screen + Audio-out
- **F1** Convey full order content to pilot.
- **Be1** Full parallel presentation: complete content on Screen + full templated TTS.
- **S1** Order Content Panel (WAD overlay on Map).
- **S2** Order TTS readout (shared R02 audio channel).
- **S3** HUD order flag (supplementary).

---

## Operate Aircraft

### R01 — Input Autopilot Parameters (input) — Touch + Keyboard
- **F1** Make AP targets settable by pilot.
- **Be1** (primary) Direct value entry.
- **Be2** (complement) Increment/step.
- **Be3** (complement) Preset pick.
- **S1** Autopilot Setpoint Panel (WAD).
- **S2** Numeric keypad (Touch).
- **S3** Step controls (Touch).
- **S4** Preset list (Touch).
- **S5** Bezel rotary + OSS (Keyboard).
- **S6** UCP alphanumeric (Keyboard).

### R02 — Notify Autopilot Reached (output) — Screen + Audio-out
- **F1** Make pilot aware AP reached target.
- **Be1** Screen convergence display + one-shot audio callout.
- **S1** AP Target/Current panel (WAD).
- **S2** Audio callout (shared notify channel).
- **S3** "Condition reached" flag (HUD).

### R03 — Select Autopilot Mode (input) — Touch + Keyboard
- **F1** Engage an autopilot mode.
- **Be1** Direct mode selection, one-shot.
- **S1** Autopilot Mode Panel (WAD, Touch) + Bezel mode OSS/rotary (Keyboard).

### R04 — Stop Using Autopilot (input) — Touch + Keyboard
- **F1** Terminate active AP mode.
- **F2** Enable pilot selection of manual flight control.
- **Be1** (F1) Deactivate-by-re-press.
- **Be2** (F2) One-shot disengage via dedicated MANUAL affordance.
- **S1** AP mode panel (WAD, shared R03) — re-tap-to-deselect.
- **S2** Bezel mode buttons (shared R03) — re-press + dedicated MANUAL.
- **S3** Dedicated MANUAL touch button (WAD).

---

## Conduct Intelligence and Reconnaissance

### R05 — Report Intelligence Data (input) — Touch + Keyboard
- **F1** Submit structured intel reports to C2.
- **Be1** Press-and-hold on Map → option ring → select preset marker → commit/send.
- **S1** Map view (shared R06/R07).
- **S2** Option ring (shared R06/R07).
- **S3** Preset marker buttons (intel taxonomy).
- **S4** Marker glyph layer.
- **S5** Input bindings — Touch (hold+tap) / Keyboard (rotary+OSS).

---

## Conduct Surveillance

### R07 — Report Surveillance Event (input) — Touch + Keyboard
- **F1** Report a classified surveillance event to C2.
- **Be1** Classify-then-commit, map-anchored (extends R05 pattern).
- **S1** Map view (shared R05/R06).
- **S2** Option ring (shared R05).
- **S3** Preset marker buttons (surveillance taxonomy).
- **S4** Marker glyph layer (shared R05).
- **S5** Input bindings (shared R05).

---

## Perform UAV Tactical Takeover

### R09 — Initiate Takeover Request (input) — Touch + Keyboard
- **F1** Dispatch a takeover request for a selected UAV.
- **Be1** Select-then-request (two-step, explicit).
- **Be2** Direct action-on-object (press-hold → option ring → Takeover).
- **Be3** Request from UAV-detail panel.
- **S1** UAV glyph layer on Map (new, shared infra R10-R20) + REQUEST button + pending marker.
- **S2** Option ring w/ Takeover segment (shared R05/R07) + pending marker.
- **S3** UAV Detail/Status Panel (new, shared infra R10-R20) + in-panel TAKEOVER button.

### R10 — Command Takeover (input) — Touch + Keyboard
- **F1** Execute the takeover command, gated on R09 ack.
- **Be1** Single one-shot commit, state-gated on R09 ack (via R08).
- **S1** Dedicated COMMAND TAKEOVER button (inert until ack).
- **S2** Option-ring TAKEOVER segment (shared R09).
- **S3** UAV detail-panel TAKEOVER row (shared R09).

---

## Control UAVs

### R11 — Input New UAV Parameters (input) — Touch + Keyboard
- **F1** Submit new UAV flight parameters.
- **F2** Awareness of UAV acceptance ack.
- **Be1** (F1, primary) Direct value entry.
- **Be2** (F1, complement) Step/increment.
- **Be3** (F1, complement) Preset profiles.
- **Be4** (F2) Redundant ack notification (R08 reuse).
- **S1** UAV Parameter Panel (WAD, Setpoint Panel family, shared R01).
- **S2** Ack via shared R08 notification stack (no new structure).

### R12 — Expose UAV Status (input) — Screen + Touch
- **F1** Show/hide the UAV status panel on demand.
- **Be1** Toggle control + dedicated close (X), two dismissal paths.
- **S1** UAV Detail/Status Panel (shared R09/R10) + persistent tab/OSS toggle + close (X).

### R13 — Communicate UAV Status (output) — Screen + Audio-out
- **F1** Maintain continuous UAV status awareness.
- **F2** Alert pilot to status changes/anomalies.
- **Be1** (F1) Persistent multi-field status render, no steady-state audio.
- **Be2** (F2) Redundant alert on transition (tone + visual flag).
- **Be3** (F2) Severity-graded alert variant.
- **S1** Extended UAV Detail/Status Panel (shared R12) — live field set.
- **S2** HUD abbreviated status strip.
- **S3** R08 notification stack, severity-parameterized.

---

## Employ UAV for ISR Operations

### R16 — Expose ISR Sensor Data (input) — Touch + Keyboard
- **F1** Summon ISR sensor feed into view.
- **F2** Select which ISR stream to expose.
- **Be1** (F1) One-shot summon/dismiss (Touch button + Keyboard toggle).
- **Be2** (F2) Direct source selection (tabs / rotary stepping).
- **S1** ISR Feed Panel (shared R12/R13 chassis) + summon controls.
- **S2** In-panel source tab strip.

### R14 — Input Sensor Move (input) — Wearable/HMD + Touch
- **F1** Command sensor line-of-sight to a designated target/point/area.
- **Be1** (Touch, discrete) Press-hold on Map/feed → option ring → commit slew.
- **Be2** (HMD, discrete) Gaze/head designate → confirm via HOTAS/UCP.
- **Be3** (HMD, continuous) Head-slaved continuous steering.
- **Be4** (Touch, continuous) Rate-slew via TDC or WAD swipe-drag.
- **S1** Map-anchored designation set (shared R05/R07 option ring) + aimpoint glyph.
- **S2** HMD designate-and-slew set (visor reticle + tracking + HOTAS confirm).
- **S3** Continuous rate-slew set (TDC + WAD swipe zone + rate indicator).

### R15 — Input Search Pattern (input) — Touch + Keyboard
- **F1** Specify search-pattern geometry over an area.
- **F2** Parameterize scan attributes (spacing, orientation, speed, overlap).
- **Be1** (F1, Touch) Tap-drop vertices + drag to size/rotate.
- **Be2** (F1, Keyboard) Numeric geometry entry via UCP/bezel.
- **Be3** (F1, Mixed) Touch to rough-shape, Keyboard to refine.
- **Be4** (F2, Touch) Setpoint-style panel, all touch.
- **Be5** (F2, Keyboard) Bezel rotary + UCP, field-by-field.
- **Be6** (F2, Mixed) Field-by-field mix on same panel.
- **S1** Map-anchored geometry editor (shared Map/overlay pattern R05/R14).
- **S2** Re-instantiated Setpoint Panel (shared R01/R11).

---

## Employ UAV for Target Tracking

### R17 — Command Track Target of Interest (input) — Touch + Keyboard
- **F1** Designate the TOI.
- **F2** Command UAV to track the designated TOI.
- **Be1** (F1, Touch) Tap target symbol / press-hold to drop TOI marker.
- **Be2** (F1, Keyboard) Cycle tracks via rotary + OSS confirm, or UCP ID entry.
- **Be3** (F2, Touch) Select TRACK from option-ring or dedicated button.
- **Be4** (F2, Keyboard) Dedicated bezel TRACK OSS.
- **Be5** (F2, Mixed) Designate Touch, commit Keyboard.
- **S1** Map/ISR-anchored designation surface (shared R16 canvas + R05/R14 option ring).
- **S2** Tracking commit controls (ring segment + bezel OSS + detail row, shared R12/R13 chassis).

### R18 — Set Tracking Distance from TOI (input) — Touch + Keyboard
- **F1** Set the standoff distance value.
- **Be1** (Touch) Keypad/steppers on-screen.
- **Be2** (Keyboard) UCP alphanumeric / bezel rotary.
- **S1** Setpoint Panel re-instantiated for single field (shared R01/R11) + inline row in R17 panel.

---

## Conduct UAV Control Handover

### R19 — Initiate Handover Request (input) — Touch + Keyboard
- **F1** Dispatch a control-handover request for a selected UAV.
- **Be1** (Touch) Press-hold → option ring → HANDOVER segment.
- **Be2** (Keyboard) Bezel HANDOVER OSS, UAV pre-selected.
- **Be3** (Mixed) UAV Detail Panel HANDOVER row.
- **S1** Dedicated HANDOVER button (bezel + WAD touch).
- **S2** HANDOVER option-ring segment (shared R09 ring).
- **S3** HANDOVER row in UAV Detail Panel (shared R12 chassis).

### R20 — Command Handover (input) — Touch + Keyboard
- **F1** Command handover execution, gated on R19 ack.
- **Be1** (Touch) One-shot HANDOVER-EXECUTE, armed after ack.
- **Be2** (Keyboard) Same action via bezel OSS/UCP.
- **S1** Reused three-surface commit set (button + ring segment + detail row) with HANDOVER-EXECUTE binding.
