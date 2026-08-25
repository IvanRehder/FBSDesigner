# R02 — Notify Autopilot Reached (output)

**Modalities:** Screen and Audio-out

## Function
F-02.1 (state-change confirmation) + F-02.2 (attention redirection): Close the loop on the pilot's autopilot command by signalling the discrete transition from commanded/capturing to target achieved, giving positive confirmation that the requested ALT/HDG/SPD condition is now true (F-02.1); and reclaim the pilot's attention from competing tasks at the moment capture completes so they need not poll autopilot state (F-02.2).

## Behaviour
Be-02.3 (Mixed pathway, serves F-02.1 and F-02.2): On capture, simultaneous audible ping + panel state-change cue + text notification line. Audio reclaims attention (F-02.2); the pilot's gaze lands on the panel/notification indication that states and localizes the reached target (F-02.1). Be-02.1 (Screen-only) and Be-02.2 (Audio-only) retained as degraded-channel fallbacks per output redundancy rule, each independently sufficient to receive the notification.

## Structure
S-02.1.2.3.2 (Notification-strip + audio, decoupled from R01): (1) Dedicated notification strip — new WAD overlay layer in a common alerts/status region rendering 'AUTOPILOT TARGET REACHED — [params]', persistent until superseded/acknowledged; explicitly the reusable notification channel for future alert requirements. (2) R01 panel light cue — field border/color change on the active target field, providing target-specific confirmation and reusing R01 structure. (3) Audio-out capture ping (+ optional TTS) — shared reusable audio-alert tone, distinct from caution/warning tones.
