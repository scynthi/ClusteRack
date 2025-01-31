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
        screen = pygame.display.set_mode((600, 400), pygame.NOFRAME)

        if os.name == "nt":
            ctypes.windll.user32.SetParent(pygame.display.get_wm_info()["window"], hwnd)
            self.after(100, self.position_pygame_top_left)

        self.run_pygame_loop(screen)

    def position_pygame_top_left(self):
        hwnd = pygame.display.get_wm_info()["window"]
        frame_x, frame_y = self.pygame_frame.winfo_rootx(), self.pygame_frame.winfo_rooty()

        ctypes.windll.user32.MoveWindow(hwnd, frame_x, frame_y, 600, 400, True)

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