#if UNITY_EDITOR
using System;
using System.Linq;
using System.Reflection;
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
        int meshesCount = int.Parse(arguments[13]);
        for(int i = 0; i < meshesCount; i++){
            string meshId = arguments[14+i];
            int assetBundleMinIdx = ((meshesCount-1)/ASSETBUNDLE_SIZE)*ASSETBUNDLE_SIZE + 1;
            string assetBundleInterval = string.Format("_{0}_{1}", assetBundleMinIdx, assetBundleMinIdx+ASSETBUNDLE_SIZE-1);
            createMeshPrefab(meshId, assetBundleInterval);
            createTextAsset(meshId, assetBundleInterval);
            addThumbToAssetBundle(meshId);
        }

        string path = "/var/www/museum/StreamingAssets";
        //string path = "Assets/AssetBundles";

        // Remove previous files
        System.IO.DirectoryInfo di = new DirectoryInfo(path);
        foreach (FileInfo file in di.GetFiles())
        {
            file.Delete(); 
        }
        // Build Asset Bundles
        BuildPipeline.BuildAssetBundles(path, BuildAssetBundleOptions.None, BuildTarget.WebGL);
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
        // Step 2.1: Set Box Collider properties
        SerializedObject boxCollider = new SerializedObject(newPrefab.GetComponent<BoxCollider>());
        boxCollider.FindProperty("m_Size").vector3Value = new Vector3(1.5f, 4.0f, 1.5f);
        boxCollider.FindProperty("m_Center").vector3Value = new Vector3(0.0f, 2.0f, 0.0f);
        boxCollider.ApplyModifiedProperties();
        // Step 3: Add Halo
        var types = Assembly.Load("UnityEngine.CoreModule, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null").GetTypes();
        Type haloType = types.First(t => t.Name.Equals("Halo"));
        newPrefab.AddComponent(haloType);
        // Step 3.1: Set Halo properties
        SerializedObject halo = new SerializedObject(newPrefab.GetComponent(haloType));
        halo.FindProperty("m_Size").floatValue = 4.53f;
        halo.FindProperty("m_Enabled").boolValue = false;
        halo.FindProperty("m_Color").colorValue = new Color(0.6784f, 0.34117f, 0.12549f, 1.0f);
        halo.ApplyModifiedProperties();
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
    static unsafe void addThumbToAssetBundle(string meshId){
        const string PREFABS_PATH = "Assets/Resources/StonesThumbs/";
        string prefabPath = PREFABS_PATH+meshId+".jpg";
        AssetImporter.GetAtPath(prefabPath).assetBundleName = "stones_thumbs";
    }
}
#endif