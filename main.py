from customtkinter import *
from tkinter import *
from modules.ui import UI, AppWindow, DGRAY, LGRAY, DBLUE, LBLUE, large_font, small_font, extra_large_font
from modules.root import Root
from PIL import Image, ImageTk
from os import path as Path
from modules.cluster import Cluster
from modules.computer import Computer

app : AppWindow = AppWindow("1000x600")
content : Frame = app.content
root : Root = None

content.grid_columnconfigure(0, weight=1)
content.grid_rowconfigure(0, weight=1)

class ImportUI:
    def __init__(self) -> None:
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

            UI.Label(cluster_frame, text=cluster.name, font=large_font).grid(row=0, column=0)

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
            self.cluster_tab.destroy()
            self.cluster_tab = ClusterBoard(cluster)
        else:
            self.cluster_tab = ClusterBoard(cluster)



                
class ClusterBoard:
    def __init__(self, cluster : Cluster) -> None:
        _frame = app.bottom_frame
        self.frame : UI.Frame = UI.Frame(_frame)
        self.frame.grid(row=0, column=0, sticky="nsw")
        

        UI.Label(self.frame, text=cluster.name, font=extra_large_font).grid(row=0, column=0)

        cluster_frame : UI.Frame = UI.Frame(self.frame)
        cluster_frame.grid(row=1, column=0)
        self.rack_model = UI.EmbedRenderer(cluster_frame, "rack_8", 12, app).get_renderer()

        self.button_frame : UI.Frame = UI.Frame(self.frame)
        self.button_frame.grid(row=2, column=0, sticky="EW")
        self.button_frame.grid_columnconfigure(0, weight=1)

        for i in range(0, 8):
            UI.Button(self.button_frame, text=f"Test {i}").grid(row=i, column=0, pady=5)

        UI.Label(self.frame, text="Information", font=extra_large_font).grid(row=0, column=1)
        self.info_frame : UI.Frame = UI.Frame(self.frame)
        self.info_frame.grid(column=1, row=1, sticky="EWNS")
        self.button_frame.grid_columnconfigure(0, weight=1)
        
        cores : int = 0
        free_cores : int = 0
        memory : int = 0
        free_memory : int = 0

        for computer in cluster.computers.values():
            cores += computer.cores
            free_cores += computer.free_cores
            memory += computer.memory
            free_memory += computer.free_memory

        UI.Label(self.info_frame, text=f"Cores: {cores} millicores").grid(row=0, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Memory: {memory} MB").grid(row=1, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Free cores: {free_cores} millicores").grid(row=2, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Free memory: {free_memory} MB").grid(row=3, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Running processes: {len(cluster.active_processes.keys())}").grid(row=4, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Stopped processes: {len(cluster.inactive_processes.keys())}").grid(row=5, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Computers: {len(cluster.computers.keys())}").grid(row=6, column=0, sticky="w", padx=10)

        self.computer_list_frame : CTkScrollableFrame = CTkScrollableFrame(self.frame, orientation="vertical", border_width=4, border_color="gray", corner_radius=0, width=230)
        self.computer_list_frame.grid(column=1, row=2, sticky="EWNS")

        for i, pc in enumerate(cluster.computers.values()):
            cur_pc_frame : UI.Frame = UI.Frame(self.computer_list_frame)

            image : CTkImage = CTkImage(Image.open(Path.join("Assets", "Images", "computer.png")), size=(220, 80))
            computer_image : CTkLabel = CTkLabel(cur_pc_frame, text=pc.name, font=large_font, fg_color="white", image=image)
            computer_image.grid(row=0, column=0, pady=5)

            UI.Button(cur_pc_frame, text=f"Open {pc.name}", command=lambda pc = i: print(pc)).grid(row=1, column=0, pady=5)
            cur_pc_frame.grid(row=i, column=0, pady=5)






    
    def destroy(self) -> None:
        self.rack_model.running = False
        self.frame.destroy()

    def update(self):
        pass



class ComputerBoard:
    def __init__(self) -> None:
        frame = app.bottom_frame
        computer_frame : UI.Frame = UI.Frame(frame)
        computer_frame.grid(row=0, column=1, sticky="nsew")

        UI.EmbedRenderer(computer_frame, "computer", 12, app).get_renderer()

root = Root(r".\Test folder")
DashboardUI()
app.mainloop()