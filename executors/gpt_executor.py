from yandex_cloud_ml_sdk import YCloudML


class GPTExecutor:
    def __init__(self, y_cloud: YCloudML):
        self.y_cloud = y_cloud
        self._messages = [
            {
                "role": "system",
                "text": "Ты голосовой помощник, которого зовут Мел. Помоги пользователю в любых его задачах.",
            }
        ]

    def run(self, prompt: str) -> str:
        if len(prompt.strip()) == 0:
            return ""
        self._messages += [
            {
                "role": "user",
                "text": prompt,
            }
        ]
        result = (
            self.y_cloud.models.completions("yandexgpt").configure(temperature=0.5).run(self._messages) #type: ignore
        )
        self._messages += [
            {"role": "assistant", "text": result[0].text}
        ]
        return result[0].text