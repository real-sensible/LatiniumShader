#version 330

uniform sampler2D texture;

in vec2 texcoord;
in vec4 glcolor;

out vec4 out_color;

void main() {
    vec4 color = texture(texture, texcoord) * glcolor;
    out_color = color; // gcolor
}
