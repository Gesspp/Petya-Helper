import sounddevice as sd
import torch, time
from engines.iengine import EngineInterface


class SDEngine(EngineInterface):

    def __init__(self, speaker: str = "baya", device: str = "cpu", samplerate: int = 48_000):
        self.__MODEL__, _ = torch.hub.load( # type: ignore
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language="ru",
            speaker="ru_v3"
        )
        self.__MODEL__.to(torch.device(device))

        self.__SPEAKER__ = speaker
        self.__SAMPLERATE__ = samplerate

    def speak(self, text: str):
        audio = self.__MODEL__.apply_tts(
            text=text,               
            speaker=self.__SPEAKER__,
            sample_rate=self.__SAMPLERATE__, 
            put_accent=True,
            put_yo=True
        )

        # проигрываем то что получилось
        sd.play(audio, samplerate=self.__SAMPLERATE__)
        time.sleep((len(audio)/self.__SAMPLERATE__))
        sd.stop()

    def set_volume(self, volume: int):
        sd.default.device[1].volume = volume # type: ignore

    def stop(self):
        sd.stop()

    def wait(self):
        sd.wait()