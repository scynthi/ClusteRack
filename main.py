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
root : Root = None

class ImportUI:
    def __init__(self) -> None:
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)
        self.center_frame: UI.Frame = UI.Frame(content)
        self.center_frame.grid(column=0, row=0)

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
        content.grid_rowconfigure(0, weight=0)
        content.grid_rowconfigure(1, weight=1)

        app.top_frame = UI.Frame(content, height=300)  
        app.top_frame.grid(row=0, column=0, sticky="new")
        app.top_frame.grid_columnconfigure(0, weight=1)

        app.bottom_frame = UI.Frame(content)
        app.bottom_frame.grid(row=1, column=0, sticky="nsew")
        app.bottom_frame.grid_columnconfigure([0,1], weight=1)
        app.bottom_frame.grid_rowconfigure(0, weight=1)

        ClusterView()

class ClusterView:
    def __init__(self) -> None:
        frame = app.top_frame
        clusters_frame : CTkScrollableFrame = CTkScrollableFrame(frame, orientation="horizontal", height=300, border_width=4, border_color="gray", corner_radius=0)
        clusters_frame.grid(row=0, column=0, sticky="nwe")
        self.cluster_tab = None

        for i, cluster in enumerate(root.clusters.values()):
            cluster_frame : UI.Frame = UI.Frame(clusters_frame)
            cluster_frame.grid_rowconfigure(1, weight=1)
            cluster_frame.grid(row=0, column=i, padx=20, pady=10, sticky="NS")

            UI.Label(cluster_frame, text=cluster.name).grid(row=0, column=0)

            image_frame : UI.Frame= UI.Frame(cluster_frame)
            image_frame.grid(row=1, column=0, sticky="NSEW")

            UI.Button(cluster_frame, text=f"Open {cluster.name}", command=lambda selected_cluster = cluster: self.open_cluster_tab(selected_cluster)).grid(row=2, column=0, sticky="EW")
            

            pc_amount : int = len(cluster.computers.keys())
            if pc_amount != 0:
                for x in range(pc_amount):
                    image : CTkImage = CTkImage(Image.open(Path.join("Assets", "Images", "rack.png")), size=(80, 200))
                    button : CTkLabel = CTkLabel(image_frame, text="", image=image)
                    button.grid(row=0, column=x, padx=5)
            else:
                image_frame.grid_rowconfigure(0, weight=1)
                UI.Label(image_frame, text="0 computers have been detected").grid(row=0, column=0)
    
    def open_cluster_tab(self, cluster : Cluster):
        if self.cluster_tab:
            self.cluster_tab.kill()
            self.cluster_tab = None
        else:
            self.cluster_tab = ClusterBoard(cluster)



                
class ClusterBoard:
    def __init__(self, cluster : Cluster) -> None:
        _frame = app.bottom_frame
        self._frame = _frame

        frame : UI.Frame = UI.Frame(_frame)
        frame.grid(row=0, column=0, sticky="nsew")

        cluster_frame : UI.Frame = UI.Frame(frame)
        cluster_frame.grid(row=0, column=0)

        print(cluster.name)

        self.rack_model = UI.EmbedRenderer(cluster_frame, "rack_8", 12, app).get_renderer()
    
    def kill(self) -> None:
        self.rack_model.running = False
        self._frame.destroy()



class ComputerBoard:
    def __init__(self) -> None:
        frame = app.bottom_frame
        computer_frame : UI.Frame = UI.Frame(frame)
        computer_frame.grid(row=0, column=1, sticky="nsew")

        UI.EmbedRenderer(computer_frame, "computer", 12, app).get_renderer()


ImportUI()
app.mainloop()