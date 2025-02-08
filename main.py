from customtkinter import *
from tkinter import *
from modules.ui import UI, AppWindow
from modules.root import Root
from modules.ui_obj_renderer import EmbedRendererWindow

app : AppWindow = AppWindow("1000x600")
content : Frame = app.content
content.grid_columnconfigure(0, weight=1)
content.grid_rowconfigure([0,1,2], weight=1)

root : Root = None

class ImportUI:
    def __init__(self) -> None:
        self.center_frame: UI.Frame = UI.Frame(content)
        self.center_frame.grid(column=0, row=1)

        path_label: UI.Label = UI.Label(self.center_frame, text="Nincsen mappa")
        path_label.grid(column=0, row=0, padx=5)

        UI.Button(self.center_frame, text="Mappa kiválasztása", command=lambda: set_folder_path()).grid(column=0, row=1, pady=10, padx=5)
        UI.Button(self.center_frame, text="Tovább", command=lambda: init_dashboard()).grid(column=0, row=2)
            
        def set_folder_path() -> None:
            path : str = filedialog.askdirectory(initialdir="./", title="Klaszter mappa kiválasztás")

            if path:
                path_label.configure(text=path)
                return

            path_label._text = "Nincsen mappa"

        def init_dashboard() -> None:
            global root
            root = Root(path_label._text)
            
            self.delete()
            DashboardUI()


    def delete(self) -> None:
        self.center_frame.grid_forget()
        
        
class DashboardUI:
    def __init__(self) -> None:
        clusters_frame : CTkScrollableFrame = CTkScrollableFrame(content, orientation="horizontal")
        clusters_frame.grid(row=0, column=0, sticky="nwe")

        a = EmbedRendererWindow(clusters_frame, "rack_1")
        a.pygame_frame.grid(row=0, column=0)

        app.after(5000, lambda: EmbedRendererWindow(content, "rack_2").pygame_frame.grid(row=0, column=1))

        
        
        


ImportUI()

app.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
app.mainloop()