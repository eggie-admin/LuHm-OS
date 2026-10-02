shader_type spatial;

// Donor: MenacingMecha/godot-psx-style-demo (MIT)
#define LIT diffuse_lambert, vertex_lighting
#define CULL cull_back
#define DEPTH depth_draw_opaque
#define BLEND blend_mix

#include "psx_base.gdshaderinc"
