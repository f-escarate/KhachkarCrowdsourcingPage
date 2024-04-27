#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using Unity.Burst;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using Unity.Collections;
using Unity.Collections.LowLevel.Unsafe;
using Unity.Jobs;
using UnityEditor;

[BurstCompile]
public class CallableMethods: MonoBehaviour
{
    static unsafe void GenerateAsset(){
        string[] arguments = Environment.GetCommandLineArgs();
        for(int i = 0; i < arguments.Length; i++){
            Debug.Log(arguments[i]);
        }
    }
    
    static unsafe void createPrefabs(){
        string[] arguments = Environment.GetCommandLineArgs();
        Debug.Log("===========");
        Debug.Log(arguments[13]);
        int meshes_count = int.Parse(arguments[13]);
        for(int i = 0; i < meshes_count; i++){
            string mesh_id = arguments[14+i];
            createPrefab(mesh_id);
        }
    }

    static unsafe void createPrefab(string mesh_id){
        const string ASSETS_PATH = "StonesMeshes/";
        const string PREFABS_PATH = "Assets/Resources/StonesPrefabs/";
        string mesh_folder_path = ASSETS_PATH+mesh_id;
        string mesh_path = mesh_folder_path+"/"+mesh_id;
        string prefab_path = PREFABS_PATH+mesh_id+".prefab";

        Debug.Log("~~~~~~~~~");
        Debug.Log(mesh_folder_path);

        // Step 1: Create an empty GameObject
        Debug.Log(mesh_path);
        Debug.Log(Resources.Load(mesh_path));
        GameObject newPrefab = Instantiate(Resources.Load(mesh_path)) as GameObject;
        // Step 4: Convert to Prefab
        PrefabUtility.SaveAsPrefabAsset(newPrefab, prefab_path);

    }
}
#endif