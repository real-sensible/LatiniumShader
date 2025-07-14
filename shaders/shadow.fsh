#version 330

uniform sampler2D lightmap;
uniform sampler2D diffuseTexture;

in vec2 lmcoord;
in vec2 texcoord;
in vec4 glcolor;

out vec4 out_color;

void main() {
        vec4 color = texture(diffuseTexture, texcoord) * glcolor;

        out_color = color;
}
