#version 330

in vec4 shadow_coords;
in vec2 plane_coords;
out vec4 frag_color;

uniform sampler2D depth;

void main()
{
    vec4 shadow_coords_w_div = shadow_coords / shadow_coords.w;
    float distance_from_light = texture2D(depth, shadow_coords_w_div.st).z;
    shadow_coords_w_div.z += 0.0005;
    float shadow = 1.0;
    if (shadow_coords.w > 0.0 &&
        shadow_coords.s > 0.0 && shadow_coords.s < 1.0 &&
        shadow_coords.t > 0.0 && shadow_coords.t < 1.0) // TODO: this shouldnt be necessary!
        shadow = distance_from_light < shadow_coords_w_div.z ? 0.7 : 1.0;
    // A completely-genuine darkening effect
    float ambient = pow(max(abs(plane_coords.x), abs(plane_coords.y)), 0.05);
    frag_color = ambient.xxxx * shadow;
}
