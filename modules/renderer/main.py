import tkinter as tk
import pygame as pg
import math
from PIL import Image, ImageTk
from modules.renderer.object import Object3D
from modules.renderer.camera import Camera
from modules.renderer.projection import Projection


class SoftwareRender:
    def __init__(self, model, frame, root):
        self.RES = self.WIDTH, self.HEIGHT = 300, 200
        self.FPS = 60
        self.root = root
        self.window_moving = False
        self.frame = frame  
        self.canvas = tk.Canvas(frame, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        pg.init()
        self.screen = pg.Surface(self.RES)
        self.clock = pg.time.Clock()
        self.running = True
        self.tk_image = None  
        self.create_objects(f"Assets/Models/{model}.obj")
        self.root.bind("<Configure>", self.on_window_move)
        self.update()

    def create_objects(self, new_object_path):
        self.camera = Camera(self, [-15, 0, -15])
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
        if not self.running or self.window_moving:
            self.root.after(50, self.update)
            return

        self.screen.fill(pg.Color(235, 235, 235))
        self.object.draw()
        self.update_tkinter_canvas()
        self.clock.tick(self.FPS)
        self.root.after(16, self.update)

    def update_tkinter_canvas(self):
        pg_image_data = pg.image.tostring(self.screen, "RGB")
        pg_image = Image.frombytes("RGB", self.RES, pg_image_data)

        self.tk_image = ImageTk.PhotoImage(pg_image)  
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def on_window_move(self, event):
        if event.widget == self.root:
            self.window_moving = True
            self.root.after(200, self.reset_window_move_flag)  # Reset after 200ms

    def reset_window_move_flag(self):
        self.window_moving = False
