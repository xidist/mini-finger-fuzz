"""Mouth Wah Mini | TouchDesigner Textport builder.

1. Open your MediaPipe demo .toe. On MediaPipe, select your webcam, enable
   Face Tracking and enable Blend Shapes if your build exposes that switch.
   Set Max Faces to 1 if available. In face_tracking, find the blend-shape
   CHOP output and verify that its jawOpen channel responds to your mouth.
2. Paste this as ONE line in Dialogs > Textport, adjusting the file path:
   exec(compile(open(r'C:/Users/you/Downloads/Mouth_Wah_Mini_Builder.py', encoding='utf-8').read(), 'Mouth_Wah_Mini_Builder.py', 'exec'))
3. Select /project1/mouth_wah_mini. On its Mouth Wah page set Jaw CHOP to
   the blend-shape CHOP (or a Null CHOP connected to that output). Set Jaw
   Channel if its name differs. Set Camera TOP to the MediaPipe video TOP
   to see the OpenCV meter at OUT_VIDEO.
4. Watch the raw jaw score on OUT_VIDEO with your mouth comfortably closed
   and open. Set Jaw Closed and Jaw Open to those values. The defaults are
   0.04 and 0.55. If your tracker offers a one-sample 0/1 face-present CHOP,
   set Face Present CHOP and Face Present Channel for dry audio on face loss.
   Without that optional gate, a tracker that sends zeros on face loss will
   park the wah at the closed-mouth end of the sweep.
5. Plug the guitar into the Vetco 1/4-inch input and the Vetco into USB-C.
   Select the Vetco recording device in guitar_in. Set Guitar Channel to
   the live input index (zero-based) if you are getting a silent channel.
6. Select your playback device in speakers. Turn down Volume and then
   enable Active. If the Vetco headphone jack offers playback in Windows,
   you can select it here. A direct monitor may also mix in dry guitar.
   If reusing a .toe with Finger Fuzz, turn off its speakers CHOP first.
7. Move your jaw to sweep dark to bright while playing. With Jaw CHOP
   empty, sweep Manual Pedal to test the wah. Save As a new .toe.

If the video plays without the meter, run import cv2; print(cv2.__version__)
in the Textport. Audio uses NumPy and works independently of the overlay.
"""


CONTROL = '''
import math


def read_channel(chop, name):
    if chop is None or not chop.numSamples:
        return None
    for channel in chop.chans():
        if channel.name == name:
            value = float(channel[0])  # first face / first sample
            return value if math.isfinite(value) else None
    return None


def pedal(base):
    par = base.par
    jaw = par.Jawchop.eval()
    if jaw is None:
        return par.Manualpedal.eval(), True, None

    raw = read_channel(jaw, par.Jawchannel.eval())
    presence = par.Presencechop.eval()
    if presence is not None:
        present = read_channel(presence, par.Presencechannel.eval())
        if present is None or present < 0.5:
            return 0.0, False, raw
    if raw is None:
        return 0.0, False, None

    low, high = par.Jawclosed.eval(), par.Jawopen.eval()
    position = (raw - low) / max(0.01, high - low)
    return min(1.0, max(0.0, position)), True, raw


def frequency(position):
    return 350.0 * (2200.0 / 350.0) ** position
'''


VIDEO = '''
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None


def onCook(scriptOp):
    base = scriptOp.parent()
    camera = base.par.Cameratop.eval()
    if camera is None:
        scriptOp.copyNumpyArray(np.zeros((270, 480, 3), dtype=np.uint8))
        return
    pixels = camera.numpyArray(delayed=True)
    if pixels is None:
        return

    # Convert TouchDesigner's bottom-up float image to top-down RGB bytes.
    frame = np.ascontiguousarray(
        (np.clip(pixels[::-1, :, :3], 0, 1) * 255).astype(np.uint8)
    )
    if cv2 is not None:
        control = base.op('pedal_control').module
        position, active, raw = control.pedal(base)
        label = 'BYPASS' if not active else '%d Hz' % control.frequency(position)
        if raw is not None:
            label += '  jaw %.2f' % raw
        cv2.putText(frame, 'MOUTH WAH  ' + label, (12, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        end = min(212, frame.shape[1] - 1)
        if active and end > 12 and frame.shape[0] > 46:
            cv2.rectangle(frame, (12, 37), (end, 46), (70, 70, 70), -1)
            fill = 12 + round((end - 12) * position)
            cv2.rectangle(frame, (12, 37), (fill, 46), (80, 255, 195), -1)
    scriptOp.copyNumpyArray(np.ascontiguousarray(frame[::-1]))


cook = onCook
'''



AUDIO = '''
import math
import numpy as np


def onCook(scriptOp):
    source = scriptOp.inputs[0]
    base = scriptOp.parent()
    scriptOp.clear()
    scriptOp.rate = source.rate
    if not source.numChans or not source.numSamples:
        return

    index = min(max(0, int(base.par.Guitarchannel.eval())), source.numChans - 1)
    dry = source.numpyArray()[index].tolist()
    rate = source.rate
    control = base.op('pedal_control').module
    target, active, _ = control.pedal(base)
    z1, z2, position, wet, last_rate, last_index = scriptOp.fetch(
        'wah_state', (0.0, 0.0, target, 0.0, rate, index)
    )
    if rate != last_rate or index != last_index:
        z1, z2, position, wet = 0.0, 0.0, target, 0.0

    # Smooth the jaw input over 45 ms. Crossfade to dry on tracking loss.
    smoothing = 1.0 - math.exp(-len(dry) / (rate * 0.045))
    position += smoothing * (target - position)
    wet_target = 0.88 if active else 0.0
    wet_end = wet + smoothing * (wet_target - wet)
    wet_step = (wet_end - wet) / len(dry)

    # Two-integrator state-variable bandpass. Preserve state across slices.
    hz = min(control.frequency(position), rate * 0.4)
    g = math.tan(math.pi * hz / rate)
    damping = 1.0 / 2.2
    a1 = 1.0 / (1.0 + g * (g + damping))
    a2 = g * a1
    a3 = g * a2
    output = []
    for sample in dry:
        v3 = sample - z2
        band = a1 * z1 + a2 * v3
        low = z2 + a2 * z1 + a3 * v3
        z1 = 2.0 * band - z1
        z2 = 2.0 * low - z2
        wet += wet_step
        output.append(sample + wet * (band * damping - sample))

    scriptOp.store('wah_state', (z1, z2, position, wet_end, rate, index))
    mono = np.clip(np.asarray(output, dtype=np.float32), -1.0, 1.0)
    scriptOp.copyNumpyArray(np.stack((mono, mono)), baseName='out')


cook = onCook
'''


def build():
    network = op('/project1')
    if network is None:
        raise RuntimeError('Create or open a TouchDesigner project with /project1.')
    existing = network.op('mouth_wah_mini')
    if existing is not None:
        print('Already exists:', existing.path)
        return

    base = network.create(baseCOMP, 'mouth_wah_mini')
    try:
        page = base.appendCustomPage('Mouth Wah')
        page.appendTOP('Cameratop', label='Camera TOP')
        page.appendCHOP('Jawchop', label='Jaw CHOP')
        page.appendStr('Jawchannel', label='Jaw Channel')[0].val = 'jawOpen'
        page.appendCHOP('Presencechop', label='Face Present CHOP')
        page.appendStr('Presencechannel', label='Face Present Channel')[0].val = 'present'
        page.appendFloat('Jawclosed', label='Jaw Closed')[0].val = 0.04
        page.appendFloat('Jawopen', label='Jaw Open')[0].val = 0.55
        manual = page.appendFloat('Manualpedal', label='Manual Pedal')[0]
        manual.min, manual.max = 0, 1
        manual.clampMin, manual.clampMax = True, True
        manual.normMin, manual.normMax = 0, 1
        page.appendInt('Guitarchannel', label='Guitar Channel')

        def make(kind, name, x, y):
            node = base.create(kind, name)
            node.nodeX, node.nodeY = x, y
            return node

        def connect(source, destination):
            destination.inputConnectors[0].connect(source)

        make(textDAT, 'START_HERE', 0, 450).text = __doc__
        make(textDAT, 'pedal_control', 210, 450).text = CONTROL
        video_code = make(textDAT, 'overlay_code', 410, 450)
        video_code.text = VIDEO
        audio_code = make(textDAT, 'wah_code', 620, 450)
        audio_code.text = AUDIO

        overlay = make(scriptTOP, 'opencv_overlay', 0, 220)
        overlay.par.callbacks = video_code.path
        preview = make(nullTOP, 'OUT_VIDEO', 210, 220)
        connect(overlay, preview)

        guitar = make(audiodeviceinCHOP, 'guitar_in', 0, 0)
        effect = make(scriptCHOP, 'mouth_wah', 210, 0)
        effect.par.callbacks = audio_code.path
        effect.par.timeslice = True
        connect(guitar, effect)
        speakers = make(audiodeviceoutCHOP, 'speakers', 420, 0)
        speakers.par.active = False
        speakers.par.volume = 0.15
        connect(effect, speakers)
    except Exception:
        base.destroy()
        raise
    print('Built', base.path, '| Open START_HERE inside the Base.')


build()
