from customtkinter import *
from tkinter import *
from PIL import Image
from os import path as Path
from modules.ui import UI, AppWindow, DGRAY, LGRAY, DBLUE, LBLUE, large_font, small_font, extra_large_font, bold_large_font, larger_font, audio
from modules.root import Root
from modules.cluster import Cluster
from modules.computer import Computer
from modules.subwindow import *

app : AppWindow = AppWindow("1000x600")
content : Frame = app.content
root : Root = None

content.grid_columnconfigure(0, weight=1)
content.grid_rowconfigure(0, weight=1)

class ImportUI:
    def __init__(self):
        self.center_frame: UI.Frame = UI.Frame(content)
        self.center_frame.grid(column=0, row=0)

        self.path_label: UI.Label = UI.Label(self.center_frame, text="Nincsen mappa")
        self.path_label.grid(column=0, row=0, padx=5)

        self.path = None

        UI.Button(self.center_frame, text="Mappa kiválasztása", command=lambda: set_folder_path()).grid(column=0, row=1, pady=10, padx=5)
        UI.Button(self.center_frame, text="Tovább", command=lambda: init_dashboard()).grid(column=0, row=2)

            
        def set_folder_path() -> None:
            self.path = filedialog.askdirectory(initialdir="./", title="Klaszter mappa kiválasztás")

            if self.path:
                self.path_label.configure(text=self.path)
                return

            self.path_label._text = "Nincsen mappa"

        def init_dashboard() -> None:
            if self.path:
                global root
                root = Root(Path.join(self.path), app)
                self.delete()
                DashboardUI()
            
           
            


    def delete(self) -> None:
        self.center_frame.grid_forget()
        

class DashboardUI:
    def __init__(self):
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
        app.cli_button.configure(command=lambda: os.system(f'start cmd /c py interp_test.py "{Path.abspath(Path.join(root.path))}"'))
        app.reload_button.configure(command=lambda: full_reload())

        def full_reload() -> None:
            root.__init__(Path.join(root.path), app)
            self.cluster_view.destroy_and_reload()

        


class ClusterView:
    def __init__(self):
        root._load_clusters()
        frame = app.top_frame
        self.clusters_frame : CTkScrollableFrame = CTkScrollableFrame(frame, orientation="horizontal", height=310, border_width=4, border_color="gray", corner_radius=0)
        self.clusters_frame.grid(row=0, column=0, sticky="nwes")
        self.clusters_frame.grid_columnconfigure(0, weight=1)
        self.clusters_frame.grid_rowconfigure(0, weight=1)

        for i, cluster in enumerate(root.clusters.values()):
            cluster_frame : UI.Frame = UI.Frame(self.clusters_frame)
            cluster_frame.grid_rowconfigure(1, weight=1)
            cluster_frame.grid(row=0, column=i, padx=20, pady=10, sticky="NEWS")

            image_frame : UI.Frame= UI.Frame(cluster_frame)
            image_frame.grid(row=1, column=0, sticky="NSEW")

            UI.Label(cluster_frame, text=cluster.name, font=large_font).grid(row=0, column=0)
            UI.Button(cluster_frame, text=f"{cluster.name} megnyitása", command=lambda selected_cluster = cluster: self.open_cluster_tab(selected_cluster)).grid(row=2, column=0, sticky="EW")
            

            pc_amount : int = len(cluster.computers.keys())
            if pc_amount != 0:
                for x in range(pc_amount):
                    image : CTkImage = CTkImage(Image.open(Path.join("Assets", "Images", "rack.png")), size=(80, 200))
                    label : CTkLabel = CTkLabel(image_frame, text="", image=image)
                    label.grid(row=0, column=x, padx=5)
            else:
                image_frame.grid_columnconfigure(0, weight=1)
                image_frame.grid_rowconfigure(0, weight=1)
                UI.Label(image_frame, text="Nem található számítógépek").grid(row=0, column=0, padx=5)

        add_cluster_frame : UI.Frame = UI.Frame(self.clusters_frame)
        add_cluster_frame.grid_rowconfigure(1, weight=1)
        add_cluster_frame.grid(row=0, column=len(root.clusters.values())+1, padx=20, pady=10, sticky="NS")

        UI.Label(add_cluster_frame, text="Új klaszter", font=large_font).grid(row=0, column=0)
        UI.Button(add_cluster_frame, text="Új klaszter létrehozása", command=lambda: ClusterCreateSubWindow(root, self)).grid(row=1, column=0)


    def open_cluster_tab(self, cluster : Cluster) -> None:
        if hasattr(self, "cluster_tab"):
            if self.cluster_tab: self.cluster_tab.destroy()
            self.cluster_tab = ClusterBoard(cluster, self)
        else:
            self.cluster_tab = ClusterBoard(cluster, self)
        

    def destroy_and_reload(self) -> None:
        try:
            self.cluster_tab.destroy()
        except: pass
        self.clusters_frame.destroy()
        self.__init__()


    def reload(self) -> None:
        cluster_tab = None
        if hasattr(self, "cluster_tab"):
            try:
                self.cluster_tab.reload_with_child()
                cluster_tab = self.cluster_tab
            except: pass
        self.clusters_frame.destroy()
        self.__init__()
        self.cluster_tab = cluster_tab


                
class ClusterBoard:
    def __init__(self, cluster : Cluster, parent_ui : ClusterView):
        self.cluster : Cluster = cluster
        self.parent_ui : ClusterView = parent_ui

        self.computer_tab = None

        _frame = app.bottom_frame
        self.frame : UI.Frame = UI.Frame(_frame)
        self.frame.grid(row=0, column=0, sticky="nsw")
        self.frame.grid_rowconfigure(2, weight=1)
        
        self.cluster_ui_name : str = cluster.name

        if len(cluster.name) > 17:
            self.cluster_ui_name = cluster.name[:17] + "..."

        UI.Label(self.frame, text="Parancsok", font=larger_font, text_color=DBLUE).grid(row=0, column=0, pady=8)
        UI.Label(self.frame, text=self.cluster_ui_name, font=larger_font, text_color=DBLUE).grid(row=0, column=1)
        UI.Label(self.frame, text="Információk", font=larger_font, text_color=DBLUE).grid(row=0, column=2)


        button_frame_helper : UI.Frame = UI.Frame(self.frame)
        button_frame_helper.grid(row=1, column=0, rowspan=2, sticky="EWNS")
        button_frame_helper.grid_rowconfigure(0, weight=1)

        self.button_frame : CTkScrollableFrame = CTkScrollableFrame(button_frame_helper)
        self.button_frame.grid(row=0, column=0, sticky="EWNS")
        self.button_frame.grid_columnconfigure(0, weight=1)


        UI.Button(self.button_frame, text=f"Gép hozzáadás", command=lambda: ComputerCreateSubWindow(self.cluster, self)).grid(row=0, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Program hozzáadás", command=lambda: StartProgramSubWindow(self.cluster, self)).grid(row=1, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Algoritmus\nbeállítások", command=lambda: ClusterAlgorithmSubWindow(self.cluster, self)).grid(row=2, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Program mozgatás", command=lambda: MoveProgramSubWindow(root, self.cluster, self)).grid(row=3, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Klaszter\nátnevezése", command=lambda: ClusterRenameSubWindow(root, cluster, self)).grid(row=4, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Klaszter\nújratöltése", bg_color="orange", command=lambda:(cluster.reload_cluster(), self.reload_with_child())).grid(row=5, column=0, pady=5, padx=10, sticky="we")
        UI.Button(self.button_frame, text=f"Klaszter törlése", bg_color="red", command=lambda: delete_cluster_and_reload()).grid(row=6, column=0, pady=5, padx=10, sticky="we")


        program_help_frame : UI.Frame = UI.Frame(self.frame)
        program_help_frame.grid(row=2, column=1, sticky="EWNS")
        program_help_frame.grid_rowconfigure(0, weight=1)
        program_help_frame.grid_columnconfigure(0, weight=1)

        self.program_frame : CTkScrollableFrame = CTkScrollableFrame(program_help_frame, orientation="vertical")
        self.program_frame.grid(row=0, column=0, sticky="EWNS")
        self.program_frame.grid_columnconfigure(0, weight=1)
        UI.Label(self.program_frame, text="Program lista", font=larger_font, text_color=DBLUE).grid(row=0, column=0)


        for i, program in enumerate(cluster.programs):
            temp_program_frame : UI.Frame = UI.Frame(self.program_frame)
            temp_program_frame.grid(row=i+1, column=0, sticky="EW", pady=5)
        
            UI.Button(temp_program_frame, text=f"{program}".upper(), font=bold_large_font, command=lambda program = program: ProgramInstancesSubWindow(self.cluster, program, self)).grid(row=0, column=0, sticky="ew")
            UI.Label(temp_program_frame, text=f"Futtatandó példányok: {cluster.programs[program]["required_count"]}").grid(row=1, column=0, pady=10, sticky="w")
            
            temp_program_frame.grid_columnconfigure(0, weight=1)
            help_button_frame : UI.Frame = UI.Frame(temp_program_frame)
            help_button_frame.grid(row=2, column=0, sticky="ew")
            help_button_frame.grid_columnconfigure([0,1], weight=1)
            UI.Button(help_button_frame, text="Megállítás", command=lambda program = program: stop_program(program)).grid(row=2, column=0, sticky="ew")
            UI.Button(help_button_frame, text="Törlés", fg_color="red", command=lambda program = program: delete_program(program)).grid(row=2, column=1, sticky="ew")
            UI.Button(help_button_frame, text="Átírás", command=lambda program = program: EditProgramSubWindow(self.cluster, program, self)).grid(row=3, column=0, columnspan=3, sticky="ew")


        cluster_frame : UI.Frame = UI.Frame(self.frame)
        cluster_frame.grid(row=1, column=1, sticky="new")

        model_num : int = len(cluster.computers.keys())
        if model_num > 8: model_num = 8
    

        self.rack_model = UI.EmbedRenderer(cluster_frame, f"rack_{model_num}", 12, app).get_renderer()

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

        instance_count = 0
        for program in cluster.instances.keys():
            for _ in cluster.instances[program].keys():
                instance_count += 1

        UI.Label(self.info_frame, text=f"Magok: {cores} millimag").grid(row=0, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Memória: {memory} MB").grid(row=1, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Szabad magok: {free_cores} millimag").grid(row=2, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Szabad memória: {free_memory} MB").grid(row=3, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Programok: {len(cluster.programs)}").grid(row=4, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Program példányok: {cluster.active_inst_num} aktív, {cluster.inactive_inst_num} inaktív").grid(row=5, column=0, sticky="w", padx=10)
        UI.Label(self.info_frame, text=f"Számítógépek: {len(cluster.computers.keys())}").grid(row=6, column=0, sticky="w", padx=10)        


        self.computer_list_frame : CTkScrollableFrame = CTkScrollableFrame(self.frame, orientation="vertical", border_width=4, border_color="gray", corner_radius=0, width=230)
        self.computer_list_frame.grid(column=2, row=2, sticky="EWNS")
        self.computer_list_frame.grid_columnconfigure(0, weight=1)

        for i, pc in enumerate(cluster.computers.values()):
            computer : Computer = cluster.computers.get(pc.name)

            cur_pc_frame : UI.Frame = UI.Frame(self.computer_list_frame)
            cur_pc_frame.grid(row=i, column=0, pady=5, sticky="ew")
            cur_pc_frame.grid_columnconfigure(0, weight=1)

            image : CTkImage = CTkImage(Image.open(Path.join("Assets", "Images", "computer.png")), size=(220, 80))
            computer_image : CTkLabel = CTkLabel(cur_pc_frame, text=computer.name, font=large_font, text_color="white", image=image)
            computer_image.grid(row=0, column=0, pady=5, sticky="we")

            UI.Button(cur_pc_frame, text=f"{computer.name} megnyitása", command=lambda pc = computer: self.open_computer_tab(pc)).grid(row=1, column=0, pady=5)
            
        
        def delete_cluster_and_reload() -> None:
            if root.delete_cluster(self.cluster.name, "f"):
                audio.play_accept()
                parent_ui.reload()
                self.destroy()
            else:
                ErrorSubWindow("Klaszter törlése sikertelen.")

        def stop_program(program : str) -> None:
            if cluster.stop_program(program):
                self.reload_with_child()
                audio.play_close_program()
            else:
                ErrorSubWindow("Program leállítása sikertelen.")

        def delete_program(program : str) -> None:
            if cluster.kill_program(program):
                self.reload_with_child()
            else:
                ErrorSubWindow("Program törlése sikertelen.")

    def open_computer_tab(self, computer : Computer) -> None:
        if self.computer_tab:
            self.prev_computer = computer
            self.computer_tab.destroy()
            self.computer_tab = ComputerBoard(self.cluster, computer, self)
        else:
            self.prev_computer = computer
            self.computer_tab = ComputerBoard(self.cluster, computer, self)
    
    def destroy(self) -> None:
        if self.computer_tab:
            self.computer_tab.destroy()
        self.rack_model.running = False
        self.frame.destroy()

    def reload(self) -> None:
        self.destroy()
        self.__init__(self.cluster, self.parent_ui)
        try:
            self.computer_tab.destroy()
        except: pass

    def reload_with_child(self) -> None:
        prev_computer = None
        if hasattr(self, "prev_computer"):
            prev_computer = self.prev_computer

        self.destroy()
        self.__init__(self.cluster, self.parent_ui)
        if prev_computer:
            self.open_computer_tab(prev_computer)

        



class ComputerBoard:
    def __init__(self, cluster : Cluster, computer : Computer, parent_ui):
        self.computer : Computer = computer
        self.cluster : Cluster = cluster
        self.parent_ui = parent_ui

        _frame = app.bottom_frame
        self.frame : UI.Frame = UI.Frame(_frame)
        self.frame.grid(row=0, column=1, sticky="nsew")

        self.computer_ui_name : str = computer.name

        if len(computer.name) > 17:
            self.computer_ui_name = computer.name[:17] + "..."

        UI.Label(self.frame, self.computer_ui_name, font=larger_font, text_color=DBLUE).grid(row=0, column=0, pady=8)
        UI.Label(self.frame, "Erőforrások", font=larger_font, text_color=DBLUE).grid(row=0, column=1)
        UI.Label(self.frame, "Kihasználtság", font=larger_font, text_color=DBLUE).grid(row=0, column=2)

        self.computer_frame : UI.Frame = UI.Frame(self.frame)
        self.computer_frame.grid(row=1, column=0, sticky="nesw")
        self.computer_frame.grid_rowconfigure(2, weight=1)

        self.computer_model = UI.EmbedRenderer(self.computer_frame, "computer", 10, app).get_renderer()
        UI.Button(self.computer_frame, text="Számítógép törlése", fg_color="red", command=lambda: delete_self()).grid(row=2, column=0, sticky="sew", padx=10, pady=5)
        UI.Button(self.computer_frame, text="Számítógép mozgatása", command=lambda: MoveComputerSubWindow(root, self.cluster, self.computer, self)).grid(row=3, column=0, sticky="sew", padx=10, pady=5)


        self.resources_frame : UI.Frame = UI.Frame(self.frame)
        self.resources_frame.grid(row=1, column=1, sticky="NS")
        self.resources_frame.grid_rowconfigure(5, weight=1)


        UI.Label(self.resources_frame, text=f"Magok: {self.computer.cores} millimag").grid(row=0, column=0, sticky="w", padx=10)
        UI.Label(self.resources_frame, text=f"Memória: {self.computer.memory} MB").grid(row=1, column=0, sticky="w", padx=10)
        UI.Label(self.resources_frame, text=f"Szabad magok: {self.computer.free_cores} millimag").grid(row=2, column=0, sticky="w", padx=10)
        UI.Label(self.resources_frame, text=f"Szabad memória: {self.computer.free_memory} MB").grid(row=3, column=0, sticky="w", padx=10)
        UI.Label(self.resources_frame, text=f"Példányok: {self.computer.active_inst_num} aktív, {self.computer.inactive_inst_num} inaktív").grid(row=4, column=0, sticky="w", padx=10)
        
        UI.Button(self.resources_frame, text="Erőforrások átírása", command=lambda: ComputerEditResourcesSubWindow(self.cluster, self.computer, self)).grid(row=5, column=0, sticky="sew", padx=10, pady=5)
        UI.Button(self.resources_frame, text="Átnevezés", command=lambda: ComputerRenameSubWindow(self.cluster, self.computer, self)).grid(row=6, column=0, sticky="sew", padx=10, pady=5)
    
        self.instances_frame : UI.Frame = UI.Frame(self.frame)
        self.instances_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.instances_frame.grid_rowconfigure(0, weight=1)
        self.instances_frame.grid_columnconfigure(0, weight=1)

        self.instances_scrollbar_frame : CTkScrollableFrame = CTkScrollableFrame(self.instances_frame, orientation="vertical")
        self.instances_scrollbar_frame.grid(row=0, column=0, sticky="nsew")
        self.instances_scrollbar_frame.grid_columnconfigure(0, weight=1)

        UI.Label(self.instances_scrollbar_frame, "Program példányok:", font=larger_font, text_color=DBLUE).grid(row=0, column=0)

        for i, instance in enumerate(self.computer.get_prog_instances()):
            if not cluster.get_instance_by_id(instance.split("-")[1]):
                return
            instance_info : dict = cluster.get_instance_by_id(instance.split("-")[1])[1]

            instance_help_frame : UI.Frame = UI.Frame(self.instances_scrollbar_frame)
            instance_help_frame.grid(row=i+1, column=0, pady=5, sticky="EW")
            instance_help_frame.grid_columnconfigure(0, weight=1)

            instance_status_help_frame : UI.Frame = UI.Frame(instance_help_frame, borderwidth=0)
            instance_status_help_frame.grid(row=0, column=0, pady=10, sticky="w")

            UI.Button(instance_status_help_frame, instance, command=lambda instance_id = instance.split("-")[1]: InstanceInfoSubWindow(cluster, instance_id, self)).grid(row=0, column=0, pady=10, sticky="w")
            
            status_label =  UI.Label(instance_status_help_frame, text="")
            status_label.grid(row=0, column=1, pady=10, padx=5, sticky="w")

            if instance_info["status"]:
                status_label.configure(True, text="⬤", text_color="green")
            else:
                status_label.configure(True, text="⬤", text_color="red")

            instance_info_help_frame : UI.Frame = UI.Frame(instance_help_frame)
            instance_info_help_frame.grid(row=1, column=0, sticky="ew")

            UI.Label(instance_info_help_frame, f"Magok: {instance_info["cores"]}").grid(row=0, column=0, padx=10)
            UI.Label(instance_info_help_frame, f"Memória: {instance_info["memory"]}").grid(row=0, column=1, padx=10)
            UI.Label(instance_info_help_frame, f"Státusz: {'Aktív' if instance_info["status"] else 'Inaktív'}").grid(row=0, column=2, padx=10)


        self.cpu_usage_frame : UI.Frame = UI.Frame(self.frame)
        self.cpu_usage_frame.grid(row=1, column=2)
        UI.Plot(self.computer, self.cpu_usage_frame, "Processzor %", "core_usage_percent")

        self.memory_usage_frame : UI.Frame = UI.Frame(self.frame)
        self.memory_usage_frame.grid(row=2, column=2)
        UI.Plot(self.computer, self.memory_usage_frame, "Memória %", "memory_usage_percent")


        def delete_self() -> None:
            if cluster.delete_computer(self.computer.name, "f"):
                cluster._load_computers()
                self.parent_ui.parent_ui.destroy_and_reload()
                self.destroy()
                audio.play_close_computer()
            else:
                ErrorSubWindow("Számítógép törlése sikertelen.")
        


    def destroy(self) -> None:
        self.computer_model.running = False
        self.frame.destroy()

    def reload(self) -> None:
        computer : Computer = self.cluster.computers.get(self.computer.name)
        cluster : Cluster = self.cluster
        parent_ui = self.parent_ui

        self.destroy()
        self.__init__(cluster, computer, parent_ui)


ImportUI()

# import random
# app.reload_button.config(command=lambda: fun())
# def fun():
#     while True:
#         x = random.randint(1, 1000)
#         y = random.randint(1, 1000)
#         app.geometry(f"{x}x{y}+{x}+{y}")
#         app.update()

app.mainloop()





    

