import pyttsx3
from engines.iengine import EngineInterface


class PyttsxEngine(EngineInterface):
    def __init__(self, engine: pyttsx3.Engine):
        self.engine = engine

    def speak(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()

    def set_volume(self, volume: int):
        self.engine.setProperty("volume", volume)

    def stop(self):
        self.engine.stop()
