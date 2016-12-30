#version 420

uniform int material_index;

layout(size1x32) uniform restrict writeonly image1D material_indexes;

in VertexData {
    vec4 barycoord;
    flat int primid;
};

out vec4 frag_out;

void main()
{
    int image_idx = 1 * (int(gl_FragCoord.y)*1280 + int(gl_FragCoord.x));
    // imageStore(material_indexes, image_idx+0, ivec4(material_index, 0, 0, 0));
    // imageStore(material_indexes, int(gl_FragCoord.x), ivec4(1, 0, 0, 0));

    vec4 data;
    data.bg = barycoord.xy;
    data.r = intBitsToFloat(primid);
    data.a = intBitsToFloat(material_index);
    frag_out = data;
}
