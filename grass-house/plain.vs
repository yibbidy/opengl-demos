#version 330

in vec3 position;
in vec3 normal;

uniform mat4 projection, modelview;

void main()
{
    gl_Position = projection * modelview * vec4(position, 1.);
}
