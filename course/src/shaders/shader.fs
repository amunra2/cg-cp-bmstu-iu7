#version 330 core

uniform vec4 curColor;
out vec4 FragColor;

void main()
{
    FragColor = curColor;
}