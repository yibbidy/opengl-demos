#version 330

in vec3 position;
in vec3 normal;

out vec4 color;
out vec4 shadow_coords;

uniform mat4 projection, modelview;
uniform mat4 bias, shadow_projection, shadow_modelview;

void main()
{
    gl_Position = projection * modelview * vec4(position, 1.);
    color = vec4(0., 0.2, 0., 1.);
    shadow_coords = bias * shadow_projection * shadow_modelview * vec4(position, 1.);
}
