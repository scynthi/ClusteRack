import pygame
import ctypes
import os
import threading
import time
import customtkinter as ctk
from modules.ui import AppWindow

ctk.set_appearance_mode("dark")


class PygameEmbedApp(AppWindow):
    def __init__(self):
        super().__init__()

        self.pygame_frame = ctk.CTkFrame(self, width=600, height=400)
        self.pygame_frame.grid(row=0, column=0)

        self.thread = threading.Thread(target=self.embed_pygame, daemon=True)
        self.thread.start()

    def embed_pygame(self):
        os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"

        pygame.init()

        hwnd = self.pygame_frame.winfo_id()
        screen = pygame.display.set_mode((600, 400), pygame.NOFRAME)

        if os.name == "nt":
            ctypes.windll.user32.SetParent(pygame.display.get_wm_info()["window"], hwnd)

        self.run_pygame_loop(screen)

    def run_pygame_loop(self, screen):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((30, 30, 30))
            pygame.draw.circle(screen, (255, 0, 0), (300, 200), 50)

            pygame.display.update()
            time.sleep(0.01)

        pygame.quit()

if __name__ == "__main__":
    app = PygameEmbedApp()
    app.mainloop()