from abc import ABC, abstractmethod


class EngineInterface(ABC):
    @abstractmethod
    def speak(self, text: str):
        ...

    @abstractmethod
    def set_volume(self, volume: int):
        ...

    @abstractmethod
    def stop(self):
        ...
