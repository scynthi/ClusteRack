import tkinter as tk
import os, pygame

root = tk.Tk()
embed_pygame = tk.Frame(root, width = 500, height = 500)
embed_pygame.pack(side = tk.TOP)

os.environ['SDL_WINDOWID'] = str(embed_pygame.winfo_id())
os.environ['SDL_VIDEODRIVER'] = 'windib'
pygame.display.init()
screen = pygame.display.set_mode()

def pygame_loop():
    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, "red", (250, 250), 125)
    pygame.display.flip()
    root.update()
    root.after(100, pygame_loop)

pygame_loop()
tk.mainloop()

