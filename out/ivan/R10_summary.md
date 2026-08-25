# R10 — Command Takeover (input)

**Modalities:** Touch and Keyboard

## Function
F-10.1 — Execute the takeover command (commit to assume control): give the pilot a means to command the takeover procedure once the request acknowledgment is received, turning a granted request into an active control transfer by commanding connection with the UAV and assuming control (UC 4.2.2–4.2.3).

## Behaviour
Be-10.1.1 — Single deliberate one-shot commit, state-gated on takeover-request confirmation: the COMMAND TAKEOVER affordance is inert/disabled until the R09 request acknowledgment is received (delivered via R08); once confirmed, the affordance becomes active and a single action (Touch tap or Keyboard bezel OSS press) transmits the takeover command (4.2.2–4.2.3). No separate confirm step — the prior acknowledgment is the gate. Each modality independently completes the full commit.

## Structure
S-10.1.1.1 — Dedicated COMMAND TAKEOVER button: co-located with the R08 confirmation delivery (pop-up / messages-tab entry); Touch = single tap on WAD button, Keyboard = mapped bezel OSS press; rendered inert/greyed until R08 request-acknowledged event, active on ack, reverts after commit/timeout/link-loss; fastest lowest-workload commit. S-10.1.1.2 — Option-ring segment: R09 press-and-hold radial option ring on the UAV glyph (Map / UAV list) extended with a COMMAND TAKEOVER segment; Touch = press-and-hold on UAV → ring opens → select segment → release to commit, Keyboard = bezel rotary selects segment + OSS confirm; segment appears/enables only post-ack for that UAV; spatial/in-context commit. S-10.1.1.3 — UAV detail panel row: COMMAND TAKEOVER row within the selected-UAV detail panel; Touch = tap row, Keyboard = bezel rotary to focus row + OSS activate; row disabled until ack for that UAV, enabled post-ack; context-explicit commit that guards against wrong-UAV selection. Common: all three are the same takeover-command action, gated by the R08 request-acknowledged state, each independently modality-complete (Touch alone or Keyboard alone), all reused and extended from R09 surfaces with the post-ack COMMAND TAKEOVER state as a shared lifecycle control.
