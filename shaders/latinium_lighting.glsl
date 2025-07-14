#ifndef LATINIUM_LIGHTING_GLSL
#define LATINIUM_LIGHTING_GLSL

// Placeholder settings for the experimental Latinium shader
#define LATINIUM_USE_SPECULAR

#define LATINIUM_USE_GI
#define LATINIUM_AO_RADIUS 4.0 // Sample radius in pixels [1 2 3 4 5 6 7 8 9 10]
#define LATINIUM_AO_STRENGTH 1.0 // Intensity of SSAO effect [0.0 0.5 1.0 1.5 2.0]

uniform vec3 latiniumAmbientColor; // Configurable ambient term
uniform sampler2D latiniumGIEnvMap; // Environment map used for simple GI
uniform sampler2D depthtex0;       // Depth buffer for SSAO
uniform float viewWidth;
uniform float viewHeight;

// Screen-space ambient occlusion implementation
float computeAmbientOcclusion(vec3 worldPos, vec3 normal) {
    vec2 texel = LATINIUM_AO_RADIUS / vec2(viewWidth, viewHeight);
    vec2 centerUV = gl_FragCoord.xy / vec2(viewWidth, viewHeight);
    float centerDepth = texture2D(depthtex0, centerUV).r;

    const vec2 offsets[8] = vec2[8](
        vec2( 1.0,  0.0),
        vec2(-1.0,  0.0),
        vec2( 0.0,  1.0),
        vec2( 0.0, -1.0),
        vec2( 1.0,  1.0),
        vec2(-1.0,  1.0),
        vec2( 1.0, -1.0),
        vec2(-1.0, -1.0)
    );

    float occlusion = 0.0;
    for (int i = 0; i < 8; ++i) {
        vec2 sampleUV = centerUV + offsets[i] * texel;
        float sampleDepth = texture2D(depthtex0, sampleUV).r;
        occlusion += step(centerDepth + 0.002, sampleDepth);
    }

    float ao = 1.0 - (occlusion / 8.0) * LATINIUM_AO_STRENGTH;
    return clamp(ao, 0.0, 1.0);
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
    vec3 envColor = texture2D(latiniumGIEnvMap, envUV).rgb;
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
