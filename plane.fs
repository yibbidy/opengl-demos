#version 330

in vec4 shadow_coords;

out vec4 FragColor;

uniform sampler2D depth;

void main()
{
    vec4 shadow_coords_w_div = shadow_coords / shadow_coords.w;
    shadow_coords_w_div.z += 0.0005;
    float distance_from_light = texture2D(depth, shadow_coords_w_div.st).z;
    float shadow = 1.0;
    //if (shadow_coords.w > 0.0)
    shadow = distance_from_light < shadow_coords_w_div.z ? 0.5 : 1.0;
    FragColor = vec4(1., 1., 1., 1.) * shadow;
    FragColor = vec4(texture2D(depth, shadow_coords.xz).r, 0., 0., 1.);
    //FragColor = shadow_coords;
}
