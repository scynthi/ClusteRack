from customtkinter import *
from tkinter import filedialog
from modules.ui import UI, AppWindow

app = AppWindow("800x400")
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure([0], weight=1)


center_frame : CTkFrame = CTkFrame(app)
center_frame.grid(column=0, row=0)

path_label : UI. Label = UI.Label(center_frame, text="Nincsen mappa")
path_label.grid(column=0, row=0)

UI.Button(center_frame, text="Mappa kiválasztása", command=lambda: set_folder_path()).grid(column=0, row=1, pady=10)
UI.Button(center_frame, text="Tovább").grid(column=0, row=2)

def set_folder_path() -> None:
    path : str = filedialog.askdirectory(initialdir="/", title="Klaszter mappa kiválasztás")
    if path:
        path_label.configure(text=path)
        return

    path_label._text = "Nincsen mappa"


app.mainloop()

