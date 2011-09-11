#version 330

in vec3 position;

uniform mat4 projection, modelview;
uniform mat4 bias, shadow_projection, shadow_modelview;

out vec4 shadow_coords;

void main()
{
    gl_Position = projection * modelview * vec4(position, 1.);
    shadow_coords = /*vec4(position/10., 1.);*/bias * shadow_projection * shadow_modelview * vec4(position, 1.);
}
