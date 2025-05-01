from __future__ import annotations
from yandex_cloud_ml_sdk import YCloudML

messages = [
    {
        "role": "system",
        "text": "Ты голосовой помощник, которого зовут Мел. Помоги пользователю в любых его задачах.",
    },
    {
        "role": "user",
        "text": """А как мне сделать мои уроки?????""",
    },
]


def main():
    sdk = YCloudML(
        folder_id="",
        auth="",
    )

    result = (
        sdk.models.completions("").configure(temperature=0.5).run(messages) # type: ignore
    )

    for alternative in result:
        print(alternative)


if __name__ == "__main__":
    main()