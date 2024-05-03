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
    static unsafe void generateAssetBundles(){
        string[] arguments = Environment.GetCommandLineArgs();
        const int ASSETBUNDLE_SIZE = 5;
        Debug.Log("===========");
        Debug.Log(arguments[13]);
        int meshesCount = int.Parse(arguments[13]);
        for(int i = 0; i < meshesCount; i++){
            string meshId = arguments[14+i];
            int assetBundleMinIdx = ((meshesCount-1)/ASSETBUNDLE_SIZE)*ASSETBUNDLE_SIZE + 1;
            string assetBundleInterval = string.Format("_{0}_{1}", assetBundleMinIdx, assetBundleMinIdx+ASSETBUNDLE_SIZE-1);
            createMeshPrefab(meshId, assetBundleInterval);
            createTextAsset(meshId, assetBundleInterval);
        }
        // Build Asset Bundles
        BuildPipeline.BuildAssetBundles("Assets/AssetBundles", BuildAssetBundleOptions.None, BuildTarget.WebGL);
    }

    static unsafe void createMeshPrefab(string meshId, string assetBundleInterval){
        const string ASSETS_PATH = "StonesMeshes/";
        const string PREFABS_PATH = "Assets/Resources/StonesPrefabs/";
        string meshFolderPath = ASSETS_PATH+meshId;
        string meshPath = meshFolderPath+"/"+meshId;
        string prefabPath = PREFABS_PATH+"Stone"+meshId+".prefab";

        // Step 1: Create an empty GameObject
        GameObject newPrefab = Instantiate(Resources.Load(meshPath)) as GameObject;
        // Step 2: Add Box Collider
        newPrefab.AddComponent<BoxCollider>();
        // Step 3: Add Halo
        // Step 4: Add Conture Rendering
        newPrefab.AddComponent<ContureRendering>();
        // Step 5: Convert to Prefab
        PrefabUtility.SaveAsPrefabAsset(newPrefab, prefabPath);
        // Step 6: Set its assetBundleName
        AssetImporter.GetAtPath(prefabPath).assetBundleName = "stones"+assetBundleInterval;
    }

    static unsafe void createTextAsset(string meshId, string assetBundleInterval){
        const string PREFABS_PATH = "Assets/Resources/StonesMetadata/";
        string prefabPath = PREFABS_PATH+"Stone"+meshId+".json";
        AssetImporter.GetAtPath(prefabPath).assetBundleName = "stones_metadata"+assetBundleInterval;
    }
}
#endif