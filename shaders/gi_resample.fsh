#version 120

// Temporal and spatial resampling pass for ReSTIR GI

uniform sampler2D restirPrevReservoir;
uniform sampler2D restirCandidate;

varying vec2 texcoord;

void main() {
    vec3 prev = texture2D(restirPrevReservoir, texcoord).rgb;
    vec3 candidate = texture2D(restirCandidate, texcoord).rgb;

    // Placeholder for actual ReSTIR resampling logic
    vec3 result = mix(candidate, prev, 0.5);

    gl_FragData[0] = vec4(result, 1.0);
}

