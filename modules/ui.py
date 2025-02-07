from tkinter import font as Font
from customtkinter import *
from os import path as Path
from tkinter import *


font : tuple = ("VCR OSD MONO", 15)

main_color : str = "#0066ff"
button_foreground_color : str = "#adadad"
button_hover_color : str = "#0052cc"

class AppWindow(CTk):
    def __init__(self, size="800x600", name="ClusteRack"):
        set_appearance_mode("light")
        super().__init__()
        self.title(name)
        self.geometry(size)
        self.iconbitmap(os.path.join("Assets","Images", "logo.ico"))
        self.resizable(True, True)
        self.configure(fg_color = "#cdcdcd")

        FontManager.load_font(Path.join("Assets","Font", "VCR_OSD_MONO_1.001.ttf"))
        

class UI:
    class Button(Button):
        def __init__(self, master : AppWindow, text : str, fg_color : str = button_foreground_color, bg_color : str = button_hover_color, **kwargs):
            super().__init__(master, 
                             text=text,
                             background="white",
                             foreground="black",
                             font=font,
                             borderwidth=6,
                             **kwargs)

    class Label(CTkLabel):
        def __init__(self, master, text, text_color=main_color, **kwargs):
            super().__init__(master, 
                             text=text, 
                             text_color=text_color, 
                             font=font, 
                             **kwargs)
