from customtkinter import *
from tkinter import *
from modules.ui import UI, AppWindow
from modules.audio_manager import AudioManager

app : AppWindow = AppWindow("800x400")
content : Frame = app.content

center_frame: CTkFrame = CTkFrame(content)
center_frame.grid(column=0, row=1)

path_label: UI.Label = UI.Label(center_frame, text="Nincsen mappa")
path_label.grid(column=0, row=0)

UI.Button(center_frame, text="Mappa kiválasztása", command=lambda: set_folder_path()).grid(column=0, row=1, pady=10)
UI.Button(center_frame, text="Tovább").grid(column=0, row=2)
    
def set_folder_path() -> None:
    path: str = filedialog.askdirectory(initialdir="/", title="Klaszter mappa kiválasztás")
    if path:
        path_label.configure(text=path)
        return

    path_label._text = "Nincsen mappa"

app.mainloop()