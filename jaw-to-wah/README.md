# Mouth Wah Mini — jaw-to-wah starter kit

The controller converts timestamped jaw scores into a normalized wah control. It uses only Python's standard library. Tracking, OSC transport, and audio processing belong to the integration layer.

The [evaluation scorecard](SCORECARD.md) provides the shared trial brief, scoring rubric, and results log for comparing Perplexity Search and Computer.

## Controller contract

- Set `closed` and `opened` to representative normalized jaw scores with `0 <= closed < opened <= 1`. As a starting calibration, take the median of a short stable recording at rest and the median at a comfortable open position. Repeat calibration if the readings overlap or the endpoints are too close to give a stable sweep.
- A finite numeric jaw score is clipped to the calibration interval and mapped linearly. Closed maps to 0, the midpoint to 0.5, and opened to 1 before smoothing. Values outside [0, 1] saturate through the same rule.
- `smoothing_ms` is a nonnegative time constant, default 60 ms. The first update emits its target immediately. Subsequent updates move a fraction `1 - exp(-elapsed_ms / smoothing_ms)` of the way toward the new target. Zero disables smoothing. This is control-rate smoothing.
- Pass `None` on missing tracking. It targets the configured `neutral` in [0, 1], default 0, using the same smoothing. Call the controller again as time passes to continue the return to neutral. Reacquisition resumes from the current output.
- Timestamps are strictly increasing nonnegative signed 64-bit integers in milliseconds. Duplicates, regressions, booleans, floats, strings, and out-of-range timestamps raise `ValueError`. Invalid calibration, configuration, or scores also raise `ValueError`. Rejected updates leave both the output and last accepted timestamp intact. Output stays in [0, 1].

## MediaPipe adapter proposal

**Target:** An external Windows x64 CPython 3.12 process with MediaPipe Tasks Python `mediapipe==0.10.32`, and Google's Face Landmarker float16 model revision 1. The pin is a review target. Google lists Python 3.9–3.12 for Tasks and the pinned release lists a Windows x64 wheel. [Google Python setup](https://developers.google.com/edge/mediapipe/solutions/setup_python), [pinned package files](https://pypi.org/project/mediapipe/0.10.32/#files), [Google's model reference](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker?tab=Python), [Google's sample model revision](https://github.com/google-ai-edge/mediapipe-samples-web/blob/main/src/tasks/face-landmarker.ts).

**Documented API:** Create `mp.tasks.vision.FaceLandmarker` using `mp.tasks.vision.FaceLandmarkerOptions` with the model asset path in `mp.tasks.BaseOptions`, `running_mode=mp.tasks.vision.RunningMode.VIDEO`, `num_faces=1`, and `output_face_blendshapes=True`. Pass decoded RGB frames as `mp.Image` with `mp.ImageFormat.SRGB` to `detect_for_video(image, timestamp_ms)`. This synchronous call takes increasing millisecond timestamps and returns per-face blendshape categories. Google's source identifies the category `jawOpen`. [Python guide](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker?tab=Python), [FaceLandmarker API](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/FaceLandmarker), [result API](https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/FaceLandmarkerResult), [Google's category list](https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/tasks/cc/vision/face_landmarker/face_blendshapes_graph.cc).

**Design choices:** Use the first face's category with `category_name == "jawOpen"` and pass its finite `score` to `JawControl.update`. Treat it as a relative control signal and calibrate it per player and setup. Supply `None` when the face, category, or usable score is absent. Start with prerecorded frames to check the adapter, then try webcam frames. For a webcam, use a single monotonic clock for frame and missing-sample timestamps. Skip duplicate millisecond ticks and drop frames whose capture timestamps predate the last controller update. When frames stop arriving, a periodic tick should submit `None` on the same clock. Keep controller calls serialized.

## TouchDesigner integration proposal

**Target:** TouchDesigner 2025.33230. Run tracking and the controller in the external process to separate MediaPipe's Python dependencies from TouchDesigner's embedded runtime. Derivative documents build 2025.33230 and the Python 3.11 runtime in the 2025 series. [Derivative release notes](https://docs.derivative.ca/Release_Notes/2025.30000), [Derivative Python documentation](https://docs.derivative.ca/Python).

1. In the adapter, send one OSC float per controller update to `127.0.0.1:9000` at the example address `/wah`. In TouchDesigner, add an **OSC In CHOP**, set **Network Port** to 9000, and set **Local Address** to `127.0.0.1`. Inspect the received channel before wiring anything downstream. The port and OSC address are design choices. Derivative documents the receiver and port configuration. [OSC In CHOP reference](https://docs.derivative.ca/OSC_In_CHOP), [Derivative OSC setup example](https://docs.derivative.ca/IOS_and_OSC).
2. Send 0, 0.5, and 1 from a local test sender. Verify the received values and channel name on your build, then use the channel to drive a parameter you expose in your own audio patch. Decide how the normalized sweep maps to that parameter's usable range. Test with low monitoring levels and check for audible stepping before adjusting smoothing.
3. Distinguish loss of face tracking from loss of the sender. When the process can still send messages, it should keep sending the controller's return to neutral. If the process or OSC stream stops, implement and test a separate receiver-side timeout before relying on neutral behavior during a live session.

The adapter, OSC wiring, receiver timeout, and audio mapping are proposed integration steps. The full OSC In CHOP reference returned HTTP 403 on direct retrieval. Its indexed official excerpt and Derivative's OSC setup guide provided the receiver documentation.

## Tests and remaining local checks

Executed `python -B -m unittest -v test_jaw_control` on Windows with CPython 3.12.10. **8 passed.**

| Executed test | Assertion |
|---|---|
| `test_calibration_endpoints_and_midpoint` | Closed, halfway, and open map to 0, 0.5, and 1. |
| `test_out_of_range_values_clamp` | Scores beyond calibration or the nominal normalized range saturate. |
| `test_invalid_configuration` | Invalid calibration and configuration are rejected. |
| `test_smoothing_matches_elapsed_time` | A constant target reaches the same value over one interval or two unequal intervals. |
| `test_missing_tracking_drifts_to_neutral_and_recovers` | Missing samples ease toward neutral and valid tracking resumes from that output. |
| `test_missing_tracking_without_smoothing` | Loss of tracking immediately emits the configured neutral value. |
| `test_malformed_and_non_monotonic_timestamps` | Invalid, duplicate, and backward timestamps raise without changing state. |
| `test_malformed_scores_leave_state_unchanged` | Invalid scores raise and allow a valid retry at the same timestamp. |

Local checks still required: confirm the installed package and model load, inspect real `jawOpen` output on recorded and webcam frames, verify TouchDesigner OSC reception and sender-loss handling, and measure responsiveness and audible artifacts with the local guitar and audio interface. Validation here covers the pure-Python module only.
