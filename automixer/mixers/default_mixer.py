import random

from pydub import AudioSegment
from tqdm import tqdm

from automixer.effects.band_pass import band_pass_filer
from automixer.effects.change_tempo import change_audioseg_tempo
from automixer.iterators.rolling_window import rolling_window
from automixer.utils import calculate_step


def _create_chunk(config, window):
    chunk = AudioSegment.silent(duration=config.sample_length)
    for channel in config.channels_config:
        start_cut = random.choice(window)
        channel_chunk = config.audio[start_cut: start_cut + config.sample_length]
        channel_chunk = band_pass_filer(channel.low_pass, channel.high_pass, channel_chunk)
        chunk = chunk.overlay(channel_chunk)
    if config.sample_speed != 1.0:
        chunk = change_audioseg_tempo(chunk, config.sample_speed, verbose=config.is_verbose_mode_enabled)

    return chunk


class RandomWindowAutoMixer:
    def mix(self, config):
        mix = AudioSegment.empty()
        pbar = tqdm(desc="Mixing")
        chunk_length_in_window = calculate_step(config.beats)
        for window in rolling_window(config.beats, config.window_divider):
            chunk1 = _create_chunk(config, window)
            while len(chunk1) < int(chunk_length_in_window):
                chunk = _create_chunk(config, window)
                chunk1 = chunk1.append(chunk, crossfade=0)
            mix = mix.append(chunk1, crossfade=0)
            pbar.update(len(mix))
        return mix

# amc ss 0.5 s 1.5 c 1,250;500,15000 w 6
# amc ss 2.0 s 0.5 c 1,250;10000,15000
# amc ss 2.0 s 0.5 c 1,250;251,300;400,500;501,600;60,700;10000,15000
