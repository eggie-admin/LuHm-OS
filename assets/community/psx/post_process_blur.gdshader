shader_type canvas_item;
#pragma disable_preprocessor

// Donor: MenacingMecha/godot-psx-style-demo (MIT)
uniform vec2 blur_scale = vec2(0.5, 0.5);
uniform float blur_samples = 50.0;
uniform float blur_brightness = 1.65;
uniform bool enabled = true;

const float PI2 = 6.283185307179586476925286766559;

float gaussian(float x)
{
    float x_squared = x*x;
    float width = 1.0 / sqrt(PI2 * blur_samples);
    return width * exp((x_squared / (2.0 * blur_samples)) * -1.0);
}

vec4 gaussian_blur_pass(vec2 texture_pixel_size, sampler2D texture_source, vec2 uv, float sample_count)
{
    float weight = 0.0;
    float total_weight = 0.0;
    vec2 scale_horiz = texture_pixel_size * vec2(blur_scale.x, 0.0);
    vec4 color_horiz = vec4(0.0);

    for(int i=-int(sample_count)/2; i < int(sample_count)/2; ++i) {
        weight = gaussian(float(i));
        color_horiz += texture(texture_source, uv + scale_horiz * vec2(float(i))) * weight;
        total_weight += weight;
    }

    weight = 0.0;
    total_weight = 0.0;
    vec2 scale_vert = texture_pixel_size * vec2(0.0, blur_scale.y);
    vec4 color_vert = vec4(0.0);

    for(int i=-int(sample_count)/2; i < int(sample_count)/2; ++i) {
        weight = gaussian(float(i));
        color_vert += texture(texture_source, uv + scale_vert * vec2(float(i))) * weight;
        total_weight += weight;
    }

    vec4 blur = mix(color_horiz, color_vert, 0.5);
    return blur;
}

void fragment()
{
    COLOR = enabled ? gaussian_blur_pass(TEXTURE_PIXEL_SIZE, TEXTURE, UV, blur_samples) * blur_brightness : texture(TEXTURE, UV);
}
