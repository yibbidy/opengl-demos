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

geometry_shader_source = '''#version 150
layout(points) in;
layout(triangle_strip, max_vertices=144) out;

uniform mat4 mvp;
uniform samplerBuffer sphere_triangles;

void main()
{
    vec4 pos = gl_in[0].gl_Position;
    const float scale = 5.;

    for (int i = 0; i < 48; ++i)
    {
        vec3 offset = texelFetch(sphere_triangles, i*3+0).xyz * scale;
        offset.z = 0.;
        gl_Position = mvp * (pos+vec4(offset, 0.));
        EmitVertex();

        offset = texelFetch(sphere_triangles, i*3+1).xyz * scale;
        offset.z = 0.;
        gl_Position = mvp * (pos+vec4(offset, 0.));
        EmitVertex();

        offset = texelFetch(sphere_triangles, i*3+2).xyz * scale;
        offset.z = 0.;
        gl_Position = mvp * (pos+vec4(offset, 0.));
        EmitVertex();

        EndPrimitive();
    }
}
'''

vertex_shader_source = '''#version 150
in vec2 position;

void main()
{
    gl_Position = vec4(position, 0., 1.);
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
        program.addShaderFromSourceCode(QGLShader.Geometry, geometry_shader_source)
        program.addShaderFromSourceCode(QGLShader.Vertex, vertex_shader_source)
        program.addShaderFromSourceCode(QGLShader.Fragment, fragment_shader_source)
        if not program.link():
          print(program.log())

        vertices = [i for i in range(0, 350*2)]

        self.vao_id = vao_id = GLuint(0)
        glGenVertexArrays(1, vao_id)
        glBindVertexArray(vao_id)
        vertex_buffer_id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_id)
        glBufferData(GL_ARRAY_BUFFER, numpy.array(vertices, 'f'), GL_STATIC_DRAW)
        vertex_size = (2)*4
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, vertex_size, c_void_p(0))
        glEnableVertexAttribArray(0)
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        triangles = parse_obj(os.path.join(os.path.dirname(__file__), 'sphere.obj'))
        float_data = []
        for v0, v1, v2 in triangles:
            float_data.extend(v0)
            float_data.extend(v1)
            float_data.extend(v2)

        # TBO
        tbo = glGenBuffers(1)
        glBindBuffer(GL_TEXTURE_BUFFER, tbo)
        glBufferData(GL_TEXTURE_BUFFER, len(float_data)*4, numpy.array(float_data, 'f'), GL_STATIC_DRAW)
        glBindBuffer(GL_TEXTURE_BUFFER, 0)

        self.sphere_tex = sphere_tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_BUFFER, sphere_tex)
        glTexBuffer(GL_TEXTURE_BUFFER, GL_RGB32F, tbo)
        glBindTexture(GL_TEXTURE_BUFFER, 0)

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

        self.program.bind()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_BUFFER, self.sphere_tex)
        self.program.setUniformValue('sphere_triangles', 0)
        glBindVertexArray(self.vao_id)

        for i in range(20, 200, 20):
            modelview = QMatrix4x4()
            modelview.translate(i, 0)
            self.program.setUniformValue('mvp', projection * modelview)
            glDrawArrays(GL_POINTS, 0, 350)

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
