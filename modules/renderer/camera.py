import pygame as pg
import numpy as np
import math
from modules.renderer.matrixfunctions import *

class Camera:
    def __init__(self, render, position):
        self.render = render
        self.min_distance = 2.0
        self.max_distance = 50.0
        self.position = np.array([*position, 1.0])
        
        self._clamp_distance()
        
        self.forward = np.array([0, 0, 1, 1])
        self.up = np.array([0, 1, 0, 1])
        self.right = np.array([1, 0, 0, 1])
        self.h_fov = math.pi / 3
        self.v_fov = self.h_fov * (render.HEIGHT / render.WIDTH)
        self.near_plane = 0.1
        self.far_plane = 100
        self.moving_speed = 0.3
        self.rotation_speed = 0.015

    def control(self):
        key = pg.key.get_pressed()
        if key[pg.K_a]:
            self.position -= self.right * self.moving_speed
        if key[pg.K_d]:
            self.position += self.right * self.moving_speed
        if key[pg.K_w]:
            self.position += self.forward * self.moving_speed
        if key[pg.K_s]:
            self.position -= self.forward * self.moving_speed
        if key[pg.K_q]:
            self.position += self.up * self.moving_speed
        if key[pg.K_e]:
            self.position -= self.up * self.moving_speed

        # Apply distance constraints after movement
        self._clamp_distance()

    def _clamp_distance(self):
        pos = self.position[:3]
        distance = np.linalg.norm(pos)
        
        if distance < self.min_distance:
            direction = pos / distance if distance != 0 else np.array([0, 0, -1])
            self.position[:3] = direction * self.min_distance
        elif distance > self.max_distance:
            direction = pos / distance
            self.position[:3] = direction * self.max_distance

    def camera_update_axii(self):
        position = self.position[:3]
        target = np.array([0, 0, 0])
        
        forward = target - position
        forward_normalized = forward / np.linalg.norm(forward)
        
        world_up = np.array([0, 1, 0])
        right = np.cross(forward_normalized, world_up)
        right_normalized = right / np.linalg.norm(right)
        
        up_normalized = np.cross(right_normalized, forward_normalized)
        
        self.forward = np.append(forward_normalized, 1.0)
        self.right = np.append(right_normalized, 1.0)
        self.up = np.append(up_normalized, 1.0)

    def camera_matrix(self):
        self.camera_update_axii()
        return self.translate_matrix() @ self.rotate_matrix()

    def translate_matrix(self):
        x, y, z, w = self.position
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [-x, -y, -z, 1]
        ])

    def rotate_matrix(self):
        rx, ry, rz, _ = self.right
        ux, uy, uz, _ = self.up
        fx, fy, fz, _ = self.forward
        return np.array([
            [rx, ux, fx, 0],
            [ry, uy, fy, 0],
            [rz, uz, fz, 0],
            [0, 0, 0, 1]
        ])