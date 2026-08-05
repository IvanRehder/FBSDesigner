# R05 — Report Intelligence Data (input)

**Modalities:** Touch and Keyboard

## Function
F-05.1 — Compose-and-transmit intelligence report: the HMI turns pilot-authored intelligence content (structured fields: event type, classification, coordinates, free-text observation) into a report that reaches C2. Substantive data is pilot-authored; the system auto-appends a metadata envelope (altitude, position, timestamp) automatically on send, treated as a read-only envelope rather than a pilot-authored field.

## Behaviour
Be-05.1.3 — Mixed Touch/Keyboard pathway: field selection and value entry are freely interleaved (e.g. field-pick by Touch, free-text entry by UCP keyboard, or vice versa), with a single shared validation gate checking completeness/format before a CONFIRM SEND. Mixed is the primary authoring mode, while the modality-complete redundancy rule keeps Touch-only (Be-05.1.1) and Keyboard-only (Be-05.1.2) paths implicitly satisfied so each modality can complete the task alone.

## Structure
S-05.1.3.1 — Dedicated Intel Report panel (WAD overlay) + UCP keyboard: WAD overlay form with labeled fields (event type, classification, coordinates, free-text observation); free-text/numeric fields focus by Touch OR bezel OSS field-step and entry via on-screen keyboard OR UCP alphanumeric keyboard; categorical fields Touch-cycle OR bezel rotary step; system auto-appends read-only metadata envelope (alt/pos/timestamp) on send; single validation gate then CONFIRM SEND via Touch OSS on panel AND bezel OSS (both live); gate/send result via notification strip + audio ping reusing the R02 multi-channel alert. Panel flagged as a reuse candidate for surveillance-data reporting (capability 3).
