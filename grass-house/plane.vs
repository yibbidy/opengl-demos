#version 330

in vec3 position;

out vec4 shadow_coords;
out vec2 plane_coords;

uniform mat4 projection, modelview;
uniform mat4 bias, shadow_projection, shadow_modelview;

void main()
{
    shadow_coords = bias * shadow_projection * shadow_modelview * vec4(position, 1.);
    plane_coords = position.xz/10.;
    gl_Position = projection * modelview * vec4(position, 1.);
}
