import pygame
import ctypes
import os
import threading
from customtkinter import *
from modules.renderer.main import SoftwareRender

class EmbedRendererWindow:
    def __init__(self, app: CTkFrame, model_name : str) -> None:
        pygame.display.init()
        #super().__init__()
        
        self.app : CTkFrame = app
        self.pygame_frame : CTkFrame = CTkFrame(app)
        self.model_name : str = model_name

        threading.Thread(target=self.embed_pygame, daemon=True).start()
        

    def embed_pygame(self) -> None:
        screen : pygame.display = pygame.display
        screen_mode = screen.set_mode((300, 200), 0, 32)
        screen_wm_info = screen.get_wm_info()["window"]

        if os.name == "nt":
            ctypes.windll.user32.SetParent(screen_wm_info, self.pygame_frame.winfo_id())
            ctypes.windll.user32.SetWindowPos(screen_wm_info, None, 0, 0, 300, 200, 0x0004)
            style = ctypes.windll.user32.GetWindowLongW(screen_wm_info, -16)
            style &= ~0x00C00000
            ctypes.windll.user32.SetWindowLongW(screen_wm_info, -16, style)
            self.app.after(100, lambda: ctypes.windll.user32.MoveWindow(screen_wm_info, 0, 0, 0, 0, True))

        renderer : SoftwareRender = SoftwareRender(self.model_name, screen_mode)
        renderer.update()

        

            
            