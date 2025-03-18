class SimpleCommand():
    def __init__(open_web_ui: MessagerInterface):
        self.messager = messager
    
    def start(self):
        self.messager.send("Привет, Как дела?")
        self.messager.send("Что делаешь?")