#version 120

uniform sampler2D lightmap;
uniform sampler2D diffuseTexture;

varying vec2 lmcoord;
varying vec2 texcoord;
varying vec4 glcolor;

void main() {
<<<<<<< HEAD
        vec4 color = texture(diffuseTexture, texcoord) * glcolor;
=======
	vec4 color = texture2D(texture, texcoord) * glcolor;
>>>>>>> parent of 6150846 (Update shaders to GLSL 330)

	gl_FragData[0] = color;
}
