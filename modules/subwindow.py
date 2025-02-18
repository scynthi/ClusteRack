from modules.ui import UI, AppWindow, DGRAY, LGRAY, DBLUE, LBLUE, large_font, small_font, extra_large_font, audio
from customtkinter import *
from tkinter import *
from ctypes import windll
from os import path as Path
from PIL import Image
from modules.root import Root
from modules.cluster import Cluster
from modules.computer import Computer


class SubWindow(CTkToplevel):
    def __init__(self):
        super().__init__()
        self.iconbitmap(Path.join("Assets", "Images", "logo.ico"))
        self.overrideredirect(True)
        self.geometry("500x300")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.config(bg=DGRAY)
        self.minimized : bool = False
        self.maximized : bool = False
        self.normal_size = self.geometry()
        self.attributes("-topmost", 1)

        title_bar : CTkFrame = Frame(self, bg=LBLUE, relief='raised', border=4)
        title_bar.grid_columnconfigure([1,2], weight=1)
        title_bar.bind('<Button-1>', self.get_pos)
        title_bar.grid(row=0, column=0, sticky="new")


        close_button : UI.Button = UI.Button(title_bar, text=' X ', command=self.destroy, padx=2, pady=2)
        program_logo : CTkImage = CTkImage(light_image=Image.open(Path.join("Assets", "Images", "logo.png")), size=(40,40))
        logo_label : CTkLabel = CTkLabel(title_bar, image=program_logo, text="")
        logo_label.grid(row=0, column=0, sticky="nw", padx=10)


        title_bar_title : UI.Label = UI.Label(title_bar, text="ClusteRack Subwindow", text_color='white', font=("VCR OSD MONO", 20))
        title_bar_title.bind('<Button-1>', self.get_pos)
        title_bar_title.grid(row=0, column=1, sticky="nw", padx=10, pady=5)
        close_button.grid(row=0, column=2, sticky="ne", padx=7, pady=1)


        content : Frame = Frame(self, bg=DGRAY)
        content.grid(row=1, column=0, sticky="nsew")

        resizey_widget : Frame = Frame(self, cursor='sb_v_double_arrow')
        resizey_widget.grid(row=1, column=0, sticky="SEW")
        resizey_widget.bind("<B1-Motion>", self.resizey)

        resizex_widget : Frame = Frame(self, cursor='sb_h_double_arrow')
        resizex_widget.grid(row=1, column=1, sticky="NSE")
        resizex_widget.bind("<B1-Motion>", self.resizex)


        self.title_bar : Frame = title_bar
        self.close_button : Frame = close_button
        self.title_bar_title : Frame = title_bar_title
        self.content : Frame = content

        self.after(10, self.set_appwindow)
        self.after(100, self.focus)
        audio.play_notification()
        

    def set_appwindow(self) -> None:
        GWL_EXSTYLE : int = -20
        WS_EX_APPWINDOW  = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        
        hwnd = windll.user32.GetParent(self.winfo_id())
        stylew = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        stylew = stylew & ~WS_EX_TOOLWINDOW
        stylew = stylew | WS_EX_APPWINDOW

        self.wm_withdraw()
        self.after(10, lambda: self.wm_deiconify())


    def get_pos(self, event) -> None:
        if self.maximized == False:
            xwin : int = self.winfo_x()
            ywin : int = self.winfo_y()
            startx : int = event.x_root
            starty : int = event.y_root

            ywin : int = ywin - starty
            xwin : int = xwin - startx

            def move_window(event) -> None:
                self.config(cursor="fleur")
                self.geometry(f'+{event.x_root + xwin}+{event.y_root + ywin}')

            def release_window(event) -> None:
                self.config(cursor="arrow")

            self.title_bar.bind('<B1-Motion>', move_window)
            self.title_bar.bind('<ButtonRelease-1>', release_window)
            self.title_bar_title.bind('<B1-Motion>', move_window)
            self.title_bar_title.bind('<ButtonRelease-1>', release_window)
        else:
            self.maximized = not self.maximized


    def resizex(self, event) -> None:
            xwin : int = self.winfo_x()
            difference : int = (event.x_root - xwin) - self.winfo_width()

            if self.winfo_width() > 150: 
                try:
                    self.geometry(f"{self.winfo_width() + difference}x{self.winfo_height()}")
                except:
                    pass
            else:
                if difference > 0:
                    try:
                        self.geometry(f"{self.winfo_width() + difference}x{self.winfo_height()}")
                    except:
                        pass
        
    
    def resizey(self, event) -> None:
        ywin : int = self.winfo_y()
        difference : int = (event.y_root - ywin) - self.winfo_height()

        if self.winfo_height() > 150:
            try:
                self.geometry(f"{self.winfo_width()}x{self.winfo_height() + difference}")
            except:
                pass
        else:
            if difference > 0:
                try:
                    self.geometry(f"{self.winfo_width()}x{self.winfo_height() + difference}")
                except:
                    pass


class ClusterCreateSubWindow(SubWindow):
    def __init__(self, root : Root, ui):
        super().__init__()
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(2, weight=1)

        Label(self.content, text="Klaszter létrehozás", fg="black",  font=large_font, bg=DGRAY).grid(row=0, column=0, pady=5)
        entry : UI.Entry = UI.Entry(self.content)
        entry.grid(row=1, column=0, pady=20, padx=50, stick="ew")
        Button(self.content, text="Létrehozás", font=large_font, bg=DBLUE, fg="white", command=lambda: create_cluster(self)).grid(row=2, column=0, sticky="N")
        error_message : UI.Label = UI.Label(self.content, text="", text_color="red", font=large_font)
        error_message.grid(row=3, column=0, pady=15)


        def create_cluster(self) -> None:
            try:
                if root.create_cluster(entry.get()):
                    ui.reload()
                    audio.play_accept()
                    self.destroy()
                else:
                    audio.play_error()
                    error_message._text = "Hibás klaszter név!"
            except:
                error_message._text = "Adjon meg egy nevet!"
                audio.play_error()

class ComputerCreateSubWindow(SubWindow):
    def __init__(self, cluster : Cluster, ui):
        super().__init__()
        self.geometry("500x400")
        self.content.grid_columnconfigure(0, weight=1)

        Label(self.content, text=f"Gép hozzáadás a {cluster.name} klaszterhez", fg="black",  font=large_font, bg=DGRAY).grid(row=0, column=0, pady=5)

        UI.Label(self.content, "Számítógép neve:").grid(row=1, column=0)
        computer_name : UI.Entry = UI.Entry(self.content)
        computer_name.grid(row=2, column=0, pady=5, padx=50, stick="ew")

        UI.Label(self.content, "Magok száma millimagokban: ").grid(row=3, column=0)
        core_entry : UI.Entry = UI.Entry(self.content)
        core_entry.grid(row=4, column=0, pady=5, padx=50, stick="ew")

        UI.Label(self.content, "Memória megabájtban:").grid(row=5, column=0)
        memory_entry : UI.Entry = UI.Entry(self.content)
        memory_entry.grid(row=6, column=0, pady=5, padx=50, stick="ew")


        Button(self.content, text="Létrehozás", font=large_font, bg=DBLUE, fg="white", command=lambda: create_computer(self)).grid(row=7, column=0, sticky="N")

        error_message : UI.Label = UI.Label(self.content, text="", text_color="red", font=large_font)
        error_message.grid(row=8, column=0, pady=15)

        def create_computer(self) -> None:
            try:
                if cluster.create_computer(computer_name.get(), int(core_entry.get()), int(memory_entry.get())):
                    ui.reload()
                    if ui.parent_ui:
                        ui.parent_ui.reload()
                    audio.play_accept()
                    self.destroy()
                else:
                    audio.play_error()
                    error_message._text = "Rossz típusú adatok lettek megadva."
            except:
                    audio.play_error()
                    error_message._text = "Belső hiba. Próbálja újra."






class StartProgramSubWindow(SubWindow):
    def __init__(self, cluster : Cluster, ui):
        super().__init__()
        self.geometry("500x500")
        self.content.grid_columnconfigure(0, weight=1)
        Label(self.content, text=f"Program hozzáadás a {cluster.name} klaszterhez", fg="black",  font=large_font, bg=DGRAY).grid(row=0, column=0, pady=5)

        UI.Label(self.content, "Program neve").grid(row=1, column=0)
        program_name : UI.Entry = UI.Entry(self.content)
        program_name.grid(row=2, column=0, pady=5, padx=50, stick="ew")

        UI.Label(self.content, "Futtatandó példányok: ").grid(row=3, column=0)
        instance_entry : UI.Entry = UI.Entry(self.content)
        instance_entry.grid(row=4, column=0, pady=5, padx=50, stick="ew")

        UI.Label(self.content, "Magok száma millimagokban: ").grid(row=5, column=0)
        core_entry : UI.Entry = UI.Entry(self.content)
        core_entry.grid(row=6, column=0, pady=6, padx=50, stick="ew")

        UI.Label(self.content, "Memória megabájtban").grid(row=7, column=0)
        memory_entry : UI.Entry = UI.Entry(self.content)
        memory_entry.grid(row=8, column=0, pady=8, padx=50, stick="ew")

        Button(self.content, text="Program hozzáadása", font=large_font, bg=DBLUE, fg="white", command=lambda: try_add_program()).grid(row=9, column=0, sticky="N")

        error_message : UI.Label = UI.Label(self.content, text="", text_color="red", font=large_font)
        error_message.grid(row=10, column=0, pady=15)

        def try_add_program() -> None:
            if cluster.add_program(program_name.get(), instance_entry.get(), core_entry.get(), memory_entry.get()):
                ui.reload()
                audio.play_accept()
                self.destroy()
            else:
                audio.play_error()
                error_message._text = "Rossz típusú adatok. Próbálja újra."


class ClusterRenameSubWindow(SubWindow):
    def __init__(self, root : Root, cluster : Cluster, ui):
        super().__init__()
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(2, weight=1)

        Label(self.content, text=f"Klaszter ({cluster.name}) átnevezése", fg="black",  font=large_font, bg=DGRAY).grid(row=0, column=0, pady=5)
        entry : UI.Entry = UI.Entry(self.content)
        entry.grid(row=1, column=0, pady=20, padx=50, stick="ew")
        

        Button(self.content, text="Átnevezés", font=large_font, bg=DBLUE, fg="white", command=lambda: rename_cluster(self)).grid(row=2, column=0, sticky="N")
        error_message : UI.Label = UI.Label(self.content, text="", text_color="red", font=large_font)
        error_message.grid(row=3, column=0, pady=15)


        def rename_cluster(self) -> None:
            try:
                if root.rename_cluster(cluster.name, entry.get()):
                    root._load_clusters()
                    audio.play_accept()
                    ui.reload()
                    self.destroy()
                else:
                    audio.play_error()
                    error_message._text = "Hibás klaszter név!"
            except:
                error_message._text = "Adjon meg egy nevet!"
                audio.play_error()
