﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[RequireComponent(typeof(MeshRenderer))]
public class Checkerboard : MonoBehaviour
{
    MeshRenderer meshRenderer;
    Material material;
    Texture2D texture;
    [SerializeField] float width = 10.0f;

    // Start is called before the first frame update
    void Start()
    {
        meshRenderer = GetComponent<MeshRenderer>();
        material = meshRenderer.material;
        texture = new Texture2D(256, 256, TextureFormat.RGBA32, true, true);
        texture.wrapMode = TextureWrapMode.Clamp;
        texture.filterMode = FilterMode.Point;
        material.SetTexture("_MainTex", texture);
        CreateCheckerboard();
        Debug.Log("Done!");
    }


    void CreateCheckerboard()
    {
        for (int y = 0; y < texture.height; y++)
        {
            for (int x = 0; x < texture.width; x++)
            {
                Color temp = EvaluateCheckerboardPixel(x, y);
                texture.SetPixel(x, y, temp);
            }
        }
        texture.Apply();
    }

    Color EvaluateCheckerboardPixel(int x, int y)
    {
        float valueX = (x % (width*2.0f))/(width*2.0f);
        int vX = 1;
        if(valueX < 0.5f)
        {
            vX = 0;
        }

        float valueY = (y % (width * 2.0f)) / (width * 2.0f);
        int vY = 1;
        if (valueY < 0.5f)
        {
            vY = 0;
        }

        float value = 0;
        if(vX == vY)
        {
            value = 1;
        }

        Color color;
        if(value == 1)
        {
            color = new Color(1.0f, 1.0f, 1.0f, 1.0f);
        }
        else
        {
            color = new Color(0.5f, 0.5f, 1.0f, 1.0f);
        }
        return color;
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}