import * as THREE from 'three';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';

//-------------------------------------------------------------------SCENE

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);

camera.position.z = 250;
camera.position.y = 80;

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

function updateRendererSize() {
  const width = window.innerWidth;
  const height = window.innerHeight;

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  renderer.setSize(width, height);
}

window.addEventListener('resize', updateRendererSize);

window.addEventListener('load', updateRendererSize);

//-------------------------------------------------------------------LIGHTING

const directionalLight = new THREE.DirectionalLight(0x00ffff, 1);
directionalLight.position.set(10, 10, 10);
directionalLight.intensity = 1.5;
directionalLight.shadow.camera.near = 1;
directionalLight.shadow.camera.far = 100;
directionalLight.shadow.mapSize.width = 1024;
directionalLight.shadow.mapSize.height = 1024;
scene.add(directionalLight);

const ambientLight = new THREE.AmbientLight(0x404040);
scene.add(ambientLight);

renderer.shadowMap.enabled = true;

//-------------------------------------------------------------------OBJECT

const loader = new OBJLoader();
let loadedObject;

const materialInvertedNormals = new THREE.MeshStandardMaterial({ color: 0x00ffff, side: THREE.BackSide });

loader.load(
  '../storage/fusion_cansat_Frame.obj',
  function (object) {
    object.traverse(function (child) {
      if (child instanceof THREE.Mesh) {
        //child.material = materialInvertedNormals;
        child.castShadow = true; 
        child.receiveShadow = true;
      }
    });

    loadedObject = object;
    loadedObject.rotation.x -= Math.PI*0.5;
    scene.add(loadedObject);
  },
  undefined,
  function (error) {
    console.error(error);
  }
);

//-------------------------------------------------------------------LOOP

function animate() {
  requestAnimationFrame(animate);

  if (loadedObject) {
    loadedObject.rotation.z += 0.1;
    loadedObject.rotation.y += 0.1 * Math.random() - 0.05;
    loadedObject.rotation.x += 0.1 * Math.random() - 0.05;
  }

  renderer.render(scene, camera);
}

//const directionalLightHelper = new THREE.DirectionalLightHelper(directionalLight, 5);
//scene.add(directionalLightHelper);

animate();