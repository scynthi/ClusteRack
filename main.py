from customtkinter import *
from tkinter import *
from modules.ui import UI, AppWindow, DGRAY, LGRAY, DBLUE, LBLUE
from modules.root import Root
from PIL import Image, ImageTk
from os import path as Path
from modules.cluster import Cluster
from modules.computer import Computer

app : AppWindow = AppWindow("1000x600")
content : Frame = app.content
content.grid_columnconfigure(0, weight=1)
content.grid_rowconfigure([0,1,2], weight=1)

root : Root = None

class ImportUI:
    def __init__(self) -> None:
        self.center_frame: UI.Frame = UI.Frame(content)
        self.center_frame.grid(column=0, row=1)

        self.path_label: UI.Label = UI.Label(self.center_frame, text="Nincsen mappa")
        self.path_label.grid(column=0, row=0, padx=5)

        UI.Button(self.center_frame, text="Mappa kiválasztása", command=lambda: set_folder_path()).grid(column=0, row=1, pady=10, padx=5)
        UI.Button(self.center_frame, text="Tovább", command=lambda: init_dashboard()).grid(column=0, row=2)

            
        def set_folder_path() -> None:
            path : str = filedialog.askdirectory(initialdir="./", title="Klaszter mappa kiválasztás")

            if path:
                self.path_label.configure(text=path)
                return

            self.path_label._text = "Nincsen mappa"

        def init_dashboard() -> None:
            global root
            root = Root(self.path_label._text)
            
            self.delete()
            DashboardUI()


    def delete(self) -> None:
        self.center_frame.grid_forget()
        

class DashboardUI:
    def __init__(self) -> None:
        clusters_frame : CTkScrollableFrame = CTkScrollableFrame(content, orientation="horizontal", height=300, border_width=4, border_color="gray", corner_radius=0)
        clusters_frame.grid(row=0, column=0, sticky="nwe")

        for i, cluster in enumerate(root.clusters.values()):
            cluster_frame : UI.Frame = UI.Frame(clusters_frame)
            cluster_frame.grid_rowconfigure(1, weight=1)
            cluster_frame.grid(row=0, column=i, padx=20, pady=10, sticky="NS")

            UI.Label(cluster_frame, text=cluster.name).grid(row=0, column=0)

            image_frame : UI.Frame= UI.Frame(cluster_frame)
            image_frame.grid(row=1, column=0, sticky="NSEW")

            UI.Button(cluster_frame, text=f"Open {cluster.name}", command=lambda cluster_name = cluster.name: print(cluster_name)).grid(row=2, column=0, sticky="EW")
            

            pc_amount : int = len(cluster.computers.keys())
            if pc_amount != 0:
                for x in range(pc_amount):
                    image : CTkImage = CTkImage(Image.open(Path.join("Assets", "Images", "rack.png")), size=(80, 200))
                    button : CTkLabel = CTkLabel(image_frame, text="", image=image)
                    button.grid(row=0, column=x, padx=5)
            else:
                image_frame.grid_rowconfigure(0, weight=1)
                UI.Label(image_frame, text="0 computers have been detected").grid(row=0, column=0)

                


ImportUI()
app.mainloop()