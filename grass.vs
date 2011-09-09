#version 150

in vec3 position;
in vec3 normal;

out vec4 color;

uniform mat4 projection;
uniform mat4 modelview;

void main()
{
    gl_Position = projection * modelview * vec4(position, 1.);
    color = vec4(normal, 1.);
}
