from customtkinter import *

class AppWindow(CTk):
    def __init__(self, size="800x600", name="ClusteRack"):
        set_appearance_mode("light")
        super().__init__()
        self.title(name)
        self.geometry(size)
        self.iconbitmap(os.path.join("Assets","Images", "logo.ico"))
        self.resizable(True, True)
        


class UI:
    class Button(CTkButton):
        def __init__(self, master, text, **kwargs):
            super().__init__(master, text=text,fg_color="#00c1ff", hover_color="#00a4bd", text_color="black", **kwargs)

    class Label(CTkLabel):
        def __init__(self, master, text, **kwargs):
            super().__init__(master, text=text, text_color="#00c1ff", **kwargs)
