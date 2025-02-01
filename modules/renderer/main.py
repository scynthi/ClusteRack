from modules.renderer.object import *
from modules.renderer.camera import *
from modules.renderer.projection import *
import pygame as pg


class SoftwareRender:
    def __init__(self):
        pg.init()
        self.RES = self.WIDTH, self.HEIGHT = 300, 200 
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 60
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.create_objects(r'Assets\Models\computer.obj')

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
        return Object3D(self, vertex, faces)

    def draw(self):
        self.screen.fill(pg.Color(235, 235, 235)) #Background Color
        self.object.draw()

    def run(self):
        while True:
            self.draw()
            # self.camera.control() ----------- Camera distance controls
            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            pg.display.set_caption("")
            pg.display.flip()
            self.clock.tick(self.FPS)

            # key = pg.key.get_pressed()
            # if key[pg.K_t]:
            #     self.create_objects(r'Assets\Models\rack.obj')
            # if key[pg.K_y]:
            #     self.create_objects(r'Assets\Models\computer.obj')