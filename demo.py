#!/usr/bin/env python
# encoding: utf-8

import random
import sys
from math import sin, cos, pi
import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtOpenGL
from PyQt4.QtOpenGL import QGLShader, QGLShaderProgram

import OpenGL
OpenGL.ERROR_CHECKING = True
OpenGL.ERROR_LOGGING = True
OpenGL.FULL_LOGGING = True
from OpenGL.GL import *
from OpenGL.GLU import *

import numpy

from renderer import VertexBuffer

def normalize(vec):
    return vec / numpy.sqrt(numpy.sum(vec**2))

def clamp(value, min, max):
    if value < min:
        return min
    if value > max:
        return max
    return value

def normal_from_points(p1, p2, p3):
    if isinstance(p1, (list, tuple)):
        v1 = [p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]]
        v2 = [p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2]]
    else:
        v1 = p2 - p1
        v2 = p3 - p1
    return normalize(numpy.cross(v1, v2))

def parse_obj(file_name):
    lines = open(file_name).readlines()
    normals_lines =  filter(lambda line: line.startswith('vn'), lines)
    vertices_lines = filter(lambda line: line.startswith('v'), lines)
    faces_lines =    filter(lambda line: line.startswith('f'), lines)
    normals =  [map(float, line.split()[1:]) for line in normals_lines]
    vertices = [map(float, line.split()[1:]) for line in vertices_lines]
    if len(normals) > 0:
        pattern = r'f (\d+)//(\d+) (\d+)//(\d+) (\d+)//(\d+)'
        faces = [map(int, re.match(pattern, line).groups()) for line in faces_lines]
        triangles = [[vertices[face[0]-1],
                      vertices[face[2]-1],
                      vertices[face[4]-1],
                      normals[face[1]-1],
                      normals[face[3]-1],
                      normals[face[5]-1]] for face in faces]
    else:
        faces = [map(int, line.split()[1:]) for line in faces_lines]
        triangles = []
        for face in faces:
            v0 = vertices[face[0]-1]
            v1 = vertices[face[1]-1]
            v2 = vertices[face[2]-1]
            normal = normal_from_points(v0, v1, v2)
            triangles.append([v0, v1, v2, normal, normal, normal])
    return triangles

def weighted_choice(weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

def triangle_area(v0, v1, v2):
    '''Heron's formula'''
    v0 = numpy.array(v0)
    v1 = numpy.array(v1)
    v2 = numpy.array(v2)
    a = sum((v0-v1)**2)**0.5
    b = sum((v0-v2)**2)**0.5
    c = sum((v1-v2)**2)**0.5
    s = (a+b+c) / 2.
    return (s*(s-a)*(s-b)*(s-c))**0.5

class Demo(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
        self.setMouseTracking(True)
        self.grabKeyboard()
        self.setCursor(Qt.BlankCursor)

        self.camera_position = QVector3D(-5, 5, -5)
        self.camera_direction = QVector3D(-0.2, -0.8, 0.2).normalized()
        self.yaw = self.pitch = 0
        self.moving_forward = False
        self.moving_backwards = False
        self.moving_left = False
        self.moving_right = False

    def resizeGL(self, width, height):
        pass

    def initializeGL(self):
        self.makeCurrent()

        # Timer used to measure frame time.
        self.timer = QElapsedTimer()
        self.timer.start()

        # Time since the beginning.
        self.time = QElapsedTimer()
        self.time.start()

        glClearColor(0., 0., 0., 0.)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glDisable(GL_CULL_FACE)
        glEnable(GL_MULTISAMPLE)

        triangles = parse_obj('house.obj')
        areas = [triangle_area(v0, v1, v2) for v0, v1, v2, _, _, _ in triangles]

        data = []
        for v0, v1, v2, n0, n1, n2 in triangles:
            data.extend(v0)
            data.extend(n0)
            data.extend(v1)
            data.extend(n1)
            data.extend(v2)
            data.extend(n2)

        self.house_buffer = VertexBuffer(numpy.array(data, numpy.float32), [(3, GL_FLOAT), (3, GL_FLOAT)])
        self.house_shader = QGLShaderProgram()
        self.house_shader.addShaderFromSourceFile(QGLShader.Vertex, 'house.vs')
        self.house_shader.addShaderFromSourceFile(QGLShader.Fragment, 'house.fs')
        self.house_shader.bindAttributeLocation('position', 0)
        self.house_shader.bindAttributeLocation('normal', 1)
        glBindFragDataLocation(self.house_shader.programId(), 0, 'FragColor')
        if not self.house_shader.link():
            print('Failed to link house shader!')

        ## Make a house out of points
        data = []
        num_points = 100*1000
        for p in range(num_points):
            # Select random triangle based on their sizes (larger ones
            # are more likely to be chosen - guarantees uniform distribution)
            random_triangle = triangles[weighted_choice(areas)]
            v0, v1, v2, n0, n1, n2 = map(numpy.array, random_triangle)
            # Select a random point inside triangle using barycentric coordinates:
            a = random.random()
            b = random.random()
            if a+b > 1.:
                a = 1-a
                b = 1-b
            c = 1-a-b
            point = a*v0 + b*v1 + c*v2
            normal = n0
            data.extend(point)
            data.extend(normal)

        self.grass_buffer = VertexBuffer(numpy.array(data, numpy.float32), [(3, GL_FLOAT), (3, GL_FLOAT)])

        self.grass_shader = QGLShaderProgram()
        self.grass_shader.addShaderFromSourceFile(QGLShader.Geometry, 'grass.gs')
        self.grass_shader.addShaderFromSourceFile(QGLShader.Vertex, 'grass.vs')
        self.grass_shader.addShaderFromSourceFile(QGLShader.Fragment, 'grass.fs')
        self.grass_shader.bindAttributeLocation('position', 0)
        self.grass_shader.bindAttributeLocation('normal', 1)
        glBindFragDataLocation(self.grass_shader.programId(), 0, 'FragColor')

        if not self.grass_shader.link():
            print('Failed to link grass shader!')

    def paintGL(self):
        self.makeCurrent()

        speed = 0.005 * self.timer.restart()
        if self.moving_forward:
            self.camera_position += self.camera_direction * speed
        if self.moving_backwards:
            self.camera_position -= self.camera_direction * speed
        if self.moving_left:
            self.camera_position -= QVector3D.crossProduct(self.camera_direction, QVector3D(0, 1, 0)).normalized() * speed
        if self.moving_right:
            self.camera_position += QVector3D.crossProduct(self.camera_direction, QVector3D(0, 1, 0)).normalized() * speed

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        projection = QMatrix4x4()
        projection.perspective(60., float(self.width()) / self.height(), 1., 500.)

        modelview = QMatrix4x4()
        modelview.lookAt(self.camera_position,
                         self.camera_position+self.camera_direction,
                         QVector3D(0, 1, 0))

        translation = QMatrix4x4()
        translation.translate(0, 1, 0)

        ## Solid geometry
        self.house_shader.bind()
        self.house_shader.setUniformValue('projection', projection)
        self.house_shader.setUniformValue('modelview', modelview * translation)
        self.house_buffer.draw()
        self.house_shader.release()

        ## Grass on top
        self.grass_shader.bind()
        self.grass_shader.setUniformValue('projection', projection)
        self.grass_shader.setUniformValue('modelview', modelview * translation)
        self.grass_shader.setUniformValue('time', float(self.time.elapsed()))
        self.grass_buffer.draw(GL_POINTS)
        self.grass_shader.release()

        self.draw_grid(projection, modelview)

        self.update()

    def draw_grid(self, projection, modelview):
        if not hasattr(self, 'grid_buffer'):
            unit = 1.
            count = 20
            data = []
            for i in range(-count, count+1):
                data.extend([-count*unit, 0, i*unit,
                              count*unit, 0, i*unit])
                data.extend([i*unit, 0, -count*unit,
                             i*unit, 0,  count*unit])
            self.grid_buffer = VertexBuffer(numpy.array(data, numpy.float32), [(3, GL_FLOAT)])

            self.grid_shader = QGLShaderProgram()
            self.grid_shader.addShaderFromSourceCode(QGLShader.Vertex,
                '''#version 330
                in vec3 position;

                uniform mat4 projection, modelview;

                void main()
                {
                    gl_Position = projection * modelview * vec4(position, 1.);
                }
                ''')
            self.grid_shader.addShaderFromSourceCode(QGLShader.Fragment,
                '''#version 330

                out vec4 FragColor;

                void main()
                {
                    FragColor = vec4(1., 1., 1., 1.);
                }
                ''')
            self.grid_shader.bindAttributeLocation('position', 0)
            glBindFragDataLocation(self.grid_shader.programId(), 0, 'FragColor')
            if not self.grid_shader.link():
                print('Failed to link grid shader!')

        self.grid_shader.bind()
        self.grid_shader.setUniformValue('projection', projection)
        self.grid_shader.setUniformValue('modelview', modelview)
        self.grid_buffer.draw(GL_LINES)
        self.grid_shader.release()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close() # TODO
        elif event.key() == Qt.Key_W:
            self.moving_forward = True
        elif event.key() == Qt.Key_S:
            self.moving_backwards = True
        elif event.key() == Qt.Key_A:
            self.moving_left = True
        elif event.key() == Qt.Key_D:
            self.moving_right = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_W:
            self.moving_forward = False
        elif event.key() == Qt.Key_S:
            self.moving_backwards = False
        elif event.key() == Qt.Key_A:
            self.moving_left = False
        elif event.key() == Qt.Key_D:
            self.moving_right = False

    def mouseMoveEvent(self, event):
        x = self.pos().x() + self.width()/2
        y = self.pos().y() + self.height()/2

        dx = event.globalX() - x
        dy = event.globalY() - y

        self.yaw += dx/200.
        self.pitch -= dy/200.
        self.pitch = clamp(self.pitch, -pi/2, pi/2)
        self.camera_direction = QVector3D(cos(self.yaw), sin(self.pitch), sin(self.yaw)).normalized()

        QCursor.setPos(x, y)

if __name__ == '__main__':
  app = QApplication(sys.argv)

  demo = Demo()
  demo.resize(800, 800)
  demo.setWindowTitle('Grass house demo')
  demo.show()

  sys.exit(app.exec_())
