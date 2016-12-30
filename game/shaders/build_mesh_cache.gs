#version 420

layout(triangles) in;
layout(triangle_strip) out;
layout(max_vertices=3) out;

layout(size1x32) uniform restrict writeonly iimage1D index_cache;

uniform int index_offset;

in VertexData {
    vec4 barycoord;
    int vertexid;
} v_in[];

out VertexData {
    vec4 barycoord;
    flat int primid;
};

void main()
{
    // ivec4 data = ivec4(v_in[0].vertexid, v_in[1].vertexid, v_in[2].vertexid, 0);
    // imageStore(index_cache, gl_PrimitiveIDIn, data);
    int primid_in = (index_offset + gl_PrimitiveIDIn) * 3;
    for (int i = 0; i < 3; i++) {
        int tri_idx = primid_in + i;
        imageStore(index_cache, tri_idx, ivec4(v_in[i].vertexid, 0, 0, 0));

        gl_Position = gl_in[i].gl_Position;
        barycoord = vec4(i==0, i==1, i==2, 1.0);
        primid = (index_offset + gl_PrimitiveIDIn) * 3;
        EmitVertex();
    }
}
