Proof-of-concept little OpenGL programs
=======================================

## Grass House Demo ##

![Grass House screenshot](http://matejd.github.com/OpenGL-proof-of-concepts/grass-house.png)

Small weekend demo that didn't turn out so well. Read more [here](http://matejd.github.com/grass_house_demo_geometry_shaders_glsl_noise_shadow_mapping).

## Research demos ##

These are demos I wrote to research certain ideas. I tried
to write them in modern OpenGL only (3+), and as cleanly as
possible, so they could prove useful to someone.

3 demos (geometry-shaders-TBOs.py, geometry-shaders-TBOs-transform-cache.py, instancing.py)
display (well, they should) exactly the same boring picture (a few green diagonal lines), but they use different approaches.
Instancing demo draws sphere geometry multiple times through glDrawArraysInstanced (vertex shader
does some magic on gl_InstanceID). Geometry demo expands points to spheres in geometry shader 
(nice looking approach, but sorta slow - geometry shader performance is determined by the maximum
amount of primitives produced; they are not meant to be used for geometry amplification).
Transform cache demo instead stores produced geometry in a VBO (no copying to RAM is done) and
then renders that directly. The last demo runs fastest On My System, but instancing is only a bit slower.

TODO: write some more
