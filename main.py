from customtkinter import *
from tkinter import *
from PIL import Image
from os import path as Path
from modules.ui import UI, AppWindow, DGRAY, LGRAY, DBLUE, LBLUE, large_font, small_font, extra_large_font
from modules.root import Root
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

        self.cluster_view : ClusterView = ClusterView()
    
    def reload_cluster_list(self):
        self.cluster_view.reload()

class ClusterView:
    def __init__(self) -> None:
        frame = app.top_frame
        self.clusters_frame : CTkScrollableFrame = CTkScrollableFrame(frame, orientation="horizontal", height=300, border_width=4, border_color="gray", corner_radius=0)
        self.clusters_frame.grid(row=0, column=0, sticky="nwe")
        self.cluster_tab = None

        for i, cluster in enumerate(root.clusters.values()):
            cluster_frame : UI.Frame = UI.Frame(self.clusters_frame)
            cluster_frame.grid_rowconfigure(1, weight=1)
            cluster_frame.grid(row=0, column=i, padx=20, pady=10, sticky="NS")

            image_frame : UI.Frame= UI.Frame(cluster_frame)
            image_frame.grid(row=1, column=0, sticky="NSEW")

            UI.Label(cluster_frame, text=cluster.name, font=large_font).grid(row=0, column=0)
            UI.Button(cluster_frame, text=f"Open {cluster.name}", command=lambda selected_cluster = cluster: self.open_cluster_tab(selected_cluster)).grid(row=2, column=0, sticky="EW")
            

            pc_amount : int = len(cluster.computers.keys())
            if pc_amount != 0:
                for x in range(pc_amount):
                    image : CTkImage = CTkImage(Image.open(Path.join("Assets", "Images", "rack.png")), size=(80, 200))
                    label : CTkLabel = CTkLabel(image_frame, text="", image=image)
                    label.grid(row=0, column=x, padx=5)
            else:
                image_frame.grid_rowconfigure(0, weight=1)
                UI.Label(image_frame, text="0 computers have been detected").grid(row=0, column=0)

        add_cluster_frame : UI.Frame = UI.Frame(self.clusters_frame)
        add_cluster_frame.grid_rowconfigure(1, weight=1)
        add_cluster_frame.grid(row=0, column=len(root.clusters.values())+1, padx=20, pady=10, sticky="NS")


        image_frame : UI.Frame= UI.Frame(add_cluster_frame)
        image_frame.grid(row=1, column=0, sticky="NSEW")
        image_frame.grid_rowconfigure(0, weight=1)

        UI.Label(add_cluster_frame, text="New cluster", font=large_font).grid(row=0, column=0)
        UI.Button(image_frame, text="Create new cluster", command=UI.SubWindow).grid(row=0, column=0)


    def open_cluster_tab(self, cluster : Cluster) -> None:
        if self.cluster_tab:
            self.cluster_tab.destroy()
            self.cluster_tab = ClusterBoard(cluster)
        else:
            self.cluster_tab = ClusterBoard(cluster)
        

    def reload(self) -> None:
        self.clusters_frame.destroy()
        self.__init__()



                
class ClusterBoard:
    def __init__(self, cluster : Cluster) -> None:
        self.cluster : Cluster = cluster

        self.computer_tab = None

        _frame = app.bottom_frame
        self.frame : UI.Frame = UI.Frame(_frame)
        self.frame.grid(row=0, column=0, sticky="nsw")
        self.frame.grid_rowconfigure(2, weight=1)

        button_frame_helper : UI.Frame = UI.Frame(self.frame)
        button_frame_helper.grid(row=1, column=0, rowspan=2, sticky="EWNS")
        button_frame_helper.grid_rowconfigure(0, weight=1)

        self.button_frame : CTkScrollableFrame = CTkScrollableFrame(button_frame_helper)
        self.button_frame.grid(row=0, column=0, sticky="EWNS")
        self.button_frame.grid_columnconfigure(0, weight=1)

        UI.Label(self.button_frame, text=f"Cluster", font=extra_large_font).grid(row=0, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Rename cluster", command=UI.SubWindow).grid(row=1, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Rename computer", command=UI.SubWindow).grid(row=2, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Move computer", command=UI.SubWindow).grid(row=3, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Create computer", command=UI.SubWindow).grid(row=4, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Edit computer", command=UI.SubWindow).grid(row=5, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Delete computer", command=UI.SubWindow).grid(row=6, column=0, pady=5, padx=10, sticky="we")


        UI.Button(self.button_frame, text=f"Algorithm settings", command=UI.SubWindow).grid(row=7, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Start process", command=UI.SubWindow).grid(row=8, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Relocate process", command=UI.SubWindow).grid(row=9, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Kill process", command=UI.SubWindow).grid(row=10, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Edit process", command=UI.SubWindow).grid(row=11, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Rename process", command=UI.SubWindow).grid(row=12, column=0, pady=5, padx=10, sticky="we")

        process_help_frame : UI.Frame = UI.Frame(self.frame)
        process_help_frame.grid(row=2, column=1, sticky="EWNS")
        process_help_frame.grid_rowconfigure(0, weight=1)
        process_help_frame.grid_columnconfigure(0, weight=1)

        self.processes_frame : CTkScrollableFrame = CTkScrollableFrame(process_help_frame, orientation="vertical")
        self.processes_frame.grid(row=0, column=0, sticky="EWNS")
        self.processes_frame.grid_columnconfigure(0, weight=1)

        UI.Label(self.processes_frame, text="Program list", font=extra_large_font).grid(row=0, column=0)
        UI.Label(self.processes_frame, text="Active", font=extra_large_font).grid(row=1, column=0)
        for i, process in enumerate(cluster.active_processes.keys()):
            temp_proc_frame : UI.Frame = UI.Frame(self.processes_frame)
            temp_proc_frame.grid(row=i+2, column=0, sticky="EW", pady=5)

            UI.Button(temp_proc_frame, text=process).grid(row=0, column=0, sticky="w")
            UI.Label(temp_proc_frame, text=f"Instaces: {cluster.active_processes[process]["instance_count"]}").grid(row=1, column=0)


        UI.Label(self.processes_frame, text="Inactive", font=extra_large_font).grid(row=len(cluster.active_processes.keys())+2, column=0)
        for i, process in enumerate(cluster.inactive_processes.keys()):
            temp_proc_frame : UI.Frame = UI.Frame(self.processes_frame)
            temp_proc_frame.grid(row=len(cluster.inactive_processes.keys())+i+5, column=0, sticky="EW", pady=5)

            UI.Button(temp_proc_frame, text=process).grid(row=0, column=0, sticky="w")
            UI.Label(temp_proc_frame, text=f"Instaces: {cluster.inactive_processes[process]["instance_count"]}").grid(row=1, column=0)

        UI.Label(self.frame, text=cluster.name, font=extra_large_font).grid(row=0, column=1)

        cluster_frame : UI.Frame = UI.Frame(self.frame)
        cluster_frame.grid(row=1, column=1, sticky="new")
        self.rack_model = UI.EmbedRenderer(cluster_frame, "rack_8", 12, app).get_renderer()

        UI.Label(self.frame, text="Information", font=extra_large_font).grid(row=0, column=2)
        self.info_frame : UI.Frame = UI.Frame(self.frame)
        self.info_frame.grid(column=2, row=1, sticky="EWN")
        
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
        self.computer_list_frame.grid(column=2, row=2, sticky="EWNS")

        for i, pc in enumerate(cluster.computers.values()):
            cur_pc_frame : UI.Frame = UI.Frame(self.computer_list_frame)

            image : CTkImage = CTkImage(Image.open(Path.join("Assets", "Images", "computer.png")), size=(220, 80))
            computer_image : CTkLabel = CTkLabel(cur_pc_frame, text=pc.name, font=large_font, text_color="white", image=image)
            computer_image.grid(row=0, column=0, pady=5)

            UI.Button(cur_pc_frame, text=f"Open {pc.name}", command=lambda pc = pc: self.open_computer_tab(pc)).grid(row=1, column=0, pady=5)
            cur_pc_frame.grid(row=i, column=0, pady=5)
        


    def open_computer_tab(self, computer : Computer) -> None:
        if self.computer_tab:
            self.computer_tab.destroy()
            self.computer_tab = ComputerBoard(computer)
        else:
            self.computer_tab = ComputerBoard(computer)
    
    def destroy(self) -> None:
        if self.computer_tab:
            self.computer_tab.destroy()
        self.rack_model.running = False
        self.frame.destroy()

    def reload(self) -> None:
        self.destroy()
        self.__init__(self.cluster)



class ComputerBoard:
    def __init__(self, computer : Computer) -> None:
        self.computer : Computer = computer

        _frame = app.bottom_frame
        self.frame : UI.Frame = UI.Frame(_frame)
        self.frame.grid(row=0, column=1, sticky="nsew")

        UI.Label(self.frame, computer.name, font=extra_large_font).grid(row=0, column=0)
        computer_frame : UI.Frame = UI.Frame(self.frame)
        computer_frame.grid(row=1, column=0, sticky="nesw")
        self.computer_model = UI.EmbedRenderer(computer_frame, "computer", 10, app).get_renderer()

        UI.Label(self.frame, "Resources", font=extra_large_font).grid(row=0, column=1)
        self.resources_frame : UI.Frame = UI.Frame(self.frame)
        self.resources_frame.grid(row=1, column=1, sticky="NS")

        UI.Label(self.resources_frame, text=f"Cores: {self.computer.cores} millicores").grid(row=0, column=0, sticky="w", padx=10)
        UI.Label(self.resources_frame, text=f"Memory: {self.computer.memory} MB").grid(row=1, column=0, sticky="w", padx=10)
        UI.Label(self.resources_frame, text=f"Free cores: {self.computer.free_cores} millicores").grid(row=2, column=0, sticky="w", padx=10)
        UI.Label(self.resources_frame, text=f"Free memory: {self.computer.free_memory} MB").grid(row=3, column=0, sticky="w", padx=10)
        UI.Label(self.resources_frame, text=f"Processes: {len(self.computer.get_prog_instances().keys())}").grid(row=4, column=0, sticky="w", padx=10)
    
        self.processes_frame : UI.Frame = UI.Frame(self.frame)
        self.processes_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.processes_frame.grid_rowconfigure(0, weight=1)
        self.processes_frame.grid_columnconfigure(0, weight=1)

        self.processes_scrollbar_frame : CTkScrollableFrame = CTkScrollableFrame(self.processes_frame, orientation="vertical")
        self.processes_scrollbar_frame.grid(row=0, column=0, sticky="nsew")
        self.processes_scrollbar_frame.grid_rowconfigure(0, weight=1)

        UI.Label(self.processes_scrollbar_frame, "Process list", font=extra_large_font).grid(row=0, column=0)

        for i, process in enumerate(self.computer.get_prog_instances()):
            process_info : dict = self.computer.get_prog_instance_info(process)

            process_help_frame : UI.Frame = UI.Frame(self.processes_scrollbar_frame)
            process_help_frame.grid(row=i+1, column=0, pady=5, sticky="EW")

            UI.Button(process_help_frame, process).grid(row=0, column=0, padx=10)
            UI.Label(process_help_frame, f"Cores: {process_info["cores"]}").grid(row=0, column=1, padx=10)
            UI.Label(process_help_frame, f"Memory: {process_info["memory"]}").grid(row=0, column=2, padx=10)
            UI.Label(process_help_frame, f"Running: {process_info["status"]}").grid(row=0, column=3, padx=10)


        UI.Label(self.frame, "Usage %", font=extra_large_font).grid(row=0, column=2)
        self.cpu_usage_frame : UI.Frame = UI.Frame(self.frame)
        self.cpu_usage_frame.grid(row=1, column=2)
        UI.Plot(self.computer, self.cpu_usage_frame, "Core usage %", "core_usage_percent")

        self.memory_usage_frame : UI.Frame = UI.Frame(self.frame)
        self.memory_usage_frame.grid(row=2, column=2)
        UI.Plot(self.computer, self.memory_usage_frame, "Memory usage %", "memory_usage_percent")
        


    def destroy(self) -> None:
        self.computer_model.running = False
        self.frame.destroy()

    def reload(self) -> None:
        self.destroy()
        self.__init__(self.computer)

root = Root(r".\Test folder")
DashboardUI()
app.mainloop()