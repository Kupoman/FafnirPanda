#version 420

uniform samplerBuffer vertex_cache;
uniform isamplerBuffer index_cache;
uniform isamplerBuffer material_indexes;
uniform samplerBuffer material_cache;
uniform sampler2D intersections;

uniform mat4 p3d_ViewMatrix;
uniform mat3 p3d_NormalMatrix;

out vec4 frag_out;

vec3 unpack_normal(vec4 vdata1)
{
    vec3 normal;
    normal.xy = unpackSnorm2x16(floatBitsToUint(vdata1.x));
    normal.z = unpackSnorm2x16(floatBitsToUint(vdata1.y)).x;
    return normal;
}

void main()
{
    ivec2 texel_pos = ivec2(gl_FragCoord.xy);
    vec4 data = texelFetch(intersections, texel_pos, 0).bgra;
    vec3 uvw = vec3(data.x, data.y, 1.0 - data.x - data.y);
    int primid = floatBitsToInt(data.z);
    int materialid = floatBitsToInt(data.w);

    // int intid = 2 * (int(gl_FragCoord.y)*1280 + int(gl_FragCoord.x));
    // materialid = texelFetch(material_indexes, intid).x;

    int v0_idx = texelFetch(index_cache, int(primid+0)).x;
    vec4 v0_data0 = texelFetch(vertex_cache, int(v0_idx)).bgra;
    int v1_idx = texelFetch(index_cache, int(primid+1)).x;
    vec4 v1_data0 = texelFetch(vertex_cache, int(v1_idx)).bgra;
    int v2_idx = texelFetch(index_cache, int(primid+2)).x;
    vec4 v2_data0 = texelFetch(vertex_cache, int(v2_idx)).bgra;

    vec4 position = vec4(0.0, 0.0, 0.0, 1.0);
    position += uvw.x * vec4(v0_data0.xyz, 0.0);
    position += uvw.y * vec4(v1_data0.xyz, 0.0);
    position += uvw.z * vec4(v2_data0.xyz, 0.0);

    vec4 v0_data1 = texelFetch(vertex_cache, int(v0_idx+1)).bgra;
    vec4 v1_data1 = texelFetch(vertex_cache, int(v1_idx+1)).bgra;
    vec4 v2_data1 = texelFetch(vertex_cache, int(v2_idx+1)).bgra;

    vec3 normal = vec3(0.0);
    normal += uvw.x * unpack_normal(v0_data1);
    normal += uvw.y * unpack_normal(v1_data1);
    normal += uvw.z * unpack_normal(v2_data1);
    normal = normalize(normal);

    vec4 material_data = texelFetch(material_cache, materialid);
    vec4 diffuse = material_data;

    vec3 light_pos = vec3(-3.0, 3.0, -3.0);
    vec3 light_vec = normalize(light_pos - position.xyz);
    float nol = dot(normal, light_vec);

    frag_out.xyz = nol*diffuse.rgb;
    frag_out.w = 1.0;
    // frag_out.xyz = vec3(0.5, 1.0, 0.0);
}
