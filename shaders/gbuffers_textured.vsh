#version 330

in vec3 in_pos;
in vec3 in_normal;
in vec2 in_uv;

uniform mat4 gbufferModelView;
uniform mat4 gbufferModelViewInverse;
uniform mat4 shadowModelView;
uniform mat4 shadowProjection;
uniform vec3 shadowLightPosition;
uniform mat4 projectionMatrix;

out vec2 lmcoord;
out vec2 texcoord;
out vec4 glcolor;
out vec3 shadowPos;
out vec3 fragWorldPos;
out vec3 fragViewDir;

void main() {
    texcoord = in_uv;
    lmcoord = vec2(0.0);
    glcolor = vec4(1.0);

    vec4 viewPos = gbufferModelView * vec4(in_pos, 1.0);
    fragViewDir = normalize(-viewPos.xyz);
    fragWorldPos = (gbufferModelViewInverse * viewPos).xyz;

    vec3 normal = normalize((gbufferModelView * vec4(in_normal, 0.0)).xyz);
    glcolor.xyz += normal * 0.0001;

    vec4 playerPos = gbufferModelViewInverse * viewPos;
    shadowPos = (shadowProjection * shadowModelView * playerPos).xyz;

    gl_Position = projectionMatrix * viewPos;
}
