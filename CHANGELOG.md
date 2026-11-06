# Changelog

Progress notes for Finger Fuzz and its current Mouth Wah Mini prototype.

## 2026-11-06 — Audio spectrum and live captions

Added a live audio spectrum for the microphone used for speech captions.

![Audio spectrum demo](https://i.gyazo.com/238a7d869fa00c4d371178f9cf0b18e7.gif)

### Live captions

See the OBS speech captions in the [live caption demo (.mov)](Movie/live-caption-demo.mov).

Twitch channel: [xidist](https://www.twitch.tv/xidist).

### FFT wah prototype

Prototype workflow for testing the wah with a mono microphone in TouchDesigner before connecting the guitar:

1. Inside a Base COMP named `fft_wah`, route `mic_in` through an Audio Spectrum CHOP in **Time to Magnitude and Phase** mode with a 2,048-sample FFT.
2. Verify the unmodified round trip first: send magnitude and phase into a second Audio Spectrum CHOP in **Magnitude and Phase to Time** mode. Monitor the result through Audio Device Out CHOP at low gain with headphones.
3. Insert a Script CHOP between the transforms. Map a manual pedal from 0 to 1 onto a logarithmic sweep from 350 Hz to 2.2 kHz: `center_hz = 350 * (2200 / 350) ** pedal`. Multiply only the magnitude bins by a smooth peak centered at that frequency, leaving phase unchanged. For a bin frequency `f`, use `gain = 0.15 + 0.85 * exp(-0.5 * (log2(max(f, 1) / center_hz) / 0.5) ** 2)`.
4. Compare the dry and processed audio with separate Audio Spectrum CHOPs in **Visualization** mode. Send the processed spectrum through CHOP to TOP for the stream visual. Keep playback on the reconstructed audio CHOP path.
5. Sweep the pedal while making a steady “shhh” sound. Use Audio File Out CHOP to record a WAV if needed. Once the manual sweep is clean, switch the input to guitar and drive the pedal with calibrated MediaPipe `jawOpen`.

Live FFT round-trip playback and guitar tracking still need validation.

## 2026-11-05 — Mouth Wah Mini prototype

### Added

- A Python builder that creates `/project1/mouth_wah_mini` in TouchDesigner.
- MediaPipe `jawOpen` control with adjustable closed-mouth and open-mouth calibration.
- A resonant wah sweep from 350 Hz to 2.2 kHz, with a 45 ms control-smoothing time constant.
- A Script CHOP guitar-processing path with persistent filter state and duplicated mono output for stereo playback.
- An OpenCV preview with a jaw score, target-frequency readout, and pedal-position meter.
- Manual Pedal control for testing the effect before connecting face tracking.
- Optional face-presence input to fade the effect back to dry when tracking is lost.
- Setup instructions for webcam tracking and Vetco USB-C guitar input and monitoring.
- A README with a Mermaid diagram of the vision, control, and guitar-audio paths.

### Changed

- Moved the interaction from a thumb–index pinch controlling fuzz to jaw opening controlling wah, freeing both hands for guitar playing.

### Repository progress

- Published the project to the public `xidist/mini-finger-fuzz` repository.
- Configured Git LFS for `.toe` project files and uploaded project snapshots and backups.
- Added `.gitkeep` placeholders to preserve the Audio, Chan, Geo, Image, and Movie folders when cloning.

### Validation and current status

- Ran the builder in TouchDesigner on Windows after correcting the quoted file path in Textport.
- Development environment reported as TouchDesigner 2025.32820 with Python 3.11.10.
- Checked jaw mapping, manual control, frequency response, stereo output, and the dry fade using simulated inputs.
- Live webcam calibration, OpenCV preview rendering, Vetco routing, and end-to-end playing latency still need verification on the laptop.

### Next session

- Confirm the `jawOpen` channel responds in the MediaPipe face-tracking blend-shape CHOP.
- Connect Jaw CHOP and Camera TOP, then calibrate a comfortable mouth movement.
- Select the guitar input and playback devices and test the sweep while playing.
- Save the configured `.toe` and capture a short demonstration.

If the tracker sends zero jaw scores on face loss and no face-presence input is connected, the wah settles at the closed-mouth end of the sweep.
