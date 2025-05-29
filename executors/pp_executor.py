from mouse_keyboard_bot import MouseKeyboardBot


class PPExecutor:
    def __init__(self, bot: MouseKeyboardBot):
        self.bot = bot
    
    def next(self):
        self.bot.press("right")
    
    def prev(self):
        self.bot.press("left")