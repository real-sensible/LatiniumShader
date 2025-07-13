#version 330

// Vertex attributes (these replace built-ins)
in vec3 in_pos;          // Replace gl_Vertex
in vec2 in_uv0;          // Replace gl_MultiTexCoord0
in vec2 in_uv1;          // Replace gl_MultiTexCoord1
in vec4 in_color;        // Replace gl_Color
in vec4 mc_Entity;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform mat4 textureMatrix0;
uniform mat4 textureMatrix1;

out vec2 lmcoord;
out vec2 texcoord;
out vec4 glcolor;

#include "distort.glsl"

void main() {
    // Texture coordinate transforms
    texcoord = (textureMatrix0 * vec4(in_uv0, 0.0, 1.0)).xy;
    lmcoord  = (textureMatrix1 * vec4(in_uv1, 0.0, 1.0)).xy;
    glcolor = in_color;

    #ifdef EXCLUDE_FOLIAGE
        if (mc_Entity.x == 10000.0) {
            gl_Position = vec4(10.0, 10.0, 10.0, 1.0);
        } else {
    #endif
            vec4 pos = projectionMatrix * viewMatrix * modelMatrix * vec4(in_pos, 1.0);
            pos.xyz = distort(pos.xyz);
            gl_Position = pos;
    #ifdef EXCLUDE_FOLIAGE
        }
    #endif
}
