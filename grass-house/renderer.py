from ctypes import c_void_p

import OpenGL
OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_LOGGING = False
OpenGL.FULL_LOGGING = False
OpenGL.ERROR_ON_COPY = False
from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_array_object import *
from OpenGL.GL.ARB.vertex_buffer_object import *

class VertexBuffer:
    def __init__(self, data, format_description, usage=GL_STATIC_DRAW):
        '''
        Sample usage: geometry = VertexBuffer(data, size, [(3, GL_FLOAT), (4, GL_FLOAT)], GL_STATIC_DRAW)

        Currently available attribute types: GL_FLOAT # TODO

        Uses Vertex Arrays Object (OpenGL 3.0) if possible. Vertex Buffer Objects were introduced in 1.5 (2003).
        '''
        self._format_description = format_description

        if glGenVertexArrays:
            self._vao = GLuint(42)
            glGenVertexArrays(1, self._vao)
            glBindVertexArray(self._vao)
            vertex_buffer_id = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_id)
            glBufferData(GL_ARRAY_BUFFER, data, usage)

            vertex_size = sum(attribute[0]*4 for attribute in format_description)
            self._num_vertices = len(data) / (vertex_size / 4)
            current_size = 0
            for i, (num_components, type) in enumerate(format_description):
                glVertexAttribPointer(i, num_components, type, GL_FALSE, vertex_size, c_void_p(current_size))
                glEnableVertexAttribArray(i)
                current_size += num_components*4

            glBindVertexArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
        else:
            self._vbo_id = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self._vbo_id)
            glBufferData(GL_ARRAY_BUFFER, data, usage)
            self._data_length = len(data)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, primitives=GL_TRIANGLES, first=0, count=-1):
        '''glDrawArrays'''
        if hasattr(self, '_vao'):
            glBindVertexArray(self._vao)
            glDrawArrays(primitives, first,
                count if count != -1 else self._num_vertices - first)
            glBindVertexArray(0)
        else:
            glBindBuffer(GL_ARRAY_BUFFER, self._vbo_id)

            vertex_size = sum(attribute[0]*4 for attribute in self._format_description)
            current_size = 0
            for i, (num_components, type) in enumerate(self._format_description):
                glVertexAttribPointer(i, num_components, type, GL_FALSE, vertex_size, c_void_p(current_size))
                glEnableVertexAttribArray(i)
                current_size += num_components*4

            glDrawArrays(primitives, first,
                count if count != -1 else self._data_length / (vertex_size / 4) - first)

            for i in range(len(self._format_description)):
                glDisableVertexAttribArray(i)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
