#version 120

// Initial sampling pass for ReSTIR GI

uniform sampler2D latiniumGIEnvMap;

varying vec2 texcoord;

void main() {
    // Sample the environment map using texcoord as a simple hemispherical lookup
    vec3 sampleColor = texture2D(latiniumGIEnvMap, texcoord).rgb;

    // Store candidate sample color and weight (encoded in alpha)
    gl_FragData[0] = vec4(sampleColor, 1.0);
}

