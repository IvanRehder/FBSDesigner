# R03 — Select Autopilot Mode (input)

**Modalities:** Touch and Keyboard

## Function
Closing on **S-03.1 — Autopilot Mode Panel (WAD) + Bezel mode buttons.**

**R03 fully closed:**
- **F-03.1** — Engage an autopilot mode.
- **Be-03.1** — Direct mode selection (flat, one-shot).
- **S-03.1** — Autopilot Mode Panel (WAD, touch) + Bezel mode OSS/rotary (keyboard), one-shot engage.

Shared-structure notes carried forward: WAD panel shared with R02; bezel OSS block flagged as candidate for reuse with other discrete autopilot actions.

Ready for the next requirement.

## Behaviour
We already closed the Behaviour for F-03.1 (Be-03.1) and its Structure (S-03.1). R03 is complete.

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

## Structure
Provide the next requirement and I'll proceed — ideally with:

- **Requirement ID + name** (e.g. R04)
- **Input/output nature**
- **Fixed modalities** for it
- **Intent** (one line)

I'll then state the intent back and propose candidate Functions (F-04.x).
