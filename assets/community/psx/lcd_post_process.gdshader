shader_type canvas_item;
#pragma disable_preprocessor

// Donor: MenacingMecha/godot-psx-style-demo (MIT)
uniform bool enabled = true;
uniform float lcd_opacity = 0.5;
uniform int scanline_gap = 5;

float when_eq(int x, int y)
{
    return 1.0 - abs(sign(float(x) - float(y)));
}

vec4 lcdColor(int pos_x, int pos_y)
{
    vec4 lcdColor = vec4(1);
    lcdColor.r = lcdColor.r * when_eq(pos_x, 0);
    lcdColor.g = lcdColor.g * when_eq(pos_x, 1);
    lcdColor.b = lcdColor.b * when_eq(pos_x, 2);
    lcdColor.rgb = lcdColor.rgb * vec3(1.0 - when_eq(pos_y, 0));
    return lcdColor;
}

void fragment()
{
    vec4 tex = texture(TEXTURE,UV);
    int pos_x = int(mod(FRAGCOORD.x, 3.0));
    int pos_y = int(mod(FRAGCOORD.y, float(scanline_gap)));
    vec4 lcd_overlay_tex = lcdColor(pos_x, pos_y);
    COLOR = enabled ? mix(tex, tex * lcd_overlay_tex, lcd_opacity) : tex;
}
