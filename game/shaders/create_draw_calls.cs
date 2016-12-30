#version 430

uniform isamplerBuffer material_counts;
layout(size1x32) uniform restrict writeonly iimage1D draw_calls;

layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
void main()
{
    int matid = int(gl_GlobalInvocationID.x);
    ivec4 command = ivec4(0);
    command.y = texelFetch(material_counts, matid).r;
    for (int i = 0; i < matid; i++) {
        command.z += texelFetch(material_counts, i).r;
    }
    imageStore(draw_calls, matid, command);
}
