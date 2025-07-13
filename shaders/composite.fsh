#version 330

// Optionally, you can use a preprocessor define or just set via uniform in code.
#define DRAW_SHADOW_MAP gcolor

uniform float frameTimeCounter;
uniform sampler2D gcolor;
uniform sampler2D shadowcolor0;
uniform sampler2D shadowtex0;
uniform sampler2D shadowtex1;

in vec2 texcoord;
out vec4 fragColor;

void main() {
    vec3 color = texture(DRAW_SHADOW_MAP, texcoord).rgb;

    fragColor = vec4(color, 1.0); // gcolor
}
