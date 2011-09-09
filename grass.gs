#version 330

layout(points) in;
layout(triangle_strip, max_vertices=3) out;

in vec3 out_position[1];
in vec3 out_normal[1];

out vec4 color;

uniform mat4 projection, modelview;
uniform float time;

void main()
{
    mat4 mvp = projection * modelview;
    vec3 right = normalize(cross(out_normal[0], normalize(vec3(0.1, 0.9, 0.))));
    const float size = 0.01;

    gl_Position = mvp * vec4((out_position[0]+out_normal[0]*size*(5+sin(time / 100.)*2)), 1.);
    color = vec4(out_normal[0], 1.);
    EmitVertex();

    gl_Position = mvp * vec4((out_position[0]+right*size), 1.);
    color = vec4(out_normal[0], 1.);
    EmitVertex();

    gl_Position = mvp * vec4((out_position[0]-right*size), 1.);
    color = vec4(out_normal[0], 1.);
    EmitVertex();

    EndPrimitive();
}
