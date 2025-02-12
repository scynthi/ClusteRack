import tkinter as tk
import pygame as pg
import math
from PIL import Image, ImageTk
from modules.renderer.object import Object3D
from modules.renderer.camera import Camera
from modules.renderer.projection import Projection

class SoftwareRender:
    def __init__(self, model, zoom_amount, frame, root):
        self.RES = self.WIDTH, self.HEIGHT = 300, 200  # Full resolution
        self.SCALED_RES = (self.WIDTH * 2, self.HEIGHT * 2)

        self.FPS = 60
        self.zoom_amount = zoom_amount
        self.root = root
        self.window_moving = False
        self.frame = frame  
        self.canvas = tk.Canvas(frame, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.screen = pg.Surface(self.SCALED_RES)  # Render 2 times the size

        self.clock = pg.time.Clock()
        self.running = True
        self.tk_image = None  
        self.create_objects(f"Assets/Models/{model}.obj")
        self.root.bind("<Configure>", self.on_window_move)
        self.update()

    def create_objects(self, new_object_path):
        self.camera = Camera(self, self.zoom_amount)
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
        """The update loop of the rederer"""
        if not self.running or self.window_moving:
            self.root.after(50, self.update)
            return

        self.screen.fill(pg.Color(235, 235, 235))
        self.object.draw()
        self.update_tkinter_canvas()
        self.clock.tick(self.FPS)
        self.root.after(16, self.update)

    def update_tkinter_canvas(self):
        """Convert Pygame surface to an image"""
        pg_image_data = pg.image.tostring(self.screen, "RGB")
        pg_image = Image.frombytes("RGB", self.SCALED_RES, pg_image_data)

        # Scale it up to match the expected display size
        pg_image = pg_image.resize(self.RES, Image.BILINEAR)

        self.tk_image = ImageTk.PhotoImage(pg_image)  
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def on_window_move(self, event):
        if event.widget == self.root:
            self.window_moving = True
            self.root.after(200, self.reset_window_move_flag)  # Reset after 200ms

    def reset_window_move_flag(self):
        self.window_moving = False
