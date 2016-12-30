#version 420

uniform ivec2 window_size;
uniform int first;

void main()
{
    // gl_Position.zw = vec2(0.0, 1.0);
    // gl_Position.x = (gl_VertexID == 0 || gl_VertexID == 3) ? -3.0 : 1.0;
    // gl_Position.y = (gl_VertexID == 0 || gl_VertexID == 1) ? -1.0 : 3.0;
    int vertex_id = gl_VertexID+first;
    ivec2 pos = ivec2(vertex_id%window_size.x, vertex_id/window_size.x);
    vec2 norm_pos = vec2(pos)/vec2(window_size.x, window_size.y);
    norm_pos = norm_pos * vec2(2.0) - vec2(1.0);
    gl_Position = vec4(norm_pos, 0.0, 1.0);
}
