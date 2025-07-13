#version 330

in vec3 in_pos;
in vec2 in_uv;
in vec4 in_color;

uniform mat4 gbufferModelView;
uniform mat4 projectionMatrix;

out vec2 lmcoord;
out vec2 texcoord;
out vec4 glcolor;

void main() {
        //use same transforms as entities and hand to avoid z-fighting issues
        vec4 viewPos = gbufferModelView * vec4(in_pos, 1.0);
        gl_Position = projectionMatrix * viewPos;
        texcoord = in_uv;
        lmcoord = in_uv;
        glcolor = in_color;
}
