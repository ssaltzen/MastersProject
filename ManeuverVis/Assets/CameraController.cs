using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraController : MonoBehaviour
{

    FileProcessor plane;

    void Awake()
    {
        plane = GameObject.Find("Super_Spitfire").GetComponent<FileProcessor>();
    }
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        transform.position = new Vector3(plane.transform.position.x + 14, plane.transform.position.y + 6, plane.transform.position.z + 1);
    }
}
