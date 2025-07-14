#version 330

in vec3 in_pos;
in vec3 in_normal;
in vec2 in_uv;
in vec4 in_color;

uniform mat4 gbufferModelView;
uniform mat4 gbufferModelViewInverse;
uniform mat4 shadowModelView;
uniform mat4 shadowProjection;
uniform vec3 shadowLightPosition;
uniform mat4 projectionMatrix;

out vec2 lmcoord;
out vec2 texcoord;
out vec4 glcolor;
out vec4 shadowPos;

#include "/distort.glsl"

void main() {
    texcoord = in_uv;
    lmcoord  = in_uv;
    glcolor = in_color;

    vec4 viewPos = gbufferModelView * vec4(in_pos, 1.0);
    vec3 normalView = normalize((gbufferModelView * vec4(in_normal, 0.0)).xyz);
    float lightDot = dot(normalize(shadowLightPosition), normalView);
    if (lightDot > 0.0) {
        vec4 playerPos = gbufferModelViewInverse * viewPos;
        shadowPos = shadowProjection * (shadowModelView * playerPos);
        shadowPos.xyz /= shadowPos.w;
        float bias = computeBias(shadowPos.xyz);
        shadowPos.xyz = distort(shadowPos.xyz);
        shadowPos.xyz = shadowPos.xyz * 0.5 + 0.5;
#ifdef NORMAL_BIAS
        vec3 worldNormal = mat3(gbufferModelViewInverse) * normalView;
        vec4 normal = shadowProjection * vec4(mat3(shadowModelView) * worldNormal, 1.0);
        shadowPos.xyz += normal.xyz / normal.w * bias;
#else
        shadowPos.z -= bias / abs(lightDot);
#endif
    } else {
        lmcoord.y *= SHADOW_BRIGHTNESS;
        shadowPos = vec4(0.0);
    }
    shadowPos.w = lightDot;
    gl_Position = projectionMatrix * viewPos;
}
