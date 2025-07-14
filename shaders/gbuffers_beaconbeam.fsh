#version 330

uniform sampler2D diffuseTexture;

in vec2 texcoord;
in vec4 glcolor;

out vec4 out_color;

void main() {
        vec4 color = texture(diffuseTexture, texcoord) * glcolor;

/* DRAWBUFFERS:0 */
        out_color = color; // gcolor
}
