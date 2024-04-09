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
}
#endif