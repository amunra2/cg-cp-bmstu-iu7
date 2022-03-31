#version 330 core

in vec4 FrontColor;
out vec4 FragColor;

void main()
{
    FragColor = FrontColor;
}



// #version 330 core

// // in vec2 UV;
// in vec4 particleColor
// // uniform vec4 curColor;
// out vec4 color;

// void main()
// {
//     color = particleColor;
// }


// #version 330 core

// // Interpolated values from the vertex shaders
// in vec2 UV;
// in vec4 particlecolor;

// // Ouput data
// out vec4 color;

// uniform sampler2D myTextureSampler;

// void main(){
// 	// Output color = color of the texture at the specified UV
// 	color = texture( myTextureSampler, UV ) * particlecolor;

// }