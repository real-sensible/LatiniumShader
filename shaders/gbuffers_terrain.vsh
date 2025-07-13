#version 330

in vec3 in_pos;
in vec3 in_normal;
in vec2 in_uv;
in vec4 in_color;
in vec4 mc_Entity;

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
out vec3 fragWorldPos;
out vec3 fragNormal;
out vec3 fragViewDir;

#include "/distort.glsl"

void main() {
        texcoord = in_uv;
        lmcoord  = in_uv;
        glcolor = in_color;

        vec3 normalView = normalize((gbufferModelView * vec4(in_normal, 0.0)).xyz);
        float lightDot = dot(normalize(shadowLightPosition), normalView);
	#ifdef EXCLUDE_FOLIAGE
		//when EXCLUDE_FOLIAGE is enabled, act as if foliage is always facing towards the sun.
		//in other words, don't darken the back side of it unless something else is casting a shadow on it.
		if (mc_Entity.x == 10000.0) lightDot = 1.0;
	#endif

        vec4 viewPos = gbufferModelView * vec4(in_pos, 1.0);
        fragViewDir = normalize(-viewPos.xyz);
        fragWorldPos = (gbufferModelViewInverse * viewPos).xyz;
        fragNormal = normalize(mat3(gbufferModelViewInverse) * normalView);
	if (lightDot > 0.0) { //vertex is facing towards the sun
                vec4 playerPos = gbufferModelViewInverse * viewPos;
                shadowPos = shadowProjection * (shadowModelView * playerPos); //convert to shadow ndc space.
		float bias = computeBias(shadowPos.xyz);
		shadowPos.xyz = distort(shadowPos.xyz); //apply shadow distortion
		shadowPos.xyz = shadowPos.xyz * 0.5 + 0.5; //convert from -1 ~ +1 to 0 ~ 1
		//apply shadow bias.
		#ifdef NORMAL_BIAS
			//we are allowed to project the normal because shadowProjection is purely a scalar matrix.
			//a faster way to apply the same operation would be to multiply by shadowProjection[0][0].
                        vec3 worldNormal = mat3(gbufferModelViewInverse) * normalView;
                        vec4 normal = shadowProjection * vec4(mat3(shadowModelView) * worldNormal, 1.0);
			shadowPos.xyz += normal.xyz / normal.w * bias;
		#else
			shadowPos.z -= bias / abs(lightDot);
		#endif
	}
	else { //vertex is facing away from the sun
		lmcoord.y *= SHADOW_BRIGHTNESS; //guaranteed to be in shadows. reduce light level immediately.
		shadowPos = vec4(0.0); //mark that this vertex does not need to check the shadow map.
	}
	shadowPos.w = lightDot;
        gl_Position = projectionMatrix * viewPos;
}
