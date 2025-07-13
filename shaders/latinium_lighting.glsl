#ifndef LATINIUM_LIGHTING_GLSL
#define LATINIUM_LIGHTING_GLSL

// Placeholder settings for the experimental Latinium shader
#define LATINIUM_USE_SPECULAR
#define LATINIUM_USE_GI

uniform vec3 latiniumAmbientColor; // Configurable ambient term
uniform sampler2D latiniumGIEnvMap; // Environment map used for simple GI

// Future implementation of ambient occlusion
float computeAmbientOcclusion(vec3 worldPos, vec3 normal) {
    // TODO: integrate AO sampling
    return 1.0;
}

// Basic Blinn-Phong style specular highlight
vec3 computeSpecular(vec3 viewDir, vec3 normal) {
#ifdef LATINIUM_USE_SPECULAR
    vec3 refl = reflect(-viewDir, normal);
    float spec = pow(max(refl.z, 0.0), 32.0);
    return vec3(spec);
#else
    return vec3(0.0);
#endif
}

// Simple environment map based GI approximation
vec3 computeGlobalIllumination(vec3 worldPos, vec3 normal) {
#ifdef LATINIUM_USE_GI
    vec2 envUV = normal.xy * 0.5 + 0.5;
    vec3 envColor = texture(latiniumGIEnvMap, envUV).rgb;
    return envColor * 0.2; // subtle contribution
#else
    return vec3(0.0);
#endif
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
