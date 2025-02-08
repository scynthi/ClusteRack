from customtkinter import *
from tkinter import *
from modules.ui import UI, AppWindow
from root import Root

app : AppWindow = AppWindow("800x400")
content : Frame = app.content
content.grid_columnconfigure(0, weight=1)
content.grid_rowconfigure([0,1,2], weight=1)

class ImportUI:
    def __init__(self) -> None:
        self.center_frame: UI.Frame = UI.Frame(content)
        self.center_frame.grid(column=0, row=1)

        path_label: UI.Label = UI.Label(self.center_frame, text="Nincsen mappa")
        path_label.grid(column=0, row=0, padx=5)

        UI.Button(self.center_frame, text="Mappa kiválasztása", command=lambda: set_folder_path()).grid(column=0, row=1, pady=10, padx=5)
        UI.Button(self.center_frame, text="Tovább", command=lambda: init_dashboard()).grid(column=0, row=2)
            
        def set_folder_path() -> None:
            path : str = filedialog.askdirectory(initialdir="/", title="Klaszter mappa kiválasztás")
            if path:
                path_label.configure(text=path)
                return

            path_label._text = "Nincsen mappa"

        def init_dashboard() -> None:
            try:
                Root(path_label._text)
            except:
                pass

    def delete(self) -> None:
        self.center_frame.destroy()

class DashboardUI:
    def __init__() -> None:
        pass


ImportUI()

app.mainloop()