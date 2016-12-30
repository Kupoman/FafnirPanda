#version 430

uniform sampler2D intersections;
uniform isamplerBuffer draw_calls;
layout(size1x32) uniform iimage1D material_counts;
layout(size1x32) uniform writeonly iimage1D sorted_indexes;

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
void main()
{
    ivec2 coord = ivec2(gl_GlobalInvocationID.xy);
    vec4 data = texelFetch(intersections, coord, 0).bgra;
    int materialid = floatBitsToInt(data.w);

    ivec4 draw_data = texelFetch(draw_calls, materialid).bgra;
    int count = draw_data.y;
    int remaining = imageAtomicAdd(material_counts, materialid, -1);
    int new_index = draw_data.z + (count - remaining);
    int current_index = coord.y * int(gl_NumWorkGroups.x) + coord.x;
    imageStore(sorted_indexes, new_index, ivec4(current_index, 0, 0, 0));
}
