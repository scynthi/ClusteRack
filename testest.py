import tkinter as tk
import pygame as pg
import os
import sys
import math
from PIL import Image, ImageTk

from modules.renderer.object import Object3D
from modules.renderer.camera import Camera
from modules.renderer.projection import Projection


class SoftwareRender:
    def __init__(self, model, frame, root):
        self.RES = self.WIDTH, self.HEIGHT = 300, 200
        self.FPS = 60
        self.root = root  # Tkinter root for scheduling updates
        self.window_moving = False  # 🔥 Detect window movement

        # Tkinter frame where we embed the renderer
        self.frame = frame  

        # Create a Tkinter canvas for rendering
        self.canvas = tk.Canvas(frame, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.grid(row=0, column=0, sticky="nsew")  # 🔥 Use grid system

        # Initialize Pygame but don't create a new window
        pg.init()
        self.screen = pg.Surface(self.RES)  # Off-screen Pygame surface

        self.clock = pg.time.Clock()
        self.running = True

        # Store image reference to prevent garbage collection
        self.tk_image = None  

        # Load 3D model
        self.create_objects(f"Assets/Models/{model}.obj")

        # 🔥 Detect window movement to prevent crashing
        self.root.bind("<Configure>", self.on_window_move)

        # 🔥 Use Tkinter's `after()` for smooth updates
        self.update()

    def create_objects(self, new_object_path):
        self.camera = Camera(self, [0, 1, -10])
        self.projection = Projection(self)
        self.object = self.get_object_from_file(new_object_path)
        self.object.rotate_y(-math.pi / 4)

    def get_object_from_file(self, filename):
        vertex, faces = [], []

        with open(filename) as f:
            for line in f:
                if line.startswith('v '):
                    vertex.append([float(i) for i in line.split()[1:]] + [1])
                elif line.startswith('f'):
                    faces_ = line.split()[1:]
                    faces.append([int(face_.split('/')[0]) - 1 for face_ in faces_])
            f.close()

        return Object3D(self, vertex, faces)

    def update(self):
        """Pygame loop running using Tkinter's `after()` to prevent UI freezing."""
        if not self.running or self.window_moving:
            self.root.after(50, self.update)  # 🔥 Reduce updates while moving window
            return

        # Render scene
        self.screen.fill(pg.Color(235, 235, 235))  # Background color
        self.object.draw()  # Render 3D model

        # Convert Pygame surface to Tkinter image
        self.update_tkinter_canvas()

        # Handle Pygame events
        # for event in pg.event.get():
        #     if event.type == pg.QUIT:
        #         self.running = False
        #         pg.quit()
        #         sys.exit()

        self.clock.tick(self.FPS)

        # 🔥 Schedule next update using Tkinter `after()`
        self.root.after(16, self.update)

    def update_tkinter_canvas(self):
        """Converts Pygame surface to a Tkinter-compatible image."""
        # 🔥 Use faster Pygame to Tkinter conversion (NO `surfarray` overhead)
        pg_image_data = pg.image.tostring(self.screen, "RGB")  # Convert Pygame surface to bytes
        pg_image = Image.frombytes("RGB", self.RES, pg_image_data)  # Convert bytes to PIL Image

        # 🔥 Store a reference to prevent garbage collection
        self.tk_image = ImageTk.PhotoImage(pg_image)  

        # Update Tkinter canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def on_window_move(self, event):
        """Detects when the window is moving to prevent crashes."""
        if event.widget == self.root:
            self.window_moving = True
            self.root.after(200, self.reset_window_move_flag)  # Reset after 200ms

    def reset_window_move_flag(self):
        """Restores rendering after the window stops moving."""
        self.window_moving = False


def create_renderer(frame, model_name, root):
    """Creates a SoftwareRender instance inside a Tkinter frame."""
    return SoftwareRender(model_name, frame, root)


# Tkinter UI
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("3D Renderer in Tkinter")
        self.geometry("700x500")

        # Create a container frame using grid
        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")

        # Configure grid for responsiveness
        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=1)
        self.container.rowconfigure(0, weight=1)

        # Create two separate renderers using grid
        self.frame1 = tk.Frame(self.container, width=300, height=200, bg="black")
        self.frame1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame2 = tk.Frame(self.container, width=300, height=200, bg="black")
        self.frame2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Start renderers using `after()` for smooth updates
        self.renderer1 = create_renderer(self.frame1, "rack_1", self)
        self.renderer2 = create_renderer(self.frame2, "rack_2", self)


if __name__ == "__main__":
    app = App()
    app.mainloop()
