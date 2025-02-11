from customtkinter import *
from os import path as Path
from tkinter import *
from PIL import Image
from ctypes import windll
from modules.audio_manager import AudioManager 
from modules.renderer.main import SoftwareRender
import pygame
from threading import Thread

Thread(target=pygame.init, daemon=True).start()
audio : AudioManager = AudioManager()


extra_large_font : tuple = ("VCR OSD MONO", 30)
large_font : tuple = ("VCR OSD MONO", 15)
small_font : tuple = ("VCR OSD MONO", 12)

LBLUE : str = "#0066ff"
DBLUE : str = "#0052cc"
LGRAY : str = "#cdcdcd"
DGRAY : str = "#adadad"


class AppWindow(CTk):
    def __init__(self, size="800x600", name="ClusteRack") -> None:
        set_appearance_mode("light")
        deactivate_automatic_dpi_awareness()
        set_widget_scaling(1)
        super().__init__()
        FontManager.load_font(Path.join("Assets","Font", "VCR_OSD_MONO_1.001.ttf"))
        self.iconbitmap(Path.join("Assets", "Images", "logo.ico"))
        self.overrideredirect(True)
        self.geometry(size)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.config(bg=DGRAY)
        self.minimized : bool = False
        self.maximized : bool = False
        self.normal_size = self.geometry()


        title_bar : CTkFrame = Frame(self, bg=DBLUE, relief='raised', border=4)
        title_bar.grid_columnconfigure([1,2], weight=1)
        title_bar.bind('<Button-1>', self.get_pos)
        title_bar.grid(row=0, column=0, sticky="new")


        close_button : UI.Button = UI.Button(title_bar, text=' X ', fg_color="white", command=lambda: os._exit(0), padx=2, pady=2)
        expand_button : UI.Button= UI.Button(title_bar, text=' 🗖 ', fg_color="white", command=self.maximize_me, padx=2, pady=2)
        minimize_button : UI.Button = UI.Button(title_bar, text=' 🗕 ', fg_color="white", command=self.minimize_me, padx=2, pady=2)

        program_logo : CTkImage = CTkImage(light_image=Image.open(Path.join("Assets", "Images", "logo.png")), size=(40,40))
        
        logo_label : CTkLabel = CTkLabel(title_bar, image=program_logo, text="")
        logo_label.grid(row=0, column=0, sticky="nw", padx=10)


        title_bar_title : UI.Label = UI.Label(title_bar, text=name, text_color='white', font=("VCR OSD MONO", 20))
        title_bar_title.bind('<Button-1>', self.get_pos)
        title_bar_title.grid(row=0, column=1, sticky="nw", padx=10, pady=5)


        minimize_button.grid(row=0, column=2, sticky="ne", padx=7, pady=1)
        expand_button.grid(row=0, column=3, sticky="ne", padx=7, pady=1)
        close_button.grid(row=0, column=4, sticky="ne", padx=7, pady=1)


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
        self.expand_button : Frame = expand_button
        self.minimize_button : Frame = minimize_button
        self.title_bar_title : Frame = title_bar_title
        self.content : Frame = content

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
        def __init__(self, master : AppWindow, text : str, fg_color : str = DGRAY, bg_color : str = LBLUE, **kwargs) -> None:
            super().__init__(master, 
                             text=text,
                             background="white",
                             foreground="black",
                             font=small_font,
                             borderwidth=6,
                             **kwargs)
            self.bind("<ButtonPress-1>", lambda event: audio.play_rnd_click())

    class Label(CTkLabel):
        def __init__(self, master, text, text_color="black", font : tuple = large_font, **kwargs) -> None:
            super().__init__(master, 
                             text=text, 
                             text_color=text_color, 
                             font=font,
                             **kwargs)
            
    class Frame(Frame):
        def __init__(self, master, bg_color=LGRAY, height: int = 200, **kwargs):
            super().__init__(master,  bg=bg_color, height=height, borderwidth=4, relief="raised", **kwargs)


    class EmbedRenderer:
        def __init__(self, frame, model_name, zoom_amount, root):
            self.frame = frame
            self.model_name = model_name
            self.zoom_amount = zoom_amount
            self.root = root

        def get_renderer(self):
            return SoftwareRender(self.model_name, self.zoom_amount, self.frame, self.root)
