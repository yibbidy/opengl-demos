#version 330

in vec3 position;
in vec3 normal;

out vec3 out_position;
out vec3 out_normal;

void main()
{
    out_position = position;
    out_normal = normal;
}
