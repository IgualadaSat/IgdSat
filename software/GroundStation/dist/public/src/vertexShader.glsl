#type vertex
#extension GL_OES_standard_derivatives : enable
precision highp float;
precision highp int;

varying vec3 vNormal;

void main() {
  vNormal = normalMatrix * normal;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}