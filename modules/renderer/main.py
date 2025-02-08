from modules.renderer.object import *
from modules.renderer.camera import *
from modules.renderer.projection import *
from os import path as Path
import pygame as pygame


class SoftwareRender:
    def __init__(self, model, screen):
        self.RES = self.WIDTH, self.HEIGHT = 300, 200 
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 60
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True  # Flag to keep track of loop status
        self.create_objects(f"Assets/Models/{model}.obj")

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
        while True:
            self.screen.fill(pygame.Color(235, 235, 235))  # Background Color
            self.object.draw()

            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            pygame.display.flip()
            self.clock.tick(self.FPS)

            
            
