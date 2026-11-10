# Mouth Wah Mini evaluation scorecard

Use the same brief to compare Perplexity Search and Computer on producing a reviewable jaw-to-wah starter kit. The scope is the Python control layer. Webcam, TouchDesigner, and live audio checks require local validation.

## Shared trial brief

```text
I am building Mouth Wah Mini, a TouchDesigner + Python guitar-effects
prototype exploring MediaPipe jaw tracking to control a wah effect.

Produce a minimal, reviewable jaw-to-wah control starter kit. No repository
or existing patch is supplied: do not claim to inspect or modify one.

Requirements:
1. Research current official MediaPipe and Derivative/TouchDesigner
   documentation. Cite sources next to API, compatibility, and integration
   claims. State which API path and versions your proposal targets.
2. Propose one supported way to obtain a jaw-opening signal. Separate
   documented API behavior from your own design choices.
3. Implement a pure-Python control module that accepts timestamped,
   normalized jaw values and emits a bounded normalized wah-control value.
   Include calibration, configurable smoothing, clamping, and explicit
   behavior when tracking is missing. Keep this module independent of
   MediaPipe and TouchDesigner.
4. Include automated tests for calibration endpoints, out-of-range inputs,
   smoothing behavior, missing tracking, and malformed or non-monotonic
   timestamps. Define expected behavior before testing it.
5. Provide integration notes for connecting the selected tracking API to
   the module and the module to TouchDesigner. Do not invent operators,
   parameters, or APIs. Label unverified integration steps.
6. Deliver README.md, jaw_control.py, and test_jaw_control.py as files if
   supported; otherwise provide complete, clearly labeled code blocks.
7. Report exactly which tests you executed, their results, and which checks
   require my local webcam, TouchDesigner, audio setup, or installed versions.
   Do not claim live camera or audio validation unless you performed it.

If a source or tool is unavailable, record the blocker and use an official
alternative where possible. Do not silently omit requirements. No paid
services, publishing, external writes, or repository changes.
```

## Run protocol

1. Use two fresh threads with the same brief, attachments, and permission settings.
2. In the Search trial, select Search and record the selected mode. Record whether it is basic or Pro Search.
3. Record date, plan, visible model/mode, elapsed time, Computer credits, and any manual intervention.
4. Score the initial responses before asking either product to repair them.
5. Save code blocks as files without editing them, then run both outputs in the same local environment. Treat prose test claims as claims until you reproduce them.
6. If you repeat the experiment, use fresh threads and report all runs rather than only the best output.
7. These are proposed experimental controls. They compare the products as usable systems, not isolated model intelligence.

## Scoring rubric

Give each category 0–2 points for a total of 6.

| Category | 0 points | 1 point | 2 points |
| --- | --- | --- | --- |
| Citation accuracy | Critical API claims are unsupported, contradicted, or cite fabricated sources. | Sources exist, but some claims overreach or version/integration details remain unclear. | Check five consequential claims—or all if fewer—and every cited official source supports the adjacent claim and relevant API/version. |
| Technical correctness | Code does not run, important behavior is broken, or integration relies on invented APIs. | Core code works, but edge cases, tests, or integration assumptions need repair. | Tests pass locally; boundaries, calibration, smoothing, tracking loss, and timestamps behave as specified; unverified integration is clearly labeled. |
| Deliverable usability | Missing or incomplete artifacts prevent a trial. | Recoverable with manual assembly or small undocumented fixes. | Complete files or copy-saveable blocks, clear setup and execution commands, dependency/version notes, and a workable local validation checklist. |

## Results log

| Trial | Citations /2 | Correctness /2 | Usability /2 | Total /6 | Time | Credits/cost | Manual fixes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Search | — | — | — | — | — | — | — |
| Computer | — | — | — | — | — | — | — |

Record blocking defects separately. An invented integration API, for example, should stay visible even when the total score is high.

**Hypothesis:** Search may be sufficient for a narrow, source-grounded explanation. Computer may have an advantage in assembling artifacts, executing checks, and iterating across steps. The results log is blank pending recorded trial data.
