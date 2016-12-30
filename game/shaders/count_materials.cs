#version 430

uniform sampler2D intersections;
layout(size1x32) uniform iimage1D material_counts;

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
void main()
{
    ivec2 coord = ivec2(gl_GlobalInvocationID.xy);
    vec4 data = texelFetch(intersections, coord, 0).bgra;
    int materialid = floatBitsToInt(data.w);
    imageAtomicAdd(material_counts, materialid, 1);
}
