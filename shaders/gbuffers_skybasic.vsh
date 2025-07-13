#version 330

in vec3 in_pos;
in vec4 in_color;

uniform mat4 gbufferModelView;
uniform mat4 projectionMatrix;

out vec4 starData; //rgb = star color, a = flag for weather or not this pixel is a star.

void main() {
        vec4 viewPos = gbufferModelView * vec4(in_pos, 1.0);
        gl_Position = projectionMatrix * viewPos;
        starData = vec4(in_color.rgb, float(in_color.r == in_color.g && in_color.g == in_color.b && in_color.r > 0.0));
}
