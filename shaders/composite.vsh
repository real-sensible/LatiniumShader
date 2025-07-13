#version 330

in vec3 in_pos;
in vec2 in_uv;

uniform mat4 gbufferModelView;
uniform mat4 projectionMatrix;

out vec2 texcoord;

void main() {
        vec4 viewPos = gbufferModelView * vec4(in_pos, 1.0);
        gl_Position = projectionMatrix * viewPos;
        texcoord = in_uv;
}
