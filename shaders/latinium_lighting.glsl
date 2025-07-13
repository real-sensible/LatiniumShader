#ifndef LATINIUM_LIGHTING_GLSL
#define LATINIUM_LIGHTING_GLSL

// Placeholder settings for the experimental Latinium shader
#define LATINIUM_USE_SPECULAR
#define LATINIUM_USE_GI

uniform vec3 latiniumAmbientColor; // Configurable ambient term

// Future implementation of ambient occlusion
float computeAmbientOcclusion(vec3 worldPos, vec3 normal) {
    // TODO: integrate AO sampling
    return 1.0;
}

// Future implementation of specular highlights
vec3 computeSpecular(vec3 viewDir, vec3 normal) {
    // TODO: add specular lighting
    return vec3(0.0);
}

// Future global illumination placeholder
vec3 computeGlobalIllumination(vec3 worldPos, vec3 normal) {
    // TODO: implement ReSTIR based GI
    return vec3(0.0);
}

// Entry point used by fragment shaders
vec3 applyLatiniumLighting(vec3 color, vec3 worldPos, vec3 normal, vec3 viewDir) {
    float ao = computeAmbientOcclusion(worldPos, normal);
    vec3 gi = computeGlobalIllumination(worldPos, normal);
    vec3 spec = computeSpecular(viewDir, normal);

    vec3 result = color;
    result *= ao;           // basic AO term
    result += gi;           // add indirect contribution
    result += spec;         // add specular highlight
    result += latiniumAmbientColor; // base ambient light
    return result;
}

#endif // LATINIUM_LIGHTING_GLSL
