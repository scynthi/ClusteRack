import pygame
import ctypes
import os
import threading
import time
from customtkinter import *
from modules.ui import AppWindow
from modules.renderer.main import SoftwareRender

class EmbedRendererWindow(AppWindow):
    def __init__(self, app: CTk):
        super().__init__()

        self.app : CTk = app
        self.pygame_frame = CTkFrame(self.app, width=300, height=200)
        self.pygame_frame.grid(column=0, row=0)

        self.running : bool = True  
        self.thread : threading.Thread= threading.Thread(target=self.embed_pygame, daemon=True)
        self.thread.start()

    def embed_pygame(self):
        pygame.init()

        hwnd : int = self.pygame_frame.winfo_id()
        screen : pygame.display = pygame.display.set_mode((300, 200), pygame.SCALED)

        if os.name == "nt":
            ctypes.windll.user32.SetParent(pygame.display.get_wm_info()["window"], hwnd)
            
            style = ctypes.windll.user32.GetWindowLongW(pygame.display.get_wm_info()["window"], -16)
            style &= ~0x00C00000
            ctypes.windll.user32.SetWindowLongW(pygame.display.get_wm_info()["window"], -16, style)
            ctypes.windll.user32.SetWindowPos(pygame.display.get_wm_info()["window"], None, 0, 0, 300, 200, 0x0004)
            self.app.after(100, self.position_pygame_top_left)

        self.run_pygame_loop(screen)

    def position_pygame_top_left(self):
        hwnd : int= pygame.display.get_wm_info()["window"]

        ctypes.windll.user32.MoveWindow(hwnd, 0, 0, 0, 0, True)
        self.app.after(100, lambda: self.position_pygame_top_left())

    def run_pygame_loop(self, screen):
        renderer : SoftwareRender = SoftwareRender()
        while self.running:
            renderer.run()

            pygame.display.update()
            time.sleep(0.01)