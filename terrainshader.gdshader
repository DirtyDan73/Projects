shader_type canvas_item;

uniform sampler2D color;
uniform sampler2D height;
uniform vec3 sunPos = vec3(1,1,1);
uniform float stepLength = .1;

uniform vec2 aPosition;
uniform vec2 aTexCoord;
varying vec2 pos;

const float shadowBrightness = 0.2;
const float STEPS = 4000.;

uniform vec3 stepDir;

float rand(){
	vec2 co = vec2(TIME,TIME*2.);
	return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void vertex() {
	pos = aTexCoord;
	UV.y = 1. - UV.y;
	
	vec2 positionVec4 = vec2(aPosition);
	positionVec4.xy = positionVec4.xy * 2.0 - 1.0;
}

void shadows(){
	
}

void fragment() {
	float hgt = texture(height, UV).r;
	vec3 p = vec3(UV, hgt);
	float inShadow = 0.;  
	for(float i = 0.; i < STEPS; i ++) {
    // Step towards the sun
		p += stepDir; //+ (rand()*.01);
		// Check height at new location
		float h = texture(height, p.xy).r;
		if(h > p.z) {
		// ray is inside the terrain therefore must be in shadow
			inShadow = 1./ (i+1.*(stepLength+1.));
	    	break;
	    }
		if(p.z > 1.) {
			break;
		}
	}
	vec4 col = texture(color, UV);
	// create a darker version of the colour for the shadows
	vec4 shadowCol = vec4(col.rgb * shadowBrightness, col.a);
	if(sunPos.z <= 0.){
		COLOR.rgb = mix(COLOR.rgb, vec3(1. - shadowBrightness), .01);
	}else{
		COLOR.rgb *= (1. - shadowBrightness*(inShadow));
	}
}

void light() {
	// Called for every pixel for every light affecting the CanvasItem.
}
