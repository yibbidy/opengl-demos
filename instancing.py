#!/usr/bin/env python
# encoding: utf-8

import sys
import os

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
from OpenGL.GL.ARB.vertex_array_object import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from ctypes import c_void_p

import numpy

vertex_shader_source = '''#version 150
in vec3 position;
uniform mat4 mvp;
const float scale = 5.;

void main()
{
    gl_Position = mvp * vec4(position.xy*scale+vec2(gl_InstanceID, gl_InstanceID)*2, 0., 1.);
}
'''

fragment_shader_source = '''#version 150
void main()
{
    gl_FragColor = vec4(0., 1., 0., 1.);
}
'''

def parse_obj(file_name):
    lines = open(file_name).readlines()
    vertices_lines = filter(lambda line: line.startswith('v'), lines)
    faces_lines =    filter(lambda line: line.startswith('f'), lines)
    vertices = [map(float, line.split()[1:]) for line in vertices_lines]
    faces = [map(int, line.split()[1:]) for line in faces_lines]
    triangles = []
    for face in faces:
        v0 = vertices[face[0]-1]
        v1 = vertices[face[1]-1]
        v2 = vertices[face[2]-1]
        triangles.append([v0, v1, v2])
    return triangles

class Example(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)

    def initializeGL(self):
        self.program = program = QGLShaderProgram()
        program.addShaderFromSourceCode(QGLShader.Vertex, vertex_shader_source)
        program.addShaderFromSourceCode(QGLShader.Fragment, fragment_shader_source)
        if not program.link():
          print(program.log())

        triangles = parse_obj(os.path.join(os.path.dirname(__file__), 'sphere.obj'))
        vertices = []
        for v0, v1, v2 in triangles:
            vertices.extend(v0)
            vertices.extend(v1)
            vertices.extend(v2)

        self.vao_id = vao_id = GLuint(0)
        glGenVertexArrays(1, vao_id)
        glBindVertexArray(vao_id)
        vertex_buffer_id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_id)
        glBufferData(GL_ARRAY_BUFFER, numpy.array(vertices, 'f'), GL_STATIC_DRAW)
        vertex_size = 3*4
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertex_size, c_void_p(0))
        glEnableVertexAttribArray(0)
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def paintGL(self):
        glCullFace(GL_BACK)
        glEnable(GL_CULL_FACE)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        projection = QMatrix4x4()
        projection.ortho(0, self.width(), 0, self.height(), -1, 1)
        modelview = QMatrix4x4()

        self.program.bind()
        self.program.setUniformValue('mvp', projection * modelview)
        glBindVertexArray(self.vao_id)

        for i in range(20, 200, 20):
            modelview = QMatrix4x4()
            modelview.translate(i, 0)
            self.program.setUniformValue('mvp', projection * modelview)
            glDrawArraysInstanced(GL_TRIANGLES, 0, 144, 350)

        glBindVertexArray(0)
        self.program.release()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            timer = QElapsedTimer()
            timer.start()
            for i in range(100):
                self.updateGL()
            print('%0.3f ms' % (timer.elapsed() / 100.))

if __name__ == '__main__':
  app = QApplication(sys.argv)

  example = Example()
  example.resize(800, 800)
  example.setWindowTitle('Example')
  example.show()

  sys.exit(app.exec_())
