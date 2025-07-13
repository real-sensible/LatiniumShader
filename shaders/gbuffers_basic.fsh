#version 330

uniform sampler2D lightmap;

in vec2 lmcoord;
in vec4 glcolor;

out vec4 out_color;

void main() {
    vec4 color = glcolor;
    color *= texture(lightmap, lmcoord);

    out_color = color; // gcolor
}
