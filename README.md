# Distant Horizons support

## Table of Contents

1. [Definitions/Properties](#definitionsproperties)
2. [Samplers/Uniforms](#samplersuniforms)
3. [Programs](#programs)
4. [Block ID's](#block-ids)

# Definitions/Properties

### Enabling the DH shadow pass

The DH shadow pass is **automatically enabled**. It's existence can be turned on or off with the shader property `dhShadow.enabled`.

**Distant Horizons has no set shadow distance; all chunks will be rendered.**

### Checking for Distant Horizons

All programs and properties have the `DISTANT_HORIZONS` define set if DH is enabled.

# Samplers/Uniforms

## Depth textures

There are two depth textures attached to Distant Horizons;

`dhDepthTex0` and `dhDepthTex1`. These behave identically to their non-DH counterparts, except they have different near/far planes (explained below) and only contain DH terrain/water.

## Uniforms

### dhNearPlane

#### Declaration

```glsl
uniform float dhNearPlane;
```

This uniform specifies the near plane of DH's projection. **This does not apply to the shadow pass, use normal projection.**

### dhFarPlane

#### Declaration

```glsl
uniform float dhFarPlane;
```

This uniform specifies the far plane of DH's projection. **This is not the render distance! Use dhRenderDistance for that.**

### dhRenderDistance

#### Declaration

```glsl
uniform int dhRenderDistance;
```

This uniform specifies the render distance currently set in DH.

### dhProjection and variants

#### Declaration

```glsl
uniform mat4 dhProjection;
uniform mat4 dhProjectionInverse;
uniform mat4 dhPreviousProjection;
```

This is the projection matrix for the non-shadow pass of Distant Horizons. This includes a different near and far plane, see the uniforms above.

# Programs

## Supported attributes

The following attributes are supported in DH programs:

`gl_Vertex`
`gl_MultiTexCoord2`
`gl_Normal`
`gl_Color`
`dhMaterialId`

The following built in uniforms are supported:

`gl_ModelViewMatrix(Inverse, etc)`
`gl_ProjectionMatrix(Inverse, etc)`
`gl_NormalMatrix`

### Terrain

Terrain gets the program `dh_terrain`. This runs before normal terrain.

### Water

Water gets the program `dh_water`.  This runs **before** normal water.

### Shadow

Shadow pass gets the program `dh_shadow`. This runs before shadow terrain and shadow water respectively. **The shadow pass retains the normal textures and projection.**

# Block ID's

**Normal block ID's (mc_Entity) are not supported.**

Iris provides "mini-IDs" in the form of `int dhMaterialId` automatically declared.

All Mini-ID's get their own definitions that can be used in any program.

```text
DH_BLOCK_UNKNOWN // Any block not in this list that does not emit light
DH_BLOCK_LEAVES // All types of leaves, bamboo, or cactus
DH_BLOCK_STONE // Stone or ore
DH_BLOCK_WOOD // Any wooden item
DH_BLOCK_METAL // Any block that emits a metal or copper sound.
DH_BLOCK_DIRT // Dirt, grass, podzol, and coarse dirt.
DH_BLOCK_LAVA // Lava.
DH_BLOCK_DEEPSLATE // Deepslate, and all it's forms.
DH_BLOCK_SNOW // Snow.
DH_BLOCK_SAND // Sand and red sand.
DH_BLOCK_TERRACOTTA // Terracotta.
DH_BLOCK_NETHER_STONE // Blocks that have the "base_stone_nether" tag.
DH_BLOCK_WATER // Water...
DH_BLOCK_AIR // Air. This should never be accessible/used.
DH_BLOCK_ILLUMINATED // Any block not in this list that emits light
```

Overview
========
The Shaders Mod makes use of a deferred rendering pipeline.
The gbuffer shaders come first in the pipeline. They render data to textures that will be sent to the composite shaders. 
Optional composite shaders can be added after the shadow map (shadowcomp), before terrain (prepare) and before water rendering (deferred).
The composite shaders then render to textures that will be sent to the final shader. 
The final shader renders directly to the screen.

Shader Files
============
All shader files are placed in the folder "shaders" of the shader pack.
The shader source files use the name of the program in which they are to be used with extension depending on their type.

Extension  Type                 
==========================
.csh       Compute shader
.vsh       Vertex shader     
.gsh       Geometry shader   
.fsh       Fragment shader   

Geometry shaders need either OpenGL 3.2 with layout qualifiers or the extension GL_ARB_geometry_shader4 (GL_EXT_geometry_shader4) 
with configuration "maxVerticesOut".

Color Attachments
=================
The data is passed from shader to shader using color attachments. 
There are at least 4 for all machines. For machines that can support it, there are up to 16.
MacOS is limited to 8 color attachments, even with modern GPUs.
In the deferred, composite and final shaders, these are referenced by the gcolor, gdepth, gnormal, composite, gaux1, gaux2, gaux3 and gaux4 uniforms.
(colortex0 to colortex15 can be used instead of gcolor, gdepth etc.)
Despite the naming, all of these color attachments are the same and can be used for any purpose with the exception of the first two. 
The first one, gcolor has its color cleared to the current fog color before rendering. 
The second one, gdepth has its color cleared to solid white before rendering and uses a higher precision storage buffer suitable for storing depth values. 
The rest have their color cleared to black with 0 alpha.

Each color attachment uses 2 buffers (A and B) with logical names "main" and "alt", which can be used as ping-pong buffers.
When the buffers are flipped the mapping between main/alt and A/B is reversed.
Gbuffer programs always read from "main" (only gaux1-4) and write to "main" buffers (they shouldn't read and write to the same buffer at the same time).
Deferred/composite programs always read from "main" and write to "alt" buffers. 
After a deferred/composite program is rendered the buffers that it writes to are flipped so the next programs can see the current output as input.
The property "flip.<program>.<buffer>=<true|false>" can be used to enable or disable the flip independant of the buffer write.
The virtual programs "deferred_pre" and "composite_pre" can be used for buffer flipping before the deferred/composite pass.

Output color attachments are configured with the "/* DRAWBUFFERS:XYZ */" or "/* RENDERTARGETS: X,Y,Z */" comment, placed in the fragment shader.
Gbuffers, deferred and composite programs can write to any color attachment, but no more than 8 at the same time.
If the output color attachments are not configured, then the program will write to the first 8 color attachments.  

In shaders using the modern syntax (130 and above) the outputs of the fragment shader should use the outColor<n> names. Example:
/* RENDERTARGETS:3,4,7 */
out vec4 outColor0; // Writes to buffer 3
out vec4 outColor1; // Writes to buffer 4
out vec4 outColor2; // Writes to buffer 7

When writing to the color attachments in the composite shader, blending is disabled. 
Writing to color attachments that the composite shader also reads from will generate artifacts (unless you just copy the original contents) 

The shaders configuration parsing is affected by the preprocessor conditional compilation directives.
The following preprocessor directives are currently recognized:
  #define <macro>
  #undef <macro>
  #ifdef <macro>
  #ifndef <macro>
  #if <int>
  #if defined <macro>
  #if !defined <macro>
  #elif <int>
  #elif defined <macro> 
  #elif !defined <macro>
  #else
  #endif

The current shaderpack can be reloaded by pressing "F3+R" or using the command "/reloadShaders". 

Compute Shaders
===============
A list of compute shaders can be attached to every program except gbuffers programs.
They are named like the program with optional suffix, for example "composite.csh", "composite_a.csh" ... "composite_z.csh".
Compute shaders run before the program and can read from all buffers using texture samplers.
They can read and write to colortex0-5 and shadowcolor0-1 buffers as images using the aliases colorimg0-5 and shadowcolorimg0-1, 
for example "layout (rgba8) uniform image2D colorimg0;"
Compute shaders need at least "#version 430" and local size definition, for example: "layout (local_size_x = 16, local_size_y = 16) in;".
Work groups are defined either fixed via "const ivec3 workGroups = ivec3(50, 30, 1);" or relative to render size 
via "const vec2 workGroupsRender = vec2(0.5f, 0.5f);".
The default configuration is "const vec2 workGroupsRender = vec2(1.0f, 1.0f);", which executes the compute shader once per pixel.

Image access
============
All programs can read and write to colorimg0-5 and shadowcolorimg0-1 using imageLoad() and imageStore().

Shader Programs
===============
Name                         Render                                When not defined use
========================================================================================
<none>                       gui, menus                            <none>
--- Shadow map ---
shadow                       everything in shadow pass             <none>  
shadow_solid                 <not used>                            shadow
shadow_cutout                <not used>                            shadow
--- Shadow composite ---
shadowcomp                   <shadowcomp>                          <none>
shadowcomp1                  <shadowcomp>                          <none>
...
shadowcomp99                 <shadowcomp>                          <none>
--- Prepare ---
prepare                      <prepare>                             <none>
prepare1                     <prepare>                             <none>
...
prepare99                    <prepare>                             <none>
--- GBuffers ---
gbuffers_basic               leash, block selection box            <none>
gbuffers_line                block outline, fishing line           gbuffers_basic
gbuffers_textured            particles                             gbuffers_basic
gbuffers_textured_lit        lit_particles, world border           gbuffers_textured
gbuffers_skybasic            sky, horizon, stars, void             gbuffers_basic
gbuffers_skytextured         sun, moon                             gbuffers_textured
gbuffers_clouds              clouds                                <none>
gbuffers_terrain             solid, cutout, cutout_mip             gbuffers_textured_lit
gbuffers_terrain_solid       <not used>                            gbuffers_terrain
gbuffers_terrain_cutout_mip  <not used>                            gbuffers_terrain
gbuffers_terrain_cutout      <not used>                            gbuffers_terrain
gbuffers_damagedblock        damaged_blocks                        gbuffers_terrain
gbuffers_block               block_entities                        gbuffers_terrain
gbuffers_beaconbeam          beacon beam                           gbuffers_textured
gbuffers_item                <not used>                            gbuffers_textured_lit
gbuffers_entities            entities                              gbuffers_textured_lit
gbuffers_entities_glowing    glowing entities, spectral effect     gbuffers_entities
gbuffers_armor_glint         glint on armor and handheld items     gbuffers_textured
gbuffers_spidereyes          eyes of spider, enderman and dragon   gbuffers_textured
gbuffers_hand                hand and opaque handheld objects      gbuffers_textured_lit
gbuffers_weather             rain, snow                            gbuffers_textured_lit
--- Deferred ---
deferred_pre                 <virtual> flip ping-pong buffers      <none>
deferred                     <deferred>                            <none>
deferred1                    <deferred>                            <none>
...
deferred99                   <deferred>                            <none>
--- GBuffers translucent ---
gbuffers_water               translucent                           gbuffers_terrain
gbuffers_hand_water          translucent handheld objects          gbuffers_hand
--- Composite ---
composite_pre                <virtual> flip ping-pong buffers      <none>
composite                    <composite>                           <none>
composite1                   <composite>                           <none>
...
composite99                  <composite>                           <none>
--- Final ---
final                        <final>                               <none>

Remarks:
 - The programs shadow_solid, shadow_cutout, gbuffers_terrain_solid, gbuffers_terrain_cutout and gbuffers_terrain_cutout_mip are not used

Todo:
 - Separate programs for world border, entities (by id, by type), cape, elytra, wolf collar, etc. 
 
Attributes
==========
Source                                          Value                                       Comment
======================================================================================================================================================================
in vec3 vaPosition;                             position (x, y, z)                          1.17+, for terrain it is relative to the chunk origin, see "modelOffset"
in vec4 vaColor;                                color (r, g, b, a)                          1.17+
in vec2 vaUV0;                                  texture (u, v)                              1.17+
in ivec2 vaUV1;                                 overlay (u, v)                              1.17+
in ivec2 vaUV2;                                 lightmap (u, v)                             1.17+
in vec3 vaNormal;                               normal (x, y, z)                            1.17+
in vec3 mc_Entity;                              xy = blockId, renderType                    "blockId" is used only for blocks specified in "block.properties"      
in vec2 mc_midTexCoord;                         st = midTexU, midTexV                       Sprite middle UV coordinates                
in vec4 at_tangent;                             xyz = tangent vector, w = handedness
in vec3 at_velocity;                            vertex offset to previous frame             In view space, only for entities and block entities
in vec3 at_midBlock;                            offset to block center in 1/64m units       Only for blocks

Uniforms
==========
Source                                          Value                                                    
=====================================================================================================================================================================
uniform int heldItemId;                         held item ID (main hand), used only for items defined in "item.properties"
uniform int heldBlockLightValue;                held item light value (main hand)
uniform int heldItemId2;                        held item ID (off hand), used only for items defined in "item.properties"
uniform int heldBlockLightValue2;               held item light value (off hand)
uniform int fogMode;                            GL_LINEAR, GL_EXP or GL_EXP2
uniform float fogStart;                         fog start distance (m)
uniform float fogEnd;                           fog end distance (m)
uniform int fogShape;                           0 = sphere, 1 = cylinder
uniform float fogDensity;                       0.0-1.0
uniform vec3 fogColor;                          r, g, b
uniform vec3 skyColor;                          r, g, b
uniform int worldTime;                          <ticks> = worldTicks % 24000
uniform int worldDay;                           <days> = worldTicks / 24000
uniform int moonPhase;                          0-7
uniform int frameCounter;                       Frame index (0 to 720719, then resets to 0)
uniform float frameTime;                        last frame time, seconds
uniform float frameTimeCounter;                 run time, seconds (resets to 0 after 3600s)
uniform float sunAngle;                         0.0-1.0
uniform float shadowAngle;                      0.0-1.0
uniform float rainStrength;                     0.0-1.0
uniform float aspectRatio;                      viewWidth / viewHeight
uniform float viewWidth;                        viewWidth
uniform float viewHeight;                       viewHeight
uniform float near;                             near viewing plane distance
uniform float far;                              far viewing plane distance
uniform vec3 sunPosition;                       sun position in eye space
uniform vec3 moonPosition;                      moon position in eye space
uniform vec3 shadowLightPosition;               shadow light (sun or moon) position in eye space
uniform vec3 upPosition;                        direction up
uniform vec3 cameraPosition;                    camera position in world space
uniform vec3 previousCameraPosition;            last frame cameraPosition
uniform mat4 gbufferModelView;                  modelview matrix after setting up the camera transformations
uniform mat4 gbufferModelViewInverse;           inverse gbufferModelView
uniform mat4 gbufferPreviousModelView;          last frame gbufferModelView
uniform mat4 gbufferProjection;                 projection matrix when the gbuffers were generated
uniform mat4 gbufferProjectionInverse;          inverse gbufferProjection
uniform mat4 gbufferPreviousProjection;         last frame gbufferProjection
uniform mat4 shadowProjection;                  projection matrix when the shadow map was generated
uniform mat4 shadowProjectionInverse;           inverse shadowProjection
uniform mat4 shadowModelView;                   modelview matrix when the shadow map was generated
uniform mat4 shadowModelViewInverse;            inverse shadowModelView
uniform float wetness;                          rainStrength smoothed with wetnessHalfLife or drynessHalfLife
uniform float eyeAltitude;                      view entity Y position
uniform ivec2 eyeBrightness;                    x = block brightness, y = sky brightness, light 0-15 = brightness 0-240 
uniform ivec2 eyeBrightnessSmooth;              eyeBrightness smoothed with eyeBrightnessHalflife
uniform ivec2 terrainTextureSize;               not used
uniform int terrainIconSize;                    not used
uniform int isEyeInWater;                       1 = camera is in water, 2 = camera is in lava, 3 = camera is in powder snow
uniform float nightVision;                      night vision (0.0-1.0)
uniform float blindness;                        blindness (0.0-1.0)
uniform float screenBrightness;                 screen brightness (0.0-1.0)
uniform int hideGUI;                            GUI is hidden
uniform float centerDepthSmooth;                centerDepth smoothed with centerDepthSmoothHalflife
uniform ivec2 atlasSize;                        texture atlas size (only set when the atlas texture is bound)
uniform vec4 spriteBounds;                      sprite bounds in the texture atlas (u0, v0, u1, v1), set when MC_ANISOTROPIC_FILTERING is enabled
uniform vec4 entityColor;                       entity color multiplier (entity hurt, creeper flashing when exploding)
uniform int entityId;                           entity ID
uniform int blockEntityId;                      block entity ID (block ID for the tile entity, only for blocks specified in "block.properties")
uniform ivec4 blendFunc;                        blend function (srcRGB, dstRGB, srcAlpha, dstAlpha)
uniform int instanceId;                         instance ID when instancing is enabled (countInstances > 1), 0 = original, 1-N = copies
uniform float playerMood;                       player mood (0.0-1.0), increases the longer a player stays underground
uniform int renderStage;                        render stage, see "Standard Macros", "J. Render stages"
uniform int bossBattle;                         1 = custom, 2 = ender dragon, 3 = wither, 4 = raid
// 1.17+
uniform mat4 modelViewMatrix;                   model view matrix
uniform mat4 modelViewMatrixInverse;            inverse model view matrix
uniform mat4 projectionMatrix;                  projection matrix
uniform mat4 projectionMatrixInverse;           inverse projection matrix
uniform mat4 textureMatrix = mat4(1.0);         texture matrix, default is identity
uniform mat3 normalMatrix;                      normal matrix
uniform vec3 modelOffset;                       used by terrain chunks (with attribute "vaPosition") and clouds, replaces chunkOffset (1.21.2+)
uniform float alphaTestRef;                     alpha test reference value, the check is "if (color.a < alphaTestRef) discard;"
// 1.19+
uniform float darknessFactor;                   strength of the darkness effect (0.0-1.0)
uniform float darknessLightFactor;              lightmap variations caused by the darkness effect (0.0-1.0) 

Constants
=====================================================================================================================================================================
// Lightmap texture matrix, 1.17+
const mat4 TEXTURE_MATRIX_2 = mat4(vec4(0.00390625, 0.0, 0.0, 0.0), vec4(0.0, 0.00390625, 0.0, 0.0), vec4(0.0, 0.0, 0.00390625, 0.0), vec4(0.03125, 0.03125, 0.03125, 1.0));

GBuffers Uniforms
================= 
Programs: basic, textured, textured_lit, skybasic, skytextured, clouds, terrain, terrain_solid, terrain_cutout_mip, terrain_cutout, damagedblock, water, block, beaconbeam, item, entities, armor_glint, spidereyes, hand, hand_water, weather)
==================
Source                                          Value                                                    
=====================================================================================================================================================================
uniform sampler2D gtexture;                     0
uniform sampler2D lightmap;                     1
uniform sampler2D normals;                      2         
uniform sampler2D specular;                     3
uniform sampler2D shadow;                       waterShadowEnabled ? 5 : 4
uniform sampler2D watershadow;                  4
uniform sampler2D shadowtex0;                   4
uniform sampler2D shadowtex1;                   5
uniform sampler2D depthtex0;                    6
uniform sampler2D gaux1;                        7  <custom texture or output from deferred programs>
uniform sampler2D gaux2;                        8  <custom texture or output from deferred programs>
uniform sampler2D gaux3;                        9  <custom texture or output from deferred programs>
uniform sampler2D gaux4;                        10 <custom texture or output from deferred programs>
uniform sampler2D colortex4;                    7  <custom texture or output from deferred programs>
uniform sampler2D colortex5;                    8  <custom texture or output from deferred programs>
uniform sampler2D colortex6;                    9  <custom texture or output from deferred programs>
uniform sampler2D colortex7;                    10 <custom texture or output from deferred programs>
uniform sampler2D colortex8;                    16 <custom texture or output from deferred programs>
uniform sampler2D colortex9;                    17 <custom texture or output from deferred programs>
uniform sampler2D colortex10;                   18 <custom texture or output from deferred programs>
uniform sampler2D colortex11;                   19 <custom texture or output from deferred programs>
uniform sampler2D colortex12;                   20 <custom texture or output from deferred programs>
uniform sampler2D colortex13;                   21 <custom texture or output from deferred programs>
uniform sampler2D colortex14;                   22 <custom texture or output from deferred programs>
uniform sampler2D colortex15;                   23 <custom texture or output from deferred programs>
uniform sampler2D depthtex1;                    11
uniform sampler2D shadowcolor;                  13
uniform sampler2D shadowcolor0;                 13
uniform sampler2D shadowcolor1;                 14
uniform sampler2D noisetex;                     15

Shadow Uniforms
==================
Programs: shadow, shadow_solid, shadow_cutout 
==================
Source                                          Value                                                    
=====================================================================================================================================================================
uniform sampler2D tex;                          0
uniform sampler2D gtexture;                     0
uniform sampler2D lightmap;                     1
uniform sampler2D normals;                      2         
uniform sampler2D specular;                     3
uniform sampler2D shadow;                       waterShadowEnabled ? 5 : 4
uniform sampler2D watershadow;                  4
uniform sampler2D shadowtex0;                   4
uniform sampler2D shadowtex1;                   5
uniform sampler2D gaux1;                        7  <custom texture>
uniform sampler2D gaux2;                        8  <custom texture>
uniform sampler2D gaux3;                        9  <custom texture>
uniform sampler2D gaux4;                        10 <custom texture>
uniform sampler2D colortex4;                    7  <custom texture>
uniform sampler2D colortex5;                    8  <custom texture>
uniform sampler2D colortex6;                    9  <custom texture>
uniform sampler2D colortex7;                    10 <custom texture>
uniform sampler2D colortex8;                    16 <custom texture>
uniform sampler2D colortex9;                    17 <custom texture>
uniform sampler2D colortex10;                   18 <custom texture>
uniform sampler2D colortex11;                   19 <custom texture>
uniform sampler2D colortex12;                   20 <custom texture>
uniform sampler2D colortex13;                   21 <custom texture>
uniform sampler2D colortex14;                   22 <custom texture>
uniform sampler2D colortex15;                   23 <custom texture>
uniform sampler2D shadowcolor;                  13
uniform sampler2D shadowcolor0;                 13
uniform sampler2D shadowcolor1;                 14
uniform sampler2D noisetex;                     15

Composite and Deferred Uniforms
===============================
Programs: composite, composite1, composite2, composite3, composite4, composite5, composite6, composite7, final, deferred, deferred1, deferred2, deferred3, deferred4, deferred5, deferred6, deferred7
===============================
Source                                          Value                                                    
=====================================================================================================================================================================
uniform sampler2D gcolor;                       0
uniform sampler2D gdepth;                       1
uniform sampler2D gnormal;                      2
uniform sampler2D composite;                    3
uniform sampler2D gaux1;                        7
uniform sampler2D gaux2;                        8
uniform sampler2D gaux3;                        9
uniform sampler2D gaux4;                        10
uniform sampler2D colortex0;                    0
uniform sampler2D colortex1;                    1
uniform sampler2D colortex2;                    2
uniform sampler2D colortex3;                    3
uniform sampler2D colortex4;                    7
uniform sampler2D colortex5;                    8
uniform sampler2D colortex6;                    9
uniform sampler2D colortex7;                    10
uniform sampler2D colortex8;                    16 
uniform sampler2D colortex9;                    17 
uniform sampler2D colortex10;                   18 
uniform sampler2D colortex11;                   19 
uniform sampler2D colortex12;                   20 
uniform sampler2D colortex13;                   21 
uniform sampler2D colortex14;                   22 
uniform sampler2D colortex15;                   23 
uniform sampler2D shadow;                       waterShadowEnabled ? 5 : 4
uniform sampler2D watershadow;                  4
uniform sampler2D shadowtex0;                   4
uniform sampler2D shadowtex1;                   5
uniform sampler2D gdepthtex;                    6
uniform sampler2D depthtex0;                    6
uniform sampler2D depthtex1;                    11
uniform sampler2D depthtex2;                    12
uniform sampler2D shadowcolor;                  13
uniform sampler2D shadowcolor0;                 13
uniform sampler2D shadowcolor1;                 14
uniform sampler2D noisetex;                     15

GBuffers Textures
=================
Id Name           Legacy name
======================================
0  gtexture       texture
1  lightmap
2  normals
3  specular
4  shadowtex0     shadow, watershadow 
5  shadowtex1     shadow (when watershadow used)
6  depthtex0
7  gaux1          colortex4 <custom texture or output from deferred programs>
8  gaux2          colortex5 <custom texture or output from deferred programs>
9  gaux3          colortex6 <custom texture or output from deferred programs>
10 gaux4          colortex7 <custom texture or output from deferred programs>
12 depthtex1
13 shadowcolor0   shadowcolor 
14 shadowcolor1
15 noisetex
16 colortex8      <custom texture or output from deferred programs>
17 colortex9      <custom texture or output from deferred programs>
18 colortex10     <custom texture or output from deferred programs>
19 colortex11     <custom texture or output from deferred programs>
20 colortex12     <custom texture or output from deferred programs>
21 colortex13     <custom texture or output from deferred programs>
22 colortex14     <custom texture or output from deferred programs>
23 colortex15     <custom texture or output from deferred programs>

Shadow Textures
==================
Id Name           Legacy name
======================================
0  gtexture       tex, texture
1  lightmap
2  normals
3  specular
4  shadowtex0     shadow, watershadow        
5  shadowtex1     shadow (when watershadow used)
7  gaux1          colortex4 <custom texture>
8  gaux2          colortex5 <custom texture>
9  gaux3          colortex6 <custom texture>
10 gaux4          colortex7 <custom texture>
13 shadowcolor0   shadowcolor
14 shadowcolor1   
15 noisetex
16 colortex8      <custom texture>
17 colortex9      <custom texture>
18 colortex10     <custom texture>
19 colortex11     <custom texture>
20 colortex12     <custom texture>
21 colortex13     <custom texture>
22 colortex14     <custom texture>
23 colortex15     <custom texture>

Composite and Deferred Textures
===============================
Id Name           Legacy name
======================================
0  colortex0      gcolor 
1  colortex1      gdepth 
2  colortex2      gnormal 
3  colortex3      composite
4  shadowtex0     shadow, watershadow 
5  shadowtex1     shadow (when watershadow used)
6  depthtex0      gdepthtex
7  colortex4      gaux1
8  colortex5      gaux2
9  colortex6      gaux3
10 colortex7      gaux4
11 depthtex1
12 depthtex2
13 shadowcolor0   shadowcolor
14 shadowcolor1
15 noisetex
16 colortex8
17 colortex9
18 colortex10
19 colortex11
20 colortex12
21 colortex13
22 colortex14
23 colortex15

Depth buffers usage
===================
Name        Usage
==============================================================================
depthtex0   everything
depthtex1   no translucent objects (water, stained glass) 
depthtex2   no translucent objects (water, stained glass), no handheld objects

Shadow buffers usage
====================
Name        Usage
==============================================================================
shadowtex0  everything
shadowtex1  no translucent objects (water, stained glass) 

Vertex Shader Configuration
===========================
Source                                          Effect                                                    Comment
=====================================================================================================================================================================
in vec3 mc_Entity;                              useEntityAttrib = true
in vec2 mc_midTexCoord;                         useMidTexCoordAttrib = true             
in vec4 at_tangent;                             useTangentAttrib = true
const int countInstances = 1;                   when "countInstances > 1" the geometry will be rendered several times, see uniform "instanceId"

Geometry Shader Configuration
===========================
Source                                          Effect                                                    Comment
=====================================================================================================================================================================
#extension GL_ARB_geometry_shader4 : enable     Enable GL_ARB_geometry_shader4
const int maxVerticesOut = 3;                   Set GEOMETRY_VERTICES_OUT_ARB for GL_ARB_geometry_shader4 

Fragment Shader Configuration
=============================
Source                                          Effect                                                     Comment
=====================================================================================================================================================================
uniform <type> shadow;                          shadowDepthBuffers = 1
uniform <type> watershadow;                     shadowDepthBuffers = 2
uniform <type> shadowtex0;                      shadowDepthBuffers = 1
uniform <type> shadowtex1;                      shadowDepthBuffers = 2
uniform <type> shadowcolor;                     shadowColorBuffers = 1
uniform <type> shadowcolor0;                    shadowColorBuffers = 1
uniform <type> shadowcolor1;                    shadowColorBuffers = 2
uniform <type> depthtex0;                       depthBuffers = 1
uniform <type> depthtex1;                       depthBuffers = 2
uniform <type> depthtex2;                       depthBuffers = 3
uniform <type> gdepth;                          if (bufferFormat[1] == RGBA) bufferFormat[1] = RGBA32F;
uniform <type> gaux1;                           colorBuffers = 5
uniform <type> gaux2;                           colorBuffers = 6
uniform <type> gaux3;                           colorBuffers = 7
uniform <type> gaux4;                           colorBuffers = 8
uniform <type> colortex4;                       colorBuffers = 5
uniform <type> colortex5;                       colorBuffers = 6
uniform <type> colortex6;                       colorBuffers = 7
uniform <type> colortex7;                       colorBuffers = 8
uniform <type> centerDepthSmooth;               centerDepthSmooth = true
/* SHADOWRES:1024 */                            shadowMapWidth = shadowMapHeight = 1024
const int shadowMapResolution = 1024;           shadowMapWidth = shadowMapHeight = 1024
/* SHADOWFOV:90.0 */                            shadowMapFov = 90
const float shadowMapFov = 90.0;                shadowMapFov = 90
/* SHADOWHPL:160.0 */                           shadowMapDistance = 160.0
const float shadowDistance = 160.0f;            shadowMapDistance = 160.0
const float shadowDistanceRenderMul = -1f;      shadowDistanceRenderMul = -1                               When > 0 enable shadow optimization (shadowRenderDistance = shadowDistance * shadowDistanceRenderMul)
const float shadowIntervalSize = 2.0f;          shadowIntervalSize = 2.0
const bool generateShadowMipmap = true;         shadowMipmap = true
const bool generateShadowColorMipmap = true;    shadowColorMipmap = true
const bool shadowHardwareFiltering = true;      shadowHardwareFiltering = true
const bool shadowHardwareFiltering0 = true;     shadowHardwareFiltering[0] = true
const bool shadowHardwareFiltering1 = true;     shadowHardwareFiltering[1] = true
const bool shadowtexMipmap = true;              shadowMipmap[0] = true
const bool shadowtex0Mipmap = true;             shadowMipmap[0] = true
const bool shadowtex1Mipmap = true;             shadowMipmap[1] = true
const bool shadowcolor0Mipmap = true;           shadowColorMipmap[0] = true
const bool shadowColor0Mipmap = true;           shadowColorMipmap[0] = true
const bool shadowcolor1Mipmap = true;           shadowColorMipmap[1] = true
const bool shadowColor1Mipmap = true;           shadowColorMipmap[1] = true
const bool shadowtexNearest = true;             shadowFilterNearest[0] = true
const bool shadowtex0Nearest = true;            shadowFilterNearest[0] = true
const bool shadow0MinMagNearest = true;         shadowFilterNearest[0] = true
const bool shadowtex1Nearest = true;            shadowFilterNearest[1] = true
const bool shadow1MinMagNearest = true;         shadowFilterNearest[1] = true
const bool shadowcolor0Nearest = true;          shadowColorFilterNearest[0] = true
const bool shadowColor0Nearest = true;          shadowColorFilterNearest[0] = true
const bool shadowColor0MinMagNearest = true;    shadowColorFilterNearest[0] = true
const bool shadowcolor1Nearest = true;          shadowColorFilterNearest[1] = true
const bool shadowColor1Nearest = true;          shadowColorFilterNearest[1] = true
const bool shadowColor1MinMagNearest = true;    shadowColorFilterNearest[1] = true
/* WETNESSHL:600.0 */                           wetnessHalfLife = 600 (ticks)
const float wetnessHalflife = 600.0f;           wetnessHalfLife = 600 (ticks)
/* DRYNESSHL:200.0 */                           drynessHalfLife = 200 (ticks)
const float drynessHalflife = 200.0f;           drynessHalfLife = 200 (ticks)
const float eyeBrightnessHalflife = 10.0f;      eyeBrightnessHalflife = 10 (ticks)
const float centerDepthHalflife = 1.0f;         centerDepthSmoothHalflife = 1 (ticks)
const float sunPathRotation = 0f;               sunPathRotation = 0f
const float ambientOcclusionLevel = 1.0f;       ambientOcclusionLevel = 1.0f                               0.0f = AO disabled, 1.0f = vanilla AO
const int superSamplingLevel = 1;               superSamplingLevel = 1
const int noiseTextureResolution = 256;         noiseTextureResolution = 256
/* GAUX4FORMAT:RGBA32F */                       buffersFormat[7] = GL_RGBA32F
/* GAUX4FORMAT:RGB32F */                        buffersFormat[7] = GL_RGB32F
/* GAUX4FORMAT:RGB16 */                         buffersFormat[7] = GL_RGB16
const int <bufferIndex>Format = <format>;       bufferFormats[index] = <format>                            See "Draw Buffer Index" and "Texture Formats"
const bool <bufferIndex>Clear = false;          gbuffersClear[index] = false                               Skip glClear() for the given buffer, only for "composite" and "deferred" programs 
const vec4 <bufferIndex>ClearColor = vec4();    gbuffersClearColor[index] = vec4(r, g, b, a)               Clear color for the given buffer, only for "composite" and "deferred" programs 
const bool <bufferIndex>MipmapEnabled = true;   bufferMipmaps[index] = true                                Only for programs "composite" , "deferred" and "final"
const int <shadowBufferIx>Format = <format>;    shadowBufferFormats[index] = <format>                      See "Shadow Buffer Index" and "Texture Formats"
const bool <shadowBufferIx>Clear = false;       shadowBuffersClear[index] = false                          Skip glClear() for the given shadow color buffer 
const vec4 <shadowBufferIx>ClearColor = vec4(); shadowBuffersClearColor[index] = vec4(r, g, b, a)          Clear color for the given shadow color buffer
/* DRAWBUFFERS:0257 */                          drawBuffers = {0, 2, 5, 7)                                 Only buffers 0 to 9 can be used.
/* RENDERTARGETS: 0,2,11,15 */                  drawBuffers = {0, 2, 11, 15}                               Buffers 0 to 15 can be used

Draw Buffer Index
=================
Prefix                  Index
==================================
colortex<0-15>          0-15
gcolor                  0
gdepth                  1
gnormal                 2
composite               3
gaux1                   4
gaux2                   5
gaux3                   6
gaux4                   7

Shadow Buffer Index
===================
Prefix                  Index
==================================
shadowcolor             0
shadowcolor<0-1>        0-1
 
Texture Formats
===============
1. 8-bit
 Normalized         Signed normalized  Integer            Unsigned integer
 =================  =================  =================  =================
 R8                 R8_SNORM           R8I                R8I
 RG8                RG8_SNORM          RG8I               RG8I
 RGB8               RGB8_SNORM         RGB8I              RGB8I
 RGBA8              RGBA8_SNORM        RGBA8I             RGBA8I
2. 16-bit
 Normalized         Signed normalized  Float              Integer            Unsigned integer
 =================  =================  =================  =================  =================
 R16                R16_SNORM          R16F               R16I               R16UI    
 RG16               RG16_SNORM         RG16F              RG16I              RG16UI   
 RGB16              RGB16_SNORM        RGB16F             RGB16I             RGB16UI  
 RGBA16             RGBA16_SNORM       RGBA16F            RGBA16I            RGBA16UI 
3. 32-bit
 Float              Integer            Unsigned integer
 =================  =================  =================
 R32F               R32I               R32UI
 RG32F              RG32I              RG32UI
 RGB32F             RGB32I             RGB32UI
 RGBA32F            RGBA32I            RGBA32UI
4. Mixed
 R3_G3_B2
 RGB5_A1
 RGB10_A2
 R11F_G11F_B10F
 RGB9_E5

Pixel Formats
=============
1. Normalized
 RED
 RG
 RGB
 BGR
 RGBA
 BGRA
2. Integer
 RED_INTEGER
 RG_INTEGER
 RGB_INTEGER
 BGR_INTEGER
 RGBA_INTEGER
 BGRA_INTEGER

Pixel Types
===========
 BYTE
 SHORT
 INT
 HALF_FLOAT
 FLOAT
 UNSIGNED_BYTE
 UNSIGNED_BYTE_3_3_2
 UNSIGNED_BYTE_2_3_3_REV
 UNSIGNED_SHORT
 UNSIGNED_SHORT_5_6_5
 UNSIGNED_SHORT_5_6_5_REV
 UNSIGNED_SHORT_4_4_4_4
 UNSIGNED_SHORT_4_4_4_4_REV
 UNSIGNED_SHORT_5_5_5_1
 UNSIGNED_SHORT_1_5_5_5_REV
 UNSIGNED_INT
 UNSIGNED_INT_8_8_8_8
 UNSIGNED_INT_8_8_8_8_REV
 UNSIGNED_INT_10_10_10_2
 UNSIGNED_INT_2_10_10_10_REV

Block ID mapping
================
The block ID mapping is defined in "shaders/block.properties" included in the shader pack.
Forge mods may add custom block mapping as "assets/<modid>/shaders/block.properties" in the mod JAR file.
The "block.properties" file can use conditional preprocessor directives (#ifdef, #if, etc.)
For more details see section "Standard Macros" A to I. Option macros are also available.
Format "block.<id>=<block1> <block2> ..."
The key is the substitute block ID, the values are the blocks which are to be replaced.
Only one line per block ID is allowed.
See "properties_files.txt" for the block matching rules.

  # Short format
  block.31=red_flower yellow_flower reeds
  # Long format
  block.32=minecraft:red_flower ic2:nether_flower botania:reeds
  # Properties
  block.33=minecraft:red_flower:type=white_tulip minecraft:red_flower:type=pink_tulip botania:reeds:type=green

See "properties.files" for more details.

Block render layers
===================
The custom block render layers are defined in "shaders/block.properties" included in the shader pack.

  layer.solid=<blocks>
  layer.cutout=<blocks>
  layer.cutout_mipped=<blocks>
  layer.translucent=<blocks>

Layers
  solid - no alpha, no blending (solid textures)
  cutout - alpha, no blending (cutout textures)
  cutout_mipped - alpha, no blending, mipmaps (cutout with mipmaps)
  translucent - alpha, blending, mipmaps (water, stained glass)
 
Blocks which are solid opaque cubes (stone, dirt, ores, etc) can't be rendered on a custom layer
as this would affect face culling, ambient occlusion, light propagation and so on.

For exaple:
  layer.translucent=glass_pane fence wooden_door

Item ID mapping
================
The item ID mapping is defined in "shaders/item.properties" included in the shader pack.
Forge mods may add custom item mapping as "assets/<modid>/shaders/item.properties" in the mod JAR file.
The "item.properties" file can use conditional preprocessor directives (#ifdef, #if, etc.)
For more details see section "Standard Macros" A to I. Option macros are also available.
Format "item.<id>=<item1> <item2> ..."
The key is the substitute item ID, the values are the items which are to be replaced.
Only one line per item ID is allowed.

  # Short format
  item.5000=diamond_sword dirt
  # Long format
  item.5001=minecraft:diamond_sword botania:reeds

Entity ID mapping
=================
The entity ID mapping is defined in "shaders/entity.properties" included in the shader pack.
Forge mods may add custom entity mapping as "assets/<modid>/shaders/entity.properties" in the mod JAR file.
The "entity.properties" file can use conditional preprocessor directives (#ifdef, #if, etc.)
For more details see section "Standard Macros" A to I. Option macros are also available.
Format "entity.<id>=<entity1> <entity2> ..."
The key is the substitute entity ID, the values are the entities which are to be replaced.
Only one line per entity ID is allowed.

  # Short format
  entity.2000=sheep cow
  # Long format
  entity.2001=minecraft:pig botania:pixie

Standard Macros
===============
The standard macros are automatically included after the "#version" declaration in every shader file

A. Minecraft version
 #define MC_VERSION <value>
 The value is in format 122 (major 1, minor 2, release 2)
 For example: 1.9.4 -> 10904, 1.11.2 -> 11102, etc.

B. Maximum supported GL version
 #define MC_GL_VERSION <value>
 The value is integer, for example: 210, 320, 450

C. Maximum supported GLSL version
 #define MC_GLSL_VERSION <value>
 The value is integer, for example: 120, 150, 450

D. Operating system 
 One of the following:
  #define MC_OS_WINDOWS
  #define MC_OS_MAC
  #define MC_OS_LINUX
  #define MC_OS_OTHER

E. Driver
 One of the following:
  #define MC_GL_VENDOR_AMD
  #define MC_GL_VENDOR_ATI
  #define MC_GL_VENDOR_INTEL
  #define MC_GL_VENDOR_MESA
  #define MC_GL_VENDOR_NVIDIA
  #define MC_GL_VENDOR_XORG
  #define MC_GL_VENDOR_OTHER

F. GPU
 One of the following:
  #define MC_GL_RENDERER_RADEON 
  #define MC_GL_RENDERER_GEFORCE
  #define MC_GL_RENDERER_QUADRO
  #define MC_GL_RENDERER_INTEL
  #define MC_GL_RENDERER_GALLIUM
  #define MC_GL_RENDERER_MESA
  #define MC_GL_RENDERER_OTHER

G. OpenGL extensions
 Macros for the supported OpenGL extensions are named like the corresponding extension with a prefix "MC_".
 For example the macro "MC_GL_ARB_shader_texture_lod" is defined when the extension "GL_ARB_shader_texture_lod" is supported.
 Only the macros which are referenced and supported are added to the shader file.

H. Options
 #define MC_FXAA_LEVEL <value>             // When FXAA is enabled, values: 2, 4
 #define MC_NORMAL_MAP                     // When the normal map is enabled
 #define MC_SPECULAR_MAP                   // When the specular map is enabled
 #define MC_RENDER_QUALITY <value>         // Values: 0.5, 0.70710677, 1.0, 1.4142135, 2.0
 #define MC_SHADOW_QUALITY <value>         // Values: 0.5, 0.70710677, 1.0, 1.4142135, 2.0
 #define MC_HAND_DEPTH <value>             // Values: 0.0625, 0.125, 0.25
 #define MC_OLD_HAND_LIGHT                 // When Old Hand Light is enabled
 #define MC_OLD_LIGHTING                   // When Old Lighting is enabled
 #define MC_ANISOTROPIC_FILTERING <value>  // When anisotropic filtering is enabled

I. Textures 
 #define MC_TEXTURE_FORMAT_LAB_PBR       // Texture format LabPBR (https://github.com/rre36/lab-pbr/wiki)
 #define MC_TEXTURE_FORMAT_LAB_PBR_1_3   // Version 1.3
 (see "texture.properties")

J. Render stages
 // Constants for the uniform "renderStage"
 // The constants are given in the order in which the stages are executed
 #define MC_RENDER_STAGE_NONE <const>                    // Undefined
 #define MC_RENDER_STAGE_SKY <const>                     // Sky
 #define MC_RENDER_STAGE_SUNSET <const>                  // Sunset and sunrise overlay
 #define MC_RENDER_STAGE_CUSTOM_SKY <const>              // Custom sky
 #define MC_RENDER_STAGE_SUN <const>                     // Sun
 #define MC_RENDER_STAGE_MOON <const>                    // Moon
 #define MC_RENDER_STAGE_STARS <const>                   // Stars
 #define MC_RENDER_STAGE_VOID <const>                    // Void
 #define MC_RENDER_STAGE_TERRAIN_SOLID <const>           // Terrain solid
 #define MC_RENDER_STAGE_TERRAIN_CUTOUT_MIPPED <const>   // Terrain cutout mipped
 #define MC_RENDER_STAGE_TERRAIN_CUTOUT <const>          // Terrain cutout
 #define MC_RENDER_STAGE_ENTITIES <const>                // Entities
 #define MC_RENDER_STAGE_BLOCK_ENTITIES <const>          // Block entities
 #define MC_RENDER_STAGE_DESTROY <const>                 // Destroy overlay
 #define MC_RENDER_STAGE_OUTLINE <const>                 // Selection outline
 #define MC_RENDER_STAGE_DEBUG <const>                   // Debug renderers
 #define MC_RENDER_STAGE_HAND_SOLID <const>              // Solid handheld objects
 #define MC_RENDER_STAGE_TERRAIN_TRANSLUCENT <const>     // Terrain translucent
 #define MC_RENDER_STAGE_TRIPWIRE <const>                // Tripwire string
 #define MC_RENDER_STAGE_PARTICLES <const>               // Particles
 #define MC_RENDER_STAGE_CLOUDS <const>                  // Clouds
 #define MC_RENDER_STAGE_RAIN_SNOW <const>               // Rain and snow
 #define MC_RENDER_STAGE_WORLD_BORDER <const>            // World border
 #define MC_RENDER_STAGE_HAND_TRANSLUCENT <const>        // Translucent handheld objects

References
==========
 http://daxnitro.wikia.com/wiki/Editing_Shaders_%28Shaders2%29
 http://www.minecraftforum.net/forums/mapping-and-modding/minecraft-mods/1286604-shaders-mod-updated-by-karyonix
 http://www.minecraftforum.net/forums/search?by-author=karyonix&display-type=posts
 http://www.seas.upenn.edu/~cis565/fbo.htm#feedback

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

Great, I’ll gather information on the following:

1. Any formal style guides or linting tools specifically for GLSL, VSH, and FSH shader files.
2. Documentation and best practices for AI-generated Minecraft shaders.
3. Examples or templates of well-styled Minecraft shader code.

I’ll review resources such as open-source shader repositories, shader development documentation, and Minecraft shader modding communities. I’ll update you shortly with the findings.


# Shader Code Style and AI-Generated Shaders in Minecraft

## 1. Style Guides and Linters for GLSL Shaders (GLSL, *.vsh*, *.fsh*)

**Formal Style Conventions:** Professional projects often follow C/C++ style guidelines adapted to GLSL. For example, Blender’s **GLSL Style Guide** advises using clear suffixes (`_vert`, `_frag`, `_geom`, `_comp`) for shader file names and descriptive variable names (with module-specific prefixes to avoid collisions). It also suggests naming variables with common category words first and specifics last (and avoiding names that shadow GLSL reserved words like `sampler`). Similarly, the Godot Engine’s **Shader Style Guide** emphasizes consistent formatting: use the **1TBS** brace style (open brace on the same line as `if`/`for`/function, and always include braces even for one-liners). Keep one statement per line and avoid merging multiple commands with semicolons. Indentation and spacing are important for readability – e.g. Godot uses tabs for indent and mandates a space around operators and after commas. Many guides also recommend limiting line length (e.g. 80-100 chars) and using comments to document complex logic.

**Naming Conventions (Files & Variables):** There isn’t a single universal shader file extension – different engines and communities use various conventions. Common practice in OpenGL tooling is to use *.vert* for vertex shaders and *.frag* for fragment shaders (sometimes *.vs* and *.fs* are used as shorter forms). Other stages follow similar patterns (*.geom* or *.gs* for geometry, *.comp* for compute, etc.). In Minecraft’s modding community (OptiFine/Iris), shaders typically use the **“.vsh”** extension for vertex shaders and **“.fsh”** for fragment shaders. (Older Minecraft shader mods were even named “GLSL Shaders,” reflecting the GLSL code inside.) Variable and function naming within shader code should be clear and consistent. Style guides recommend using **descriptive names** (e.g. `sunLightFactor` instead of `f1`) and sometimes prefixing with a subsystem for uniqueness in large projects. It’s also good practice to group related uniforms or inputs together and comment them. For example, sorting uniform declarations alphabetically or by purpose can make the shader easier to read.

**Linting & Formatting Tools:** Maintaining consistent style is easier with tools. A primary tool for GLSL is **Khronos’s glslangValidator**, which isn’t exactly a style linter but a compiler/validator that catches errors – many editors integrate it to provide real-time feedback. The **GLSL Lint** extension for VS Code uses glslangValidator under the hood to validate shader files on the fly. It supports all shader stages that glslangValidator does, and even allows linting of shader code inside strings (for example, in JavaScript files) with special `#pragma` hints. This extension also recognizes multiple file extensions by default – e.g. treating *.vert* or *.vs* as vertex stage, *.frag* or *.fs* as fragment stage, etc. – and can be configured with additional mappings. For formatting (style consistency like indentation, line breaks), one option is **GLSLX** by Evan Wallance, which is a GLSL type-checker *and code formatter*. It can automatically reformat shader code according to a set of rules and even minify/obfuscate if needed, which is useful for catching mistakes and enforcing structure (GLSLX will, for example, insert required `#extension` statements and ensure types match). Another tool, **glslfmt** (from the stack.gl ecosystem), can prettify GLSL code, though it’s less widely used. Beyond linters, **editor support** is key: the VS Code extension **“Shader Languages Support”** provides syntax highlighting and basic formatting for *.glsl*, *.vsh*, *.fsh* files, and plugins exist for other editors (Vim, Emacs, etc.) to enforce indentation and highlight syntax.

**Helpful Practices:** In absence of an official GLSL style standard, many teams adopt the **style of the host language** (e.g. if your game engine code is in C++, follow C++ naming/bracing style in shaders too). The Blender docs explicitly say “follow the C/C++ Style Guide even in GLSL files”. This means things like all **constants ALL\_CAPS**, camelCase or snake\_case consistently for variables, and using `//` for comments (since GLSL supports C++-style `//` comments, many style guides prefer them over `/*…*/` for single-line comments). In fact, Blender’s GLSL guidelines even note to prefer `//` for commenting and avoid block comments except when necessary (to prevent nesting issues). Overall, the goal is to treat shader code with the same rigor as normal source code: clear organization, consistent naming, and comments for clarity.

**Automated Formatting:** While not as common as in C/C++, automated formatters do exist. GLSLX (mentioned above) can be run as a CLI or Node module to auto-format code. Some teams use **clang-format** with custom rules for GLSL, since GLSL syntax is C-like – this can enforce indent sizes, bracket placement, etc. Another approach is using an IDE’s C/C++ formatter by associating \*.glsl or \*.vsh files with C syntax – this won’t catch shader-specific issues but can uniformly format braces and indents. There’s also **glslify** (a Node-based preprocessor for GLSL) which isn’t a formatter per se, but it encourages writing modular, maintainable shader code by allowing you to `#pragma glslify: import` common functionality. In practice, glslify can be combined with a linter: for instance, the VSCode GLSL extension has optional glslify integration to resolve includes before linting. This means you can keep your shader code clean (small includes for noise, lighting functions, etc.) and still lint the whole program – a big win for maintainability.

## 2. AI-Generated Minecraft Shaders – Best Practices and Tools

**AI Tools for Shader Generation:** Recently, developers have started using large language models (LLMs) to generate GLSL shader code. The most commonly used are **OpenAI’s ChatGPT** (or Codex, which powers GitHub Copilot) – these can take a description (e.g. “a GLSL fragment shader that applies a cel-shaded outline effect”) and produce code. In fact, GitHub Copilot can autocomplete shader functions inside your editor. There are also experiments like **Keijiro’s AIShader** (an open-source Unity plugin) which hook up ChatGPT’s API to generate Unity shaders on demand. For Minecraft specifically, there isn’t a specialized “shader AI,” so modders use general code models. ChatGPT (GPT-4 in 2025) is quite capable of outputting syntactically correct GLSL for Minecraft’s shader pipeline, given the right prompt (including the GLSL version and any specific OptiFine context like `uniform` inputs). Other AI tools used include **text-to-code generators** like Google’s Codey or Meta’s Code Llama, but these are less tested on shader code than ChatGPT/Codex.

**Generation Techniques:** When using AI for shaders, prompt engineering is important. You should **specify the shader stage and any constraints** in your prompt. For example: *“Write an OpenGL GLSL **fragment shader** for Minecraft (OptiFine) that implements water waves. Use version 150 compatibility, and assume a uniform `time`.”* Providing the GLSL `#version` and known uniforms upfront helps the AI produce code that fits Minecraft’s environment. Some creators iterate by **conversational refinement** – you ask for a basic shader, then ask follow-up tweaks (e.g. “now add fog blending to that shader”). This iterative approach is essentially using the AI as a coding assistant.

However, **experience shows AI-generated shaders usually need manual fixes**. One developer’s account of experimenting with GPT-3 to make Shadertoy/Minecraft-style shaders noted that *“about 99% of \[the AI’s shaders] are broken or look awful”* without intervention. Common issues include:

* *Incorrect or “hallucinated” functions and variables:* The AI might call a function like `noise()` or use a uniform `uLightPos` that it assumed exists, when in reality you have no such function/uniform defined. These missing references cause compile errors or just no effect – they happen because the model has seen shader code using custom noise functions, etc., and tries to use them out of context.
* *Type mismatches and syntax errors:* It’s common to see an AI confuse `vec3` vs `vec4`, or try to assign a float to a vec3, etc.. GLSL is strongly typed, so these errors prevent compilation. Similarly, an AI might forget a semicolon or misuse a GLSL keyword (like using `texture2D` in a core #version 330 shader where it should use `texture`).
* *Logic flaws:* Even if the shader compiles, the effect might not behave as intended. The AI could implement an algorithm incorrectly – e.g., miscalculate lighting or normals – producing visual artifacts or extremely low performance. For instance, an AI might unknowingly write an unbounded loop or too high instruction count for a fragment shader, causing huge lag.

**Validation & Optimization Guidelines:** To deal with AI’s mistakes, **verification is key**. Always run the generated shader through a compiler or Minecraft’s debug logs. OptiFine will log shader compile errors to `shaderpacks/debug` or the game output; those messages are invaluable. A best practice is to take those errors and feed them back to the AI: e.g. *“The shader code you gave has an error: ‘error X: undeclared identifier uLightPos’. Please fix that.”* Often, ChatGPT will apologize and correct the code once it “sees” the error message, essentially acting as a pair programmer debugging with you. This iterative refine-and-fix loop can quickly converge on a working shader. Some users even automate this: they have a script to test-compile AI output with *glslangValidator* or in-game, then loop back the errors for the AI to correct.

Another guideline is to **provide context to the AI beforehand**. In one case, a developer improved results by telling GPT what functions were available and the expected inputs/outputs (for example, “you can use a `noise()` function defined in an include” or “the shader has `uniform vec3 skyColor` available”). This reduces hallucinations. You can also ask the AI to comment its code – this often reveals its reasoning and can highlight if it misunderstood something (if the comment says “// use built-in noise() function” you know it assumed one exists).

**Optimization for Performance:** AI models won’t automatically optimize for GPU performance or Minecraft-specific quirks. It’s up to you to **review the code for efficiency**. For example, check that the AI isn’t doing expensive operations per pixel that could be done per vertex or once – e.g., moving heavy calculations from fragment shader to vertex shader if possible, or using a precomputed texture/LUT instead of a complex math function in the shader. If the AI gives you a working shader, profile it. Minecraft’s shader mod has an option to capture shader render times; use that to spot bottlenecks. Simple things like reducing **texture lookups** or using **lowp/mediump** precision (on GLES devices) can massively improve speed, but an AI won’t know to do that unless told. So consider prompting: *“optimize this shader by minimizing texture fetches and using vec3 instead of mat3 where possible”*. The AI might then unroll or simplify code. Still, **manual optimization and refactoring** is recommended – treat the AI output as a starting point.

**Current State (2025):** The quality of AI-generated shaders is improving rapidly. Early on, GPT-3 often produced non-compiling code that needed heavy debugging. Newer models like GPT-4 and others (the dev community even mentioned a model called **Grok** 3) have gotten much better – one user reported that *Grok 3 was able to generate shaders that worked on ShaderToy “copy, paste, and compile” with no fixes needed*. That’s promising, but you should still be prepared to verify everything. Remember that **Minecraft’s shader environment (OptiFine/Iris)** has its own set of uniforms, texture samplers, and version (largely GLSL 1.2/1.3 or 330 compatibility). Ensure the AI knows which version to target. If it writes `#version 450 core` shaders using SSBOs, that won’t run in Minecraft. Often specifying `#version 330 core` (or `compatibility`) in the prompt is necessary to get compatible code. In summary: AI can accelerate shader development – it’s great for brainstorming or writing boilerplate – but human oversight for correctness and performance is still required. Using linters and real-time shader compilers alongside the AI is the best practice (catch the mistakes early and loop back fixes).

## 3. Examples of Well-Styled Minecraft Shader Code (Templates & Repos)

**Base Shader Pack Templates:** A good starting point for a “well-styled” Minecraft shader is a base template pack created by the community. For example, the ShaderLabs community provides **“Base 330”**, a template shader pack that includes all the essential files and structure, but with no visual effects (essentially a no-op shader). It uses modern GLSL (#version 330) and is meant for MC 1.17+. The Base-330 pack demonstrates a clean folder layout: a `shaders/` directory containing stub files for each shader stage (e.g. empty `gbuffers_terrain.vsh/fsh`, `final.vsh/fsh`, etc.), all properly named. This gives new shader developers a styled starting point to fill in. Using such a template ensures you follow the expected naming and structure that OptiFine/Iris will recognize. *OptiFine’s official documentation* itself defines how to name and organize files: “All shader files are placed in the `shaders/` folder of the pack. The shader source files use the name of the program in which they are used, with extension depending on type”. For example, a program that renders terrain will have a vertex shader `gbuffers_terrain.vsh` and fragment shader `gbuffers_terrain.fsh`. OptiFine recognizes `.vsh` as a vertex shader, `.fsh` as fragment (and similarly `.gsh` for geometry, `.csh` for compute, etc., if used). Sticking to this naming scheme is part of writing “well-styled” Minecraft shaders – it’s both a convention and a requirement for the engine to load the stages correctly.

**Reputable Shader Packs (Style Examples):** Many popular shader packs have source code available (either published on GitHub or included in their zip) that illustrate good style. **BSL Shaders** by CaptTatsu, for instance, is known not only for its visual quality but also a relatively clean codebase. In forks like BSL++, you can see that the author kept the code organized by feature (water, lighting, etc.) and even removed unused features to keep it lean. Variable names in BSL are descriptive (`torchLightColor`, `skyLightIntensity`, etc.), and the pack makes heavy use of **includes** to avoid duplication (common math functions and lighting calculations reside in reusable *.inc* files). Another well-respected example is **Sildur’s Vibrant Shaders** – Sildur’s code is often praised for clarity. Each pass (shadow, g-buffer, composite) is in a separate file, with comments marking sections (e.g. *“// Volumetric Lighting”* in the composite shader). This modular separation of concerns (each file does one stage of the pipeline) is a hallmark of well-styled shader packs.

We also have open-source projects and tutorials demonstrating style. **Saad Amin’s “MinecraftShaderProgramming”** repository is a tutorial series for writing OptiFine shaders, and it doubles as an example of clean shader code structure. Each tutorial step in his repo is a working shader pack focusing on one effect, with ample comments and consistent formatting. For instance, in the *Advanced Lighting* tutorial, the code is neatly divided into sections for calculating diffuse light vs. specular, each with comments, and uses intuitive names like `normalVector` and `lightDir` instead of cryptic short names. Reviewing such community examples is extremely useful – they illustrate how to handle complexity while keeping code readable (e.g. using helper functions in GLSL, or preprocessor `#ifdef` blocks to toggle features, all properly indented and commented).

**Code Snippet – Example:** Below is a tiny excerpt from Iris’s shader development guide, showing a minimal shader program. This example is a grayscale post-processing shader, and it highlights clean and correct style:



```glsl
// composite.vsh – vertex shader for full-screen quad
#version 330 compatibility
out vec2 texcoord;
void main() {
    gl_Position = ftransform();                           // standard transform
    texcoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
}
```

```glsl
// composite.fsh – fragment shader that makes the final image grayscale
#version 330 compatibility
uniform sampler2D colortex0;
in vec2 texcoord;
layout(location = 0) out vec4 color;
void main() {
    vec4 orig = texture(colortex0, texcoord);
    float gray = dot(orig.rgb, vec3(0.33333));            // average RGB
    color = vec4(gray, gray, gray, orig.a);
}
```

*(Source: IrisShaders documentation tutorial)*

This snippet demonstrates a few stylistic best practices: Each shader file declares `#version` first. Uniforms and inputs are clearly listed at the top. The code is indented consistently inside the `main()` function, and commented to explain the grayscale calculation. Variable names (`orig`, `gray`, `texcoord`) are concise but meaningful. Even though this is very simple, **it’s easy to imagine scaling this style up** – a larger shader would have multiple sections separated by blank lines and comments, but still using consistent indentation and naming as shown.

**Maintaining Formatting:** To help keep shader code well-formatted, developers can use editor plugins or IDE features. For example, many pack authors write shaders in Visual Studio Code with the GLSL extensions mentioned, so they get **auto-indentation and syntax highlights**. Some also use **prettier or custom format configs** so that on save, the file is aligned to their style (inserting missing newline at EOF, trimming trailing spaces, etc., which are minor things but contribute to overall neatness). Additionally, integrating shaders into version control (GitHub) encourages clean diffs – if you consistently format your code, diffs will show logical changes rather than noise from re-indentation. ShaderLab’s Base-330 readme even notes that it’s Unlicensed (public domain) so that people can freely use it as a starting point – this implies the community wants newcomers to copy a good format instead of reinventing with poor style.

**Community Resources:** Finally, communities like the **ShaderLABS Discord** and forums on Minecraft shader development place a strong emphasis on code quality. They often share *“best practices”* like avoiding deep nesting (which makes shaders hard to debug) and using the **temporal recompilation** feature (OptiFine can output the post-preprocessor shader source for debugging). While those are more advanced topics, they all tie back to maintainable code. A well-styled shader is not just aesthetically pleasing, but also easier to optimize and less error-prone when making changes. By following established style guides, using proper naming and file organization, and leveraging tools (linters, formatters, template packs) to enforce consistency, you can ensure your Minecraft shader code remains clean and professional.

**Sources:** References include official style guides (Blender), community guides (Godot), the OptiFine shader documentation, VS Code Marketplace info for GLSL linters, and first-hand write-ups on AI-generated shaders. Example code and templates are drawn from Iris Shaders docs and ShaderLABS’ base pack, as well as open-source shader repositories. These illustrate the recommended practices in action.

