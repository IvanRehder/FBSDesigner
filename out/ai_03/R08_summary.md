# R08 — Communicate Message (system->user) (output)

**Modalities:** Screen and Audio-out

## Function
F-08.3 — Convey with graded priority (triage): Function is to deliver system-generated messages while differentiating their operational importance, so the pilot's finite attention is allocated correctly (routine acknowledgment vs. safety-critical). The message's weight is communicated alongside its content.

## Behaviour
Be-08.3.3 — Mixed (cross-channel reinforcement): Priority governs how many channels fire and how insistently. Routine = Screen notification strip only, no audio. Elevated = Screen persistent + single audio ping. Critical = Screen modal banner + repeating audio/TTS, both cleared by one acknowledgment. The channel-count itself becomes a priority cue; critical content is fully available on either channel independently (modality-complete redundancy). Established as the foundational output/feedback behaviour reused by downstream requirements (R02, R06, and all HMI-informs-pilot / acknowledgment steps).

## Structure
S-08.3.3.2 — Distributed by criticality across WAD + HUD: WAD notification strip (fixed persistent region) rendering three visual tiers — routine (transient, auto-dismiss ~5s), elevated (held until read), critical (expands to modal high-contrast banner, blocks until ack); message store backing the strip for persistence and re-review; critical tier mirrored to HUD as a forward-view banner for the head-out pilot; per-tier audio mapping (routine = silent, elevated = single ping, critical = repeating tone + TTS); single Acknowledge control (WAD touch or bezel OSS) clearing WAD + HUD + audio together. The notification strip + message store is the concrete binding point reused by R02, R06, and acknowledgment-feedback steps.
