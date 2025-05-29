import threading
from setuptools import Command
from engines.iengine import EngineInterface
from executors import SystemExecutor, WordExecutor, GoogleSearchExecutor, TelegramExecutor, SteamExecutor, GPTExecutor, DNDExecutor, TileManager, CodeWriterExecutor
import speech_recognition as sr
from json import load, dump
from typing import List
import pyttsx4
from errors import ProgramNotFoundError
import pygame, os
from utils import get_path
import time
import re

class Assistant:

    def __init__(
            self, 
            engine: EngineInterface, 
            recognizer: sr.Recognizer,
            system_executor: SystemExecutor,
            word_executor: WordExecutor,
            search_executor: GoogleSearchExecutor,
            telegram_executor: TelegramExecutor,
            steam_executor: SteamExecutor,
            gpt_executor: GPTExecutor,
            dnd_executor: DNDExecutor,
            tile_exec: TileManager,
            code_exec: CodeWriterExecutor
        ) -> None:
        self.engine = engine
        self.recognizer = recognizer
        self.system_executor = system_executor
        self.word_executor = word_executor
        self.search_executor = search_executor
        self.telegram_executor = telegram_executor
        self.steam_executor = steam_executor
        self.gpt_executor = gpt_executor
        self.dnd_executor = dnd_executor
        self.tile_exec = tile_exec
        self.code_exec = code_exec
        self._load_scommands("supercommands.json")
    
        self.speaking_thread = None
        self.is_running = False
        self._lock = threading.Lock()

        self.speaking = False
        self.listening = False

        self.is_waiting = False
        self.is_dnd = False
        self.working = False

        self._keywords = {
            "документ" : self._open_document, 
            "открой" : self.open_router, # done
            "закрой" : self._close_program, # done
            "выключи" : self._shutdown, # done
            "создай папку": self._create_folder, # done
            "громкость" : self._set_volume, # done
            "загугли" : self._search, # done
            "найди": self._youtube_search, #done
            "напиши в тг": self._telegram_write, #done
            "давай поиграем": self.dnd_start,
            "поставь": self.TileMangerRatio,
            "напиши код": self.code_write
            # "включи режим диалога": ...
        }
        pygame.init()

    def get_status(self) -> dict:
        return {"speaking": self.speaking, "listening": self.listening}

    def get_settings(self) -> dict:
        return {
            "programs" : self.system_executor.programs,
            "sites" : self.search_executor.sites,
            "supercommands" : self.scommands
        }


    def wait_for_command(self):
        while True:
            phrase = self.listen()
            
            if 'петя' in phrase.lower():
                self.is_waiting = True
                return
            
            
    def run(self):
        while True:
            # if self.is_waiting:
                self.wait_for_command()
                self.play_sound("./sounds/signal.wav")
                self.start()

    def start(self):
        self.speak("Слушаю")
        self.working = True
        while self.working:
            command = self.listen()
            if not command:
                continue
            if any(word in command for word in ("стоп", "выход", "отдыхай")):
                self.speak("Ушел")
                self.working = False
                return
            self.execute_command(command)
        print("Я вышел", self.working, self.is_running)

        
    def stop(self):
        self.working = False
        self.stop_speaking()

    def speak(self, text):
        def _speak():
            with self._lock:
                print("Начинаю говорить:", text)
                self.engine.speak(text)
                self.engine.wait()
                print("Закончил говорить")
        
        self.stop_speaking()  # <- теперь не блокирует
        self.speaking_thread = threading.Thread(target=_speak)
        self.speaking_thread.start()

    def stop_speaking(self):
        print("stop_speaking called")
        if self.speaking_thread:
            print("speaking_thread is_alive:", self.speaking_thread.is_alive())
        self.engine.stop()
        print("engine.stop() called")

    def listen(self):
        if not self.listening:
            print("Слушаю...")
            self.listening = True

            # Замер времени начала всей операции
            start_total_time = time.time()
            
            # Этап 1: Настройка микрофона и запись аудио
            start_record_time = time.time()
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5) #type: ignore
                audio = self.recognizer.listen(
                    source
                )
            end_record_time = time.time()
            record_duration = end_record_time - start_record_time
            print(f"🔊 Запись аудио: {record_duration:.2f} сек")

            # Этап 2: Распознавание речи
            start_recognition_time = time.time()
            try:
                command = self.recognizer.recognize_google(audio, language="ru-RU") #type: ignore
                print(f"Вы сказали: {command}")
                self.listening = False
            except sr.UnknownValueError:
                self.speak("Извините, я не понял.")
                self.listening = False
                command = ""
            except sr.RequestError:
                self.speak("Ошибка подключения к сервису распознавания.")
                self.listening = False
                command = ""
            end_recognition_time = time.time()
            recognition_duration = end_recognition_time - start_recognition_time
            print(f"🔍 Распознавание речи: {recognition_duration:.2f} сек")

            # Общее время выполнения
            end_total_time = time.time()
            total_duration = end_total_time - start_total_time
            print(f"⏱ Общее время выполнения: {total_duration:.2f} сек")

            return command.lower() if command else ""
        return ""
    
    def set_volume(self, volume: int):
        self.engine.set_volume(volume)
    
    def dnd_next(self, command):
        while self.is_dnd:
            prompt = self.listen()
            ans = self.dnd_executor.run(prompt)
            self.speak(ans)
            if prompt == "стоп":
                self.is_dnd = False

    def dnd_start(self, command):
        self.speak(self.dnd_executor.start())
        self.is_dnd = True
        self.dnd_next(command)

    def code_write(self, command):
        print("code_write", command)
        file_path = ""
        if "тут" in command:
            self.code_exec.write_code_in_place(command)
            return
        elif "файл" in command:
            prompt = " ".join(command.split()[:-3])
            idx = command.find("файл")
            file_path = command[idx + 5:]
            self.code_exec.write_code(prompt, file_path)
        self.speak("Код записан")

    def _telegram_write(self, command: str):
        self.system_executor.execute("open", "telegram")
        getter = command.split()[-1]
        message = " ".join(command.split()[1:-1])
        self.telegram_executor.send_message_to(getter, message)

    def delete_program(self, program_name: str):
        self.system_executor.remove_program(program_name)

    def delete_site(self, site_name: str):
        self.search_executor.remove_site(site_name)

    def get_ratio(self, command):
        ratios = list(map(int, re.findall(r'\d+', command)))
        return ratios
            
    def TileMangerRatio(self, command):
        ratio = self.get_ratio(command)
        print(ratio)

        command_words = command.split(" ")
        prg1, prg2 = command_words[1], command_words[3]
        self.system_executor.execute("open", prg1)
        self.system_executor.execute("open", prg2)
        print(prg1, prg2)

        self.tile_exec.tile_windows(prg1, prg2, ratio)

    def delete_scommand(self, scommand_name: str):
        self._load_scommands("supercommands.json")
        del self.scommands[scommand_name]
        with open("supercommands.json", "w", encoding="utf-8") as file:
            dump(self.scommands, file, separators=(",\n", ": "))

    def add_program_to_list(self, program_name: str, program_path: str):
        self.system_executor.add_program(program_name, program_path)

    def add_site_to_list(self, site_name: str, site_url: str):
        self.search_executor.add_sites(site_name, site_url)

    def add_scommand_to_list(self, scommand_name: str, subcommands: List[str]):
        self._load_scommands("supercommands.json")
        self.scommands[scommand_name] = subcommands
        with open("supercommands.json", "w", encoding="utf-8") as file:
            dump(self.scommands, file, separators=(",\n", ": "))

    def edit_program(self, program_name: str, new_name: str, new_path: str):
        self.system_executor.edit_program(program_name, new_name, new_path)

    def edit_site(self, site_name: str, new_name: str, new_url: str):
        self.search_executor.edit_site(site_name, new_name, new_url)

    def edit_scommand(self, scommand_name: str, new_name: str, new_subcommands: List[str]):
        self._load_scommands("supercommands.json")
        self.scommands[new_name] = new_subcommands
        if scommand_name != new_name:
            del self.scommands[scommand_name]
        with open("supercommands.json", "w", encoding="utf-8") as file:
            dump(self.scommands, file, separators=(",\n", ": "))

    def execute_command(self, command: str):
        self._load_scommands("supercommands.json")
        print("execute_command", command)
        for keyword in self._keywords:
            if keyword in command:
                self._keywords[keyword](command)
                return
        for scm in self.scommands.keys():
            if scm.lower() in command:
                self.use_scommand(scm)
                return
        gpt_answer = self.gpt_executor.run(command)
        print("gpt_answer", gpt_answer)
        self.speak(gpt_answer)

    def open_router(self, command: str):
        programs = self.system_executor.programs
        sites = self.search_executor.sites
        command = command.lower()
        value = " ".join(command.split()[1:])
        print(value)

        for program in programs:
            if value == program:
                self.system_executor.execute("open", program)
                self.speak(f"Открываю {program}")
                return
        for site in sites:
            if value == site:
                self.search_executor.open_link(site)
                self.speak(f"Открываю {site}")
                return

        self.speak(f"Я не нашел {value}")


    def _load_scommands(self, config_file: str="supercommands.json"):
        if not os.path.exists(config_file):
            with open(config_file, "w", encoding="utf-8") as file:
                dump({}, file, separators=(",\n", ": "))
        with open(config_file, "r", encoding="utf-8") as file:
            commands = load(file)
            print("Суперкоманды загружены!", commands)
            self.scommands = commands

    def use_scommand(self, command: str):
        print("Использую команду", command)
        subcommands = self.scommands[command]

        for subcommand in subcommands:
            self.execute_command(subcommand)
        

    def _youtube_search(self, command: str):
        querry = command.split()[1:]
        query = " ".join(querry)
        self.search_executor.youtube_search(query)


    def play_sound(self, sound_file="signal.mp3"):
        sound_file = get_path(sound_file)
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

    def _search(self, command: str):
        if len(command.split()) < 2:
            self.speak("что ищем?")
            query = self.listen()
        else:
            query = " ".join(command.split()[1:])
        self.search_executor.open_search(query)

    def _open_link(self, command: str):
        if len(command.split()) < 3:
            self.speak("какую ссылку открывать?")
            link = self.listen()
        else:
            link = " ".join(command.split()[2:])
        self.search_executor.open_link(link)

    def _open_program(self, command: str):
        try:
            program = " ".join(command.split()[1:])
            self.system_executor.execute("open", program)
            self.speak(f"Открываю {program}")
        except ProgramNotFoundError as e:
            self.speak(str(e))

    def _close_program(self, command: str):
        program = " ".join(command.split()[1:])
        self.system_executor.execute("close", program)
        self.speak(f"закрываю {program}")

    def _shutdown(self, command: str):
        self.system_executor.execute("shutdown")

    def _create_folder(self, command: str):
        if len(command.split()) < 3:
            self.speak("как назовем папку?")
            folder_name = self.listen()
        else:
            folder_name = " ".join(command.split()[2:])
        self.system_executor.execute("create_folder", folder_name)
        self.speak(f"создал папку {folder_name}")

    def _set_volume(self, command: str):
        if len(command.split()) < 2:
            self.speak("какую громкость поставить?")
            volume = int(self.listen())
        else:
            volume = int(command.split()[1])
        self.system_executor.execute("set_volume", volume)
    
    
    def _open_document(self, command: str):
        if "открой" in command:
            if len(command.split()) < 3:
                self.speak("как назовем документ?")
                file_name = self.listen()
            else:
                file_name = " ".join(command.split()[2:])
            self.word_executor.execute("open_document", file_name)
            self.speak("открываю документ")
        elif "создай" in command:
            if len(command.split()) < 3:
                self.speak("как назовем документ?")
                file_name = self.listen()
            else:
                file_name = " ".join(command.split()[3:])
            self.word_executor.execute("new_document", file_name)
            self.speak("создал документ")   
        elif "напиши" in command:
            self.speak("Что написать в документ?")
            text = self.listen()
            self.word_executor.execute("new_paragraph", text)
            self.speak("Написал")
        elif "покажи" in command:
            self.speak("Какой документ показать?")
            file_name = self.listen()
            self.word_executor.execute("show_document", file_name)
            self.speak("Показал")


    def check_empty_settings(self):
        """Возвращает True, если в файле настроек нет ни одной программы или сайта"""
        return (len(self.system_executor.programs) == 0 and len(self.search_executor.sites) == 0)
    