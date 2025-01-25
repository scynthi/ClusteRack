from customtkinter import *


class UI:
    class Button(CTkButton):
        def __init__(self, master, text, **kwargs):
            super().__init__(master, text=text,fg_color="#00c1ff", hover_color="#00a4bd", text_color="black", **kwargs)

    class Label(CTkLabel):
        def __init__(self, master, text, **kwargs):
            super().__init__(master, text=text, text_color="#00c1ff", **kwargs)
