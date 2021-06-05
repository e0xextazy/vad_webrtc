import wave
import webrtcvad

DEFAULT_PARAMS_OF_WEBRTC_ALG = {
    'Min_Silence': 0.2, 'Min_Speech': 0.1, 'Comp_Ratio': 2}
FRAME_DURATION = 0.01


def is_file_correct(file_name):
    fp = wave.open(file_name, 'r')
    try:
        assert fp.getnchannels() == 1
        assert fp.getsampwidth() == 2
        assert fp.getframerate() == 8000
    except AssertionError:
        return False
    finally:
        fp.close()
    return True


def load_sound(file_name):
    fp = wave.open(file_name, 'rb')
    sampling_frequency = fp.getframerate()
    sound_data = fp.readframes(fp.getnframes())
    fp.close()
    del fp
    return sound_data, sampling_frequency


def smooth_spoken_frames(spoken_frames, min_frames_in_silence, min_frames_in_speech):
    n_frames = len(spoken_frames)
    prev_speech_pos = -1
    for frame_ind in range(n_frames):
        if spoken_frames[frame_ind]:
            if prev_speech_pos >= 0:
                if (prev_speech_pos + 1) < frame_ind:
                    spoken_frames[(prev_speech_pos + 1):frame_ind] = [True] * \
                        (frame_ind - prev_speech_pos - 1)
            prev_speech_pos = frame_ind
        else:
            if prev_speech_pos >= 0:
                if (frame_ind - prev_speech_pos) > min_frames_in_silence:
                    prev_speech_pos = -1
    if prev_speech_pos >= 0:
        if (prev_speech_pos + 1) < n_frames:
            spoken_frames[(prev_speech_pos + 1):n_frames] = [True] * \
                (n_frames - prev_speech_pos - 1)
    speech_start = -1
    for frame_ind in range(n_frames):
        if spoken_frames[frame_ind]:
            if speech_start < 0:
                speech_start = frame_ind
        else:
            if speech_start >= 0:
                if (frame_ind - speech_start) >= min_frames_in_speech:
                    yield (speech_start, frame_ind)
                speech_start = -1
    if speech_start >= 0:
        if (n_frames - speech_start) >= min_frames_in_speech:
            yield (speech_start, n_frames)


def detect_spoken_frames_with_webrtc(sound_data, sampling_frequency, params=DEFAULT_PARAMS_OF_WEBRTC_ALG):
    assert sampling_frequency == 8000, 'Sampling frequency is inadmissible!'
    n_data = len(sound_data)
    assert (n_data > 0) and ((n_data % 2) == 0), 'Sound data are wrong!'
    frame_size = int(round(FRAME_DURATION * float(sampling_frequency)))
    sound_duration = (n_data - 2.0) / (2.0 * float(sampling_frequency))
    n_frames = int(round(n_data / (2.0 * float(frame_size))))
    spoken_frames = [False] * n_frames
    buffer_start = 0
    vad = webrtcvad.Vad(mode=params['Comp_Ratio'])
    for frame_ind in range(n_frames):
        if (buffer_start + frame_size * 2) <= n_data:
            if vad.is_speech(sound_data[buffer_start:(buffer_start + frame_size * 2)],
                             sample_rate=sampling_frequency):
                spoken_frames[frame_ind] = True
        buffer_start += (frame_size * 2)
    del vad
    min_frames_in_silence = int(
        round(params['Min_Silence'] * float(sampling_frequency) / frame_size))
    if min_frames_in_silence < 0:
        min_frames_in_silence = 0
    min_frames_in_speech = int(
        round(params['Min_Speech'] * float(sampling_frequency) / frame_size))
    if min_frames_in_speech < 0:
        min_frames_in_speech = 0
    for cur_speech_frame in smooth_spoken_frames(spoken_frames, min_frames_in_silence, min_frames_in_speech):
        init_time = cur_speech_frame[0] * FRAME_DURATION
        fin_time = cur_speech_frame[1] * FRAME_DURATION
        if fin_time > sound_duration:
            fin_time = sound_duration
        yield (int(1000 * init_time), int(1000 * fin_time))


def Vad(file_name):
    sd, sf = load_sound(file_name)
    bounds_of_speech = list(detect_spoken_frames_with_webrtc(sd, sf))
    return bounds_of_speech
