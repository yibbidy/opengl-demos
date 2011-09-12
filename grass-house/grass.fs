#version 330

in vec4 shadow_coords;
in vec4 color;
out vec4 frag_color;

uniform sampler2D depth;
uniform bool shadows;

void main()
{
    if (shadows)
    {
        vec4 shadow_coords_w_div = shadow_coords / shadow_coords.w;
        float distance_from_light = texture2D(depth, shadow_coords_w_div.st).z;
        shadow_coords_w_div.z += 0.0005;
        float shadow = 1.0;
        if (shadow_coords.w > 0.0)
            shadow = distance_from_light < shadow_coords_w_div.z ? 0.3 : 1.0;
        frag_color = color * shadow;
    }
    else
        frag_color = vec4(1., 1., 1., 1.);
}
