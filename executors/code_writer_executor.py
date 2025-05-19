import code
import os
from pathlib import Path
from yandex_cloud_ml_sdk import YCloudML
from mouse_keyboard_bot import MouseKeyboardBot

class CodeWriterExecutor:
    def __init__(self, y_cloud: YCloudML, bot: MouseKeyboardBot):
        self.y_cloud = y_cloud
        self._messages = [
            {
                "role": "system",
                "text": '''
                    Тебя попросят написать код. Твой ответ не должен содержать абсолютно никаких комментариев. В твоем ответе должнен быть только код, не должно быть ни единого комментария вне кода. Твой ответ сразу будет вставлен в код, поэтому он не должен содержать даже тройных ковычек для пометки кода
                ''',
            }
        ]
        self.bot = bot
    
    def write_code(self, prompt: str, file_path: str):
        self._messages += [
            {
                "role": "user",
                "text": prompt,
            }
        ]
        result = self.y_cloud.models.completions("yandexgpt").configure(temperature=0.5).run(self._messages) #type: ignore
        self._messages += [
            {"role": "assistant", "text": result[0].text}
        ]

        result = result[0].text.replace("```", "")
        
        path = (Path.home() / "Desktop" / f"{file_path}")

        with open(path, "w") as f:
            f.write(result)

    def write_code_in_place(self, prompt: str):
        print(prompt)
        self._messages += [
            {
                "role": "user",
                "text": prompt,
            }
        ]
        result = self.y_cloud.models.completions("yandexgpt").configure(temperature=0.5).run(self._messages) #type: ignore
        self._messages += [
            {"role": "assistant", "text": result[0].text}
        ]

        result = result[0].text.replace("```", "")

        self.bot.click()
        self.bot.input(result)

        
        

    
