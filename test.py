import pygame
import ctypes
import os
import threading
import time
import customtkinter as ctk
from modules.ui import AppWindow
from modules.renderer.main import SoftwareRender

class PygameEmbedApp(AppWindow):
    def __init__(self):
        super().__init__()

        self.pygame_frame = ctk.CTkFrame(self, width=600, height=400)
        self.pygame_frame.grid(column=0, row=0)

        self.running = True  
        self.thread = threading.Thread(target=self.embed_pygame, daemon=True)
        self.thread.start()

    def embed_pygame(self):
        pygame.init()

        hwnd = self.pygame_frame.winfo_id()
        screen = pygame.display.set_mode((600, 400), pygame.SCALED)

        if os.name == "nt":
            ctypes.windll.user32.SetParent(pygame.display.get_wm_info()["window"], hwnd)
            
            style = ctypes.windll.user32.GetWindowLongW(pygame.display.get_wm_info()["window"], -16)
            style &= ~0x00C00000
            ctypes.windll.user32.SetWindowLongW(pygame.display.get_wm_info()["window"], -16, style)
            ctypes.windll.user32.SetWindowPos(pygame.display.get_wm_info()["window"], None, 0, 0, 600, 400, 0x0004)
            self.after(100, self.position_pygame_top_left)

        self.run_pygame_loop(screen)

    def position_pygame_top_left(self):
        hwnd = pygame.display.get_wm_info()["window"]

        ctypes.windll.user32.MoveWindow(hwnd, 0, 0, 0, 0, True)
        self.after(100, lambda: app.position_pygame_top_left())

    def run_pygame_loop(self, screen):
        app = SoftwareRender()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return

            app.run()

            pygame.display.update()
            time.sleep(0.01)

if __name__ == "__main__":
    app = PygameEmbedApp()
    app.mainloop()


