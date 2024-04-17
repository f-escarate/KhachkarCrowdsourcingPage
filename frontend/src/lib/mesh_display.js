import * as THREE from "three";
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js';
import { DDSLoader } from 'three/examples/jsm/loaders/DDSLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { HOST } from './constants.js';

let scene;
let camera;
let renderer;

export function init(window, element, id) {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
    camera.position.z = 20;
    renderer = new THREE.WebGLRenderer();
    // Basic lighting
    const ambientLight = new THREE.AmbientLight(0xFFFFFF, 1.0);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 10.0);
    directionalLight.position.set(0, 0, 5);
    scene.add(directionalLight);
    scene.background = new THREE.Color(0xEEEEEE);
    renderer.setSize(window.innerWidth, window.innerHeight);
    element.appendChild(renderer.domElement);
    
    // model
    var onProgress = function ( xhr ) {
        if ( xhr.lengthComputable ) {
            var percentComplete = xhr.loaded / xhr.total * 100;
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
    requestAnimationFrame(animate);
    render()
}