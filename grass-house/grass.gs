#version 330

layout(points) in;
layout(triangle_strip, max_vertices=3) out;

in vec3 out_position[1];
in vec3 out_normal[1];

out vec4 shadow_coords;
out vec3 blade_normal;
out vec4 color;

uniform mat4 mvp;
uniform mat4 shadow_mvp;
uniform float time;
uniform vec3 camera_right;
uniform bool color_normal;

//
// Description : Array and textureless GLSL 2D/3D/4D simplex 
//               noise functions.
//      Author : Ian McEwan, Ashima Arts.
//  Maintainer : ijm
//     Lastmod : 20110822 (ijm)
//     License : Copyright (C) 2011 Ashima Arts. All rights reserved.
//               Distributed under the MIT License. See LICENSE file.
//               https://github.com/ashima/webgl-noise
// 

vec3 mod289(vec3 x)
{
    return x - floor(x * (1.0 / 289.0)) * 289.0;
}

vec4 mod289(vec4 x)
{
    return x - floor(x * (1.0 / 289.0)) * 289.0;
}

vec4 permute(vec4 x)
{
    return mod289(((x*34.0)+1.0)*x);
}

vec4 taylorInvSqrt(vec4 r)
{
    return 1.79284291400159 - 0.85373472095314 * r;
}

float snoise(vec3 v)
{
    const vec2 C = vec2(1.0/6.0, 1.0/3.0) ;
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);

    // First corner
    vec3 i  = floor(v + dot(v, C.yyy));
    vec3 x0 =   v - i + dot(i, C.xxx);

    // Other corners
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);

    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy; // 2.0*C.x = 1/3 = C.y
    vec3 x3 = x0 - D.yyy;      // -1.0+3.0*C.x = -0.5 = -D.y

    // Permutations
    i = mod289(i); 
    vec4 p = permute(permute(permute(
             i.z + vec4(0.0, i1.z, i2.z, 1.0))
           + i.y + vec4(0.0, i1.y, i2.y, 1.0)) 
           + i.x + vec4(0.0, i1.x, i2.x, 1.0));

    // Gradients: 7x7 points over a square, mapped onto an octahedron.
    // The ring size 17*17 = 289 is close to a multiple of 49 (49*6 = 294)
    float n_ = 0.142857142857; // 1.0/7.0
    vec3  ns = n_ * D.wyz - D.xzx;

    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);  //  mod(p,7*7)

    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);    // mod(j,N)

    vec4 x = x_ *ns.x + ns.yyyy;
    vec4 y = y_ *ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);

    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);

    vec4 s0 = floor(b0)*2.0 + 1.0;
    vec4 s1 = floor(b1)*2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));

    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;

    vec3 p0 = vec3(a0.xy,h.x);
    vec3 p1 = vec3(a0.zw,h.y);
    vec3 p2 = vec3(a1.xy,h.z);
    vec3 p3 = vec3(a1.zw,h.w);

    //Normalise gradients
    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
    p0 *= norm.x;
    p1 *= norm.y;
    p2 *= norm.z;
    p3 *= norm.w;

    // Mix final noise value
    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1),
                                dot(p2,x2), dot(p3,x3)));
}

void emit(vec3 position0, vec4 color0,
          vec3 position1, vec4 color1,
          vec3 position2, vec4 color2)
{
    gl_Position = mvp * vec4(position0, 1.);
    shadow_coords = shadow_mvp * vec4(position0, 1.);
    color = color0;
    EmitVertex();

    gl_Position = mvp * vec4(position1, 1.);
    shadow_coords = shadow_mvp * vec4(position1, 1.);
    color = color1;
    EmitVertex();

    gl_Position = mvp * vec4(position2, 1.);
    shadow_coords = shadow_mvp * vec4(position2, 1.);
    color = color2;
    EmitVertex();

    EndPrimitive();
}

void main()
{
    // Semi-randomly move the tip of grass blade (which is just a triangle):
    vec3 x = normalize(cross(out_normal[0], normalize(vec3(0.49, 0.42, 0.78))));
    vec3 y = normalize(cross(out_normal[0], x));
    vec3 normal = normalize(out_normal[0] + x*(snoise(out_position[0]*10.) + snoise(out_position[0] + time / 3000.)*2.) +
                                            y*(snoise(out_position[0]*4.)  + snoise(x + time / 3000.)*2.));
    const float size = 0.004;
    const float part_length = 10.*size*(1. + snoise(out_position[0])/1.5);

    vec4 bottom_color = color_normal ? vec4(normal, 1.) : vec4(0.1, 0.7, 0.1, 1.);
    vec4 top_color = color_normal ? vec4(normal, 1.) : vec4(0.9, 0.8, 0.3, 1.);

    emit(out_position[0]+camera_right*size, bottom_color,
         out_position[0]-camera_right*size, bottom_color,
         out_position[0]+normal*part_length*3, top_color);
}
