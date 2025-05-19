# import pyttsx4
# # only coqui_ai_tts engine support cloning voice.
# engine = pyttsx4.init('coqui_ai_tts')
# engine.setProperty('speaker_wav', './docs/i_have_a_dream_10s.wav')

# engine.say('this is an english text to voice test, listen it carefully and tell who i am.')
# engine.runAndWait()

# from main import start_assistant


# assist = start_assistant()

from yandex_cloud_ml_sdk import YCloudML
import os
from executors.code_writer_executor import CodeWriterExecutor
from mouse_keyboard_bot import MouseKeyboardBot
bot = MouseKeyboardBot()

folder_id = os.getenv("YANDEX_FOLDER_ID")
auth_token = os.getenv("YANDEX_AUTH_TOKEN")
if folder_id is None or auth_token is None:
    raise Exception("YANDEX_FOLDER_ID or YANDEX_AUTH_TOKEN is not set")
y_cloud = YCloudML(
    folder_id=folder_id,
    auth=auth_token
)

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]


code_writer = CodeWriterExecutor(y_cloud, bot)
code_writer.write_code_in_place("напиши код функции сортировки пузырьком на python тут")