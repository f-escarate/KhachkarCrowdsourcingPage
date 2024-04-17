import * as THREE from "three";
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js';
import { DDSLoader } from 'three/examples/jsm/loaders/DDSLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { HOST } from './constants.js';
const FPS = 30;

let scene;
let camera;
let renderer;
let percentComplete;

export function init(width, height, element, id) {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, width/height, 0.1, 2000);
    transform_camera(10, 10, 1);
    renderer = new THREE.WebGLRenderer();
    // Basic lighting
    const ambientLight = new THREE.AmbientLight(0xFFFFFF, 1.0);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 10.0);
    directionalLight.position.set(0, 0, 5);
    scene.add(directionalLight);
    scene.background = new THREE.Color(0xEEEEEE);
    renderer.setSize(width, height);
    element.appendChild(renderer.domElement);

    // Axes
    const axesHelper = new THREE.AxesHelper(20);
    scene.add( axesHelper );
    
    // model
    var onProgress = function ( xhr ) {
        if ( xhr.lengthComputable ) {
            percentComplete = xhr.loaded / xhr.total * 100;
            console.log( Math.round( percentComplete, 2 ) + '% downloaded' );
        }
    };
    var onError = function () { };
    
    var manager = new THREE.LoadingManager();
    manager.addHandler( /\.dds$/i, new DDSLoader() );
    new MTLLoader()
        .setPath(`${HOST}/get_mtl/${id}/`)
        .load('', function (materials) {
            materials.preload();
            new OBJLoader()
                .setMaterials(materials)
                .setPath(`${HOST}/get_obj/`)
                .load(`${id}`, function (object) {
                    scene.add(object);
                }, onProgress, onError);
    });    
}

const render = () => {
    renderer.clear()
    renderer.render(scene, camera);
}

export const animate = () => {
    setTimeout(function() {
        requestAnimationFrame(animate);
    }, 1000 / FPS );
    render()
}
const deg_to_rad = (deg) => {
    return deg * Math.PI / 180;
}
export function transform_stone(transformations) {
    let {pos, rot, scale} = transformations;
    try {
        let stone = scene.getObjectByProperty('type', 'Group');
        stone.rotation.x = deg_to_rad(rot.x);
        stone.rotation.y = deg_to_rad(rot.y);
        stone.rotation.z = deg_to_rad(rot.z);
        stone.position.x = pos.x;
        stone.position.y = pos.y;
        stone.position.z = pos.z;
        stone.scale.x = scale.value;
        stone.scale.y = scale.value;
        stone.scale.z = scale.value;
    }
    catch (e) {
        alert("Stone isn't loaded yet");
    }
}
export function transform_camera(angle, zoom, height) {
    camera.position.x = Math.sin(deg_to_rad(angle)) * zoom;
    camera.position.z = Math.cos(deg_to_rad(angle)) * zoom;
    camera.position.y = height;
    camera.lookAt(0, 0, 0);
}