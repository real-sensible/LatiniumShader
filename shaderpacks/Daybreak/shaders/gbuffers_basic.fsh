#version 460 core

uniform sampler2D gTexture;

in vec2 texCoord;
in vec3 vertColor; // passed from vertex shader

layout(location = 0) out vec4 outColor0;

void main() {
    vec4 colorData = texture(gTexture, texCoord);
    vec3 rgb = colorData.rgb * vertColor;
    float alpha = colorData.a;
    if (alpha < 0.1)
        discard;
    // convert to linear space for lighting
    rgb = pow(rgb, vec3(2.2));
    // ... lighting would happen here ...
    rgb = pow(rgb, vec3(1.0/2.2));
    outColor0 = vec4(rgb, alpha);
}
