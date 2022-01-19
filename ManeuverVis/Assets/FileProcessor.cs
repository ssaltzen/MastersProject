using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FileProcessor : MonoBehaviour
{
    public TextAsset ManeuverDataFile;
    public List<double>[] orientation;
    public int index = 1;
    float indexFloat = 1;
    public double time = 1;
    public bool airForceFile = false;
    public int indexSkipOnArrowKey = 1;
    public int maxIndex;
    public int speedUpMultiplier = 2;
    public float slowDownMultiplier = 0.25f;
    public List<double> values = new List<double>();
    GameObject checkerboard;
    bool slowDown = false;

    // Start is called before the first frame update
    void Awake()
    {
        string ManeuverData = ManeuverDataFile.text;
        string[] ManeuverDataLines = ManeuverData.Split('\n');
        maxIndex = ManeuverDataLines.Length - 1;
        orientation = new List<double>[maxIndex];
        double max = 0;
        if (airForceFile)
        {
            for (int i = 2; i < maxIndex; i++)
            {
                List<double> indexOrientation = new List<double>();
                string[] dataCells = ManeuverDataLines[i].Split('\t');
                indexOrientation.Add(Double.Parse(dataCells[1]));
                indexOrientation.Add(Double.Parse(dataCells[2]));
                indexOrientation.Add(Double.Parse(dataCells[3]));
                indexOrientation.Add(Double.Parse(dataCells[4]));
                indexOrientation.Add(Double.Parse(dataCells[8]));
                indexOrientation.Add(Double.Parse(dataCells[9]));
                indexOrientation.Add(Double.Parse(dataCells[10]));
                orientation[i] = indexOrientation;
            }
            checkerboard = GameObject.Find("Plane");
            for (int i = 2; i < maxIndex; i++)
            {
                if (orientation[i][1] > max)
                {
                    max = orientation[i][1];
                }
                if (orientation[i][3] > max)
                {
                    max = orientation[i][3];
                }
            }
        }
        else
        {
            for (int i = 1; i < maxIndex; i++)
            {
                List<double> indexOrientation = new List<double>();
                string[] dataCells = ManeuverDataLines[i].Split('\t');
                indexOrientation.Add(Double.Parse(dataCells[1]));
                indexOrientation.Add(Double.Parse(dataCells[2]));
                indexOrientation.Add(Double.Parse(dataCells[3]));
                indexOrientation.Add(Double.Parse(dataCells[4]));
                indexOrientation.Add(Double.Parse(dataCells[8]));
                indexOrientation.Add(Double.Parse(dataCells[9]));
                indexOrientation.Add(Double.Parse(dataCells[10]));
                orientation[i] = indexOrientation;
            }
            checkerboard = GameObject.Find("Plane");
            for (int i = 1; i < maxIndex; i++)
            {
                if (orientation[i][1] > max)
                {
                    max = orientation[i][1];
                }
                if (orientation[i][3] > max)
                {
                    max = orientation[i][3];
                }
            }
        }

        //the z axis in unity is the same as y axis in the data
        checkerboard.transform.localScale =  new Vector3(((float)max), 1, ((float)max));

        
        
    }

    // Update is called once per frame
    void Update()
    {
        if (!slowDown)
        {
            indexFloat = index;
        }
        if (Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift))
        {
            slowDown = false;
            if ((Input.GetKey(KeyCode.RightArrow)))
            {
                index += indexSkipOnArrowKey * speedUpMultiplier;
            }
            else if ((Input.GetKey(KeyCode.LeftArrow)))
            {
                index -= indexSkipOnArrowKey * speedUpMultiplier;
            }
        }
        else if (Input.GetKey(KeyCode.Space))
        {
            slowDown = true;
            if ((Input.GetKey(KeyCode.RightArrow)))
            {
                indexFloat += indexSkipOnArrowKey * slowDownMultiplier;
            }
            else if ((Input.GetKey(KeyCode.LeftArrow)))
            {
                indexFloat -= indexSkipOnArrowKey * slowDownMultiplier;
            }
            index = (int)Math.Floor(indexFloat);

        }
        else if ((Input.GetKey(KeyCode.RightArrow)))
        {
            slowDown = false;
            index += indexSkipOnArrowKey;
        }
        else if ((Input.GetKey(KeyCode.LeftArrow)))
        {
            slowDown = false;
            index -= indexSkipOnArrowKey;
        }

        if(index >= maxIndex)
        {
            index = maxIndex - 1;
        }

        if(index < 1)
        {
            index = 1;
        }


        values = orientation[index];
        //Debug.Log(values);
        time = values[0];
        Quaternion rotation = new Quaternion();
        Vector3 position;
        if (airForceFile)
        {
            rotation = Quaternion.Euler((float)values[6], (float)values[5], (float)values[4]);
            position = new Vector3((float)values[1], (float)values[3], (float)values[2]);
        }
        else
        {
            rotation = Quaternion.Euler((float)values[5], (float)values[4], (float)values[6]);
            position = new Vector3((float)values[1], (float)values[3], (float)values[2]);
        }
        transform.SetPositionAndRotation(position, rotation);
        Camera.main.transform.position = new Vector3(transform.position.x + 20, transform.position.y + 14, transform.position.z);

    }
}
