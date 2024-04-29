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
        const int ASSETBUNDLE_SIZE = 5;
        Debug.Log("===========");
        Debug.Log(arguments[13]);
        int meshesCount = int.Parse(arguments[13]);
        for(int i = 0; i < meshesCount; i++){
            string meshId = arguments[14+i];
            Debug.Log((meshesCount-1)/ASSETBUNDLE_SIZE);
            int assetBundleMinIdx = ((meshesCount-1)/ASSETBUNDLE_SIZE)*ASSETBUNDLE_SIZE + 1;
            string assetBundleInterval = string.Format("_{0}_{1}", assetBundleMinIdx, assetBundleMinIdx+ASSETBUNDLE_SIZE-1);
            Debug.Log(assetBundleInterval);
            createMeshPrefab(meshId, assetBundleInterval);
        }
    }

    static unsafe void createMeshPrefab(string meshId, string assetBundleInterval){
        const string ASSETS_PATH = "StonesMeshes/";
        const string PREFABS_PATH = "Assets/Resources/StonesPrefabs/";
        string meshFolderPath = ASSETS_PATH+meshId;
        string meshPath = meshFolderPath+"/"+meshId;
        string prefabPath = PREFABS_PATH+meshId+".prefab";

        Debug.Log("~~~~~~~~~");
        Debug.Log(meshFolderPath);

        // Step 1: Create an empty GameObject
        Debug.Log(meshPath);
        Debug.Log(Resources.Load(meshPath));
        GameObject newPrefab = Instantiate(Resources.Load(meshPath)) as GameObject;
        // Step 2: Convert to Prefab
        PrefabUtility.SaveAsPrefabAsset(newPrefab, prefabPath);
        // Step 3: Set its assetBundleName
        AssetImporter.GetAtPath(prefabPath).assetBundleName = "stones"+assetBundleInterval;

    }
}
#endif