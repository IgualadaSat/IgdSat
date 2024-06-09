precision highp float;
precision highp int;

varying vec3 vNormal;

void main() {
  gl_FragColor = vec4(0.5 + 0.5 * normalize(vNormal), 1.0);
}