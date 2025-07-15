#version 460 core

layout(location = 0) in vec3 vaPosition;
layout(location = 1) in vec2 vaUV0;
layout(location = 2) in vec3 vaColor;

uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;

out vec2 texCoord;
out vec3 vertColor;

void main() {
    texCoord = vaUV0;
    vertColor = vaColor;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(vaPosition, 1.0);
}
