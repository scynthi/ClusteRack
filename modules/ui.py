from tkinter import font as Font
from customtkinter import *
from os import path as Path

font : tuple = ("VCR OSD MONO", 14)


class AppWindow(CTk):
    def __init__(self, size="800x600", name="ClusteRack"):
        set_appearance_mode("light")
        super().__init__()
        self.title(name)
        self.geometry(size)
        self.iconbitmap(os.path.join("Assets","Images", "logo.ico"))
        self.resizable(True, True)

        FontManager.load_font(Path.join("Assets","Font", "VCR_OSD_MONO_1.001.ttf"))
        

class UI:
    class Button(CTkButton):
        def __init__(self, master, text, **kwargs):
            super().__init__(master, text=text,fg_color="#00c1ff", hover_color="#00a4bd", text_color="black", font=font, **kwargs)

    class Label(CTkLabel):
        def __init__(self, master, text, text_color="#00c1ff", **kwargs):
            super().__init__(master, text=text, text_color=text_color, font=font, **kwargs)
