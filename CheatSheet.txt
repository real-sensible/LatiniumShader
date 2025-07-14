Below is a **pure-text transcription** of the “Space Conversion Cheat Sheet” diagram (for GLSL #version 120 and the compatibility profile in later versions). Everything is laid out exactly as labels appear in the image, so a text-only model can follow the same flow without seeing the picture.

---

## 1 . Uniforms / Constants declared once

```glsl
uniform float viewHeight;
uniform float viewWidth;

uniform mat4 gbufferModelView;
uniform mat4 gbufferModelViewInverse;
uniform mat4 gbufferProjection;
uniform mat4 gbufferProjectionInverse;

uniform mat4 shadowModelView;
uniform mat4 shadowModelViewInverse;
uniform mat4 shadowProjection;
uniform mat4 shadowProjectionInverse;

uniform sampler2D depthtex0;

uniform vec3  cameraPosition;           // world-space camera
vec3  eyeCameraPosition = cameraPosition + gbufferModelViewInverse[3].xyz;

const int shadowMapResolution = ...;    // fill-in
```

### Helper

```glsl
vec3 projectAndDivide(mat4 proj, vec3 pos) {
    vec4 h = proj * vec4(pos, 1.0);
    return h.xyz / h.w;
}
```

---

## 2 . Name → formula, ordered by coordinate space

| Space                            | Variable         | How to get it                                                                                         | Reverse conversion                                        |
| -------------------------------- | ---------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Model space** (a.k.a. *local*) | `vec3 modelPos`  | `gl_Vertex.xyz` (in every `gbuffers_*.vsh` & `shadow.vsh`)                                            | —                                                         |
| **View/Eye space**               | `vec3 viewPos`   | `(gl_ModelViewMatrix * gl_Vertex).xyz`<br/>**or** `(gl_ModelViewMatrix * vec4(modelPos,1.0)).xyz`     | `(gbufferModelViewInverse * vec4(viewPos,1.0)).xyz`       |
| **Clip space**                   | `vec4 clipPos`   | `gbufferProjection * vec4(viewPos,1.0)`<br/>**or** `gl_ProjectionMatrix * vec4(viewPos,1.0)` (note 2) | `(gbufferProjectionInverse * clipPos).xyz`                |
| **NDC** (-1 … 1)                 | `vec3 ndcPos`    | `clipPos.xyz / clipPos.w`                                                                             | `clipPos = vec4(ndcPos,1.0)` then mult. by projection     |
| **Screen** (0 … 1)               | `vec3 screenPos` | `ndcPos * 0.5 + 0.5`                                                                                  | `ndcPos = screenPos * 2.0 - 1.0`                          |
| **Texel / pixel**                | `vec3 texelPos`  | `screenPos * vec3(viewWidth, viewHeight, 1.0)`                                                        | `screenPos = texelPos / vec3(viewWidth, viewHeight, 1.0)` |

### Player-/world-position helpers

```glsl
// in view space
vec3 eyePlayerPos   = mat3(gbufferModelViewInverse) * viewPos;
vec3 viewPos        = mat3(gbufferModelView)       * eyePlayerPos;

// “feet” origin of the player
vec3 feetPlayerPos  = eyePlayerPos + gbufferModelViewInverse[3].xyz;
vec3 viewPos        = (gbufferModelView * vec4(feetPlayerPos,1.0)).xyz;

// world space
vec3 worldPos       = feetPlayerPos + cameraPosition;
vec3 feetPlayerPos  = worldPos - cameraPosition;
```

---

## 3 . Light / shadow path (uses *shadow* matrices & resolution)

| Space             | Variable               | Forward                                                                                                   | Reverse                                                                                  |
| ----------------- | ---------------------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Shadow-view**   | `vec3 shadowViewPos`   | `(shadowModelView * vec4(feetPlayerPos,1.0)).xyz`                                                         | `(shadowModelViewInverse * vec4(shadowViewPos,1.0)).xyz`                                 |
| **Shadow-clip**   | `vec4 shadowClipPos`   | `shadowProjection * vec4(shadowViewPos,1.0)`<br/>*(or* `gl_ProjectionMatrix * …` *inside* `shadow.vsh`)\* | `(shadowProjectionInverse * shadowClipPos).xyz`                                          |
| **Shadow-NDC**    | `vec3 shadowNdcPos`    | `shadowClipPos.xyz / shadowClipPos.w`                                                                     | `shadowClipPos = vec4(shadowNdcPos,1.0)`                                                 |
| **Shadow-screen** | `vec3 shadowScreenPos` | `shadowNdcPos * 0.5 + 0.5`                                                                                | `shadowNdcPos = shadowScreenPos * 2.0 - 1.0`                                             |
| **Shadow-texel**  | `vec3 shadowTexelPos`  | `shadowScreenPos * vec3(shadowMapResolution, shadowMapResolution, 1.0)`                                   | `shadowScreenPos = shadowTexelPos / vec3(shadowMapResolution, shadowMapResolution, 1.0)` |

---

## 4 . Depth-reconstruction stub (fragment stage)

```glsl
// In composite.fsh, final.fsh, deferred.fsh
vec3 eyePosFromDepth = vec3(texcoord,
                            texture2D(depthtex0, texcoord));
```

---

## 5 . Notes (exact wording)

1. **`gl_Position`** is expected to be in clip space. In `shadow.vsh`, that means *shadow* clip space.
2. If assigning to `gl_Position` in **gbuffers\_hand**, **always** use `gl_ProjectionMatrix`.
3. Apply shadow distortion *before* converting to shadow screen space.
4. `gbuffers_armor_glint`, `gbuffers_hand`, and `gbuffers_entities` **must** use *identical* transforms — no mixing with `ftransform()`.
5. `gl_Vertex`, `gl_ModelViewMatrix`, `gl_ProjectionMatrix`, `gl_Position`, and `ftransform()` are built-ins and don’t need explicit `uniform` declarations.
6. Any position derived from `gl_Vertex` can be passed from vertex → fragment stage with `varying`/`in out`.
7. “View space” ≡ “eye space” in OptiFine docs.
8. “Model space” ≡ “local space”.
9. “Player space” ≡ “scene space”.

---

**Everything above is now in plain, copy-paste-able text—no image required.**
