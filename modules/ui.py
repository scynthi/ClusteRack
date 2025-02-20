from customtkinter import *
from os import path as Path
from tkinter import *
from PIL import Image
from ctypes import windll
from modules.audio_manager import AudioManager 
from modules.renderer.main import SoftwareRender
import pygame
from threading import Thread
from matplotlib import font_manager
import matplotlib
import matplotlib.axes
import matplotlib.figure as figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from modules.computer import Computer

Thread(target=pygame.init, daemon=True).start()
audio : AudioManager = AudioManager()

set_appearance_mode("light")
deactivate_automatic_dpi_awareness()
set_widget_scaling(1)
FontManager.load_font(Path.join("Assets","Font", "VCR_OSD_MONO_1.001.ttf"))

font_entry : font_manager.FontEntry = font_manager.FontEntry(fname=Path.join("Assets","Font", "VCR_OSD_MONO_1.001.ttf"), name="VCR OSD MONO")
font_manager.fontManager.ttflist.insert(0, font_entry)
matplotlib.rcParams["font.family"] = font_entry.name


extra_large_font : tuple = ("VCR OSD MONO", 30)
larger_font : tuple = ("VCR OSD MONO", 25)
large_font : tuple = ("VCR OSD MONO", 15)
bold_large_font : tuple = ("VCR OSD MONO", 15, "bold")
small_font : tuple = ("VCR OSD MONO", 12)

LBLUE : str = "#0066ff"
DBLUE : str = "#0052cc"
LGRAY : str = "#cdcdcd"
DGRAY : str = "#adadad"


class AppWindow(CTk):
    def __init__(self, size="800x600", name="ClusteRack"):
        super().__init__()
        self.iconbitmap(Path.join("Assets", "Images", "logo.ico"))
        self.overrideredirect(True)
        self.geometry(size)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.config(bg=DGRAY)
        self.minimized : bool = False
        self.maximized : bool = False
        self.normal_size = self.geometry()


        self.title_bar : CTkFrame = Frame(self, bg=DBLUE, relief='raised', border=4)
        self.title_bar.grid_columnconfigure([1,2], weight=1)
        self.title_bar.bind('<Button-1>', self.get_pos)
        self.title_bar.grid(row=0, column=0, sticky="new")


        program_logo : CTkImage = CTkImage(light_image=Image.open(Path.join("Assets", "Images", "logo.png")), size=(40,40))
        logo_label : CTkLabel = CTkLabel(self.title_bar, image=program_logo, text="")
        logo_label.grid(row=0, column=0, sticky="nw", padx=10)


        self.title_bar_title : UI.Label = UI.Label(self.title_bar, text=name, text_color='white', font=("VCR OSD MONO", 20))
        self.title_bar_title.bind('<Button-1>', self.get_pos)
        self.title_bar_title.grid(row=0, column=1, sticky="nw", padx=10, pady=5)


        self.close_button : UI.Button = UI.Button(self.title_bar, text=' X ', command=lambda: os._exit(0), padx=2, pady=2)
        self.expand_button : UI.Button= UI.Button(self.title_bar, text=' 🗖 ', command=self.maximize_me, padx=2, pady=2)
        self.minimize_button : UI.Button = UI.Button(self.title_bar, text=' 🗕 ', command=self.minimize_me, padx=2, pady=2)
        self.reload_button : UI.Button = UI.Button(self.title_bar, text=' ⟳ ', padx=2, pady=2)
        self.cli_button : UI.Button = UI.Button(self.title_bar, text=' >_ ', padx=2, pady=2)

        self.cli_button.grid(row=0, column=2, sticky="ne", padx=7, pady=1)
        self.reload_button.grid(row=0, column=3, sticky="ne", padx=7, pady=1)
        self.minimize_button.grid(row=0, column=4, sticky="ne", padx=7, pady=1)
        self.expand_button.grid(row=0, column=5, sticky="ne", padx=7, pady=1)
        self.close_button.grid(row=0, column=6, sticky="ne", padx=7, pady=1)


        self.content : Frame = Frame(self, bg=DGRAY)
        self.content.grid(row=1, column=0, sticky="nsew")


        resizey_widget : Frame = Frame(self, cursor='sb_v_double_arrow', width=10)
        resizey_widget.grid(row=1, column=0, sticky="SEW")
        resizey_widget.bind("<B1-Motion>", self.resizey)

        resizex_widget : Frame = Frame(self, cursor='sb_h_double_arrow', height=10)
        resizex_widget.grid(row=1, column=1, sticky="NSE")
        resizex_widget.bind("<B1-Motion>", self.resizex)


        self.bind("<FocusIn>", self.deminimize)
        self.after(10, self.set_appwindow)
        self.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))

    def set_appwindow(self) -> None:
        GWL_EXSTYLE : int = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        
        hwnd = windll.user32.GetParent(self.winfo_id())
        stylew = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        stylew = stylew & ~WS_EX_TOOLWINDOW
        stylew = stylew | WS_EX_APPWINDOW

        self.wm_withdraw()
        self.after(10, lambda: self.wm_deiconify())


    def minimize_me(self) -> None:
        self.attributes("-alpha", 0)
        self.minimized = True 


    def deminimize(self, event) -> None:
        self.focus()
        self.attributes("-alpha", 1)
        if self.minimized == True:
            self.minimized = False


    def maximize_me(self) -> None:
        if self.maximized == False:
            self.normal_size = self.geometry()
            self.expand_button.config(text=" 🗗 ")
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
            self.maximized = not self.maximized
        else:
            self.expand_button.config(text=" 🗖 ")
            if self.normal_size == f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0":
                self.geometry("800x500+0+0")
            else:
                self.geometry(self.normal_size)
            self.maximized = not self.maximized


    def get_pos(self, event) -> None:
        if self.maximized == False:
            xwin : int = self.winfo_x()
            ywin : int = self.winfo_y()
            startx : int = event.x_root
            starty : int = event.y_root

            ywin : int = ywin - starty
            xwin : int = xwin - startx

            def move_window(event) -> None:
                if self.winfo_width() == self.winfo_screenwidth():
                    self.maximized = True
                    self.maximize_me()

                self.config(cursor="fleur")
                self.geometry(f'+{event.x_root + xwin}+{event.y_root + ywin}')

            def release_window(event) -> None:
                self.config(cursor="arrow")

            self.title_bar.bind('<B1-Motion>', move_window)
            self.title_bar.bind('<ButtonRelease-1>', release_window)
            self.title_bar_title.bind('<B1-Motion>', move_window)
            self.title_bar_title.bind('<ButtonRelease-1>', release_window)
        else:
            self.expand_button.config(text=" 🗖 ")
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


class UI:
    def __init__(self):
        self.LGRAY = LGRAY
        self.LBLUE = LBLUE
        self.DBLUE = DBLUE
        self.DGRAY = DGRAY

    class Button(Button):
        def __init__(self, master : AppWindow, text : str, fg_color : str = "black", bg_color : str = "white", font : tuple = small_font, **kwargs):
            super().__init__(master, 
                             text=text,
                             background=bg_color,
                             foreground=fg_color,
                             font=font,
                             borderwidth=6,
                             **kwargs)
            self.bind("<ButtonPress-1>", lambda event: audio.play_rnd_click())

    class Label(CTkLabel):
        def __init__(self, master, text : str, text_color : str="black", font : tuple = large_font, **kwargs):
            super().__init__(master, 
                             text=text, 
                             text_color=text_color, 
                             font=font,
                             **kwargs)
            
    class Frame(Frame):
        def __init__(self, master, bg_color : str=LGRAY, height: int = 200,  borderwidth : int = 4, **kwargs):
            super().__init__(master, bg=bg_color, height=height, borderwidth=borderwidth, relief="raised", **kwargs)

    class OptionMenu(CTkComboBox):
        def __init__(self, master, values : list, **kwargs):
            super().__init__(master,
                             values=values,
                             font=large_font,
                             bg_color=DGRAY,
                             fg_color=LGRAY,
                             text_color="black",
                             button_color="gray",
                             button_hover_color=LGRAY,
                             dropdown_font=large_font,
                             dropdown_fg_color=DGRAY,
                             corner_radius=0,
                             border_width=2,
                             border_color="gray",
                             state="readonly",
                             **kwargs)

    class Entry(Entry):
        def __init__(self, master, font : tuple=large_font, bg : str=LGRAY, fg : str="black", borderwidth : int=4, **kwargs):
            super().__init__(master,
                             font=font,
                             bg=bg,
                             fg=fg,
                             borderwidth=borderwidth,
                             relief="sunken",
                             **kwargs)

    class EmbedRenderer:
        def __init__(self, frame, model_name, zoom_amount, root):
            self.frame = frame
            self.model_name : str = model_name
            self.zoom_amount : int = zoom_amount
            self.root = root

        def get_renderer(self) -> SoftwareRender:
            return SoftwareRender(self.model_name, self.zoom_amount, self.frame, self.root)
    

    class Plot():
        def __init__(self, computer : Computer, frame : Frame, title : str, property : str) -> None:
            self.title : str = title
            self.frame : UI.Frame = frame
            self.computer : Computer = computer
            self.property : str = property

            self.fig: figure.Figure = figure.Figure(figsize=(3, 3), facecolor=LGRAY)
            self.canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(self.fig, self.frame)
            self.canvas.get_tk_widget().grid(column=0, row=0)
            self.ax: matplotlib.axes._axes.Axes = self.fig.add_subplot()

            self.time_count: list = [0]
            self.usage_list: list = [0]
            self.add_point_to_plot()

        def add_point_to_plot(self) -> None:
            try:
                self.ax.clear()
                self.ax.set_ylim(0, 100)
                self.ax.set_xlim(0, 30)
                self.ax.set_title(self.title)


                if len(self.time_count) == 30:
                    last_usage: float = self.usage_list[-1]

                    self.usage_list.clear()
                    self.time_count.clear()

                    self.usage_list.append(last_usage)
                    self.time_count.append(1)


                usage: int = self.computer.calculate_resource_usage()[self.property]
                if usage == 100:
                    usage = 99
                self.usage_list.append(usage)
                self.time_count.append(int(self.time_count[-1]+1))

                self.ax.plot(self.time_count, self.usage_list, color=LBLUE)
                self.canvas.draw()
                
                self.frame.after(400, self.add_point_to_plot)
            except: pass

