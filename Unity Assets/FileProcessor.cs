using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class FileProcessor : MonoBehaviour
{
    public TextAsset ManeuverDataFile;
    public List<double>[] orientation;
    public int index = 1;
    public int cluster = 0;
    float indexFloat = 1;
    public double time = 1;
    public bool airForceFile = false;
    public int indexSkipOnArrowKey = 1;
    public int maxIndex;
    public int speedUpMultiplier = 2;
    public float slowDownMultiplier = 0.25f;
    public bool tsv = true;
    public bool clustered_file = false;
    public List<double> values = new List<double>();
    GameObject checkerboard;
    Text indexText;
    Text fileText;
    bool slowDown = false;

    // Start is called before the first frame update
    void Awake()
    {
        String starting_file_name = ManeuverDataFile.name;
        Debug.Log(starting_file_name);
        indexText = GameObject.Find("IndexText").GetComponent<Text>();
        fileText = GameObject.Find("FileText").GetComponent<Text>();
        InputField input = GameObject.Find("FileInput").GetComponent<InputField>();
        InputField idx = GameObject.Find("ChangeIndex").GetComponent<InputField>();
        input.interactable = true;
        idx.interactable = true;
        input.onEndEdit.AddListener(SubmitFile);
        idx.onEndEdit.AddListener(ChangeIndex);
        LoadFile();
        fileText.GetComponent<UnityEngine.UI.Text>().text = "Current File: " + starting_file_name;

        
        
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKey("escape"))
        {
            Application.Quit();
        }

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

        indexText.GetComponent<UnityEngine.UI.Text>().text = "Index: " + index.ToString();

        values = orientation[index];

        //Debug.Log(values);
        time = values[0];
        Quaternion rotation = new Quaternion();
        Vector3 position;
        if (airForceFile)
        {
            rotation = Quaternion.Euler(-1*(float)values[6], (float)values[5], (float)values[4]);
            position = new Vector3((float)values[1], (float)values[3], (float)values[2]);
        }
        else
        {
            rotation = Quaternion.Euler(-1*(float)values[5], (float)values[4], -1*(float)values[6]);
            position = new Vector3((float)values[1], (float)values[3], (float)values[2]);
        }
        transform.SetPositionAndRotation(position, rotation);
        Camera.main.transform.position = new Vector3(transform.position.x + 20, transform.position.y + 14, transform.position.z);

        if (clustered_file)
        {
            cluster = (int)values[7];
        }

    }

    void LoadFile()
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
                string[] dataCells;
                List<double> indexOrientation = new List<double>();
                if (tsv)
                {
                    dataCells = ManeuverDataLines[i].Split('\t');
                }
                else
                {
                    dataCells = ManeuverDataLines[i].Split(',');
                }
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
                string[] dataCells;
                List<double> indexOrientation = new List<double>();
                if (tsv)
                {
                    dataCells = ManeuverDataLines[i].Split('\t');
                }
                else
                {
                    dataCells = ManeuverDataLines[i].Split(',');
                }
                indexOrientation.Add(Double.Parse(dataCells[1]));
                indexOrientation.Add(Double.Parse(dataCells[2]));
                indexOrientation.Add(Double.Parse(dataCells[3]));
                indexOrientation.Add(Double.Parse(dataCells[4]));
                indexOrientation.Add(Double.Parse(dataCells[8]));
                indexOrientation.Add(Double.Parse(dataCells[9]));
                indexOrientation.Add(Double.Parse(dataCells[10]));
                if (clustered_file)
                {
                    indexOrientation.Add(Double.Parse(dataCells[11]));
                }
                orientation[i] = indexOrientation;
            }
            checkerboard = GameObject.Find("Plane");
            for (int i = 1; i < maxIndex; i++)
            {
                if (Math.Abs(orientation[i][2]) > max)
                {
                    max = Math.Abs(orientation[i][2]);
                }
                if (Math.Abs(orientation[i][4]) > max)
                {
                    max = Math.Abs(orientation[i][4]);
                }
            }
        }
        //Debug.Log(orientation[150][4]);
        //the z axis in unity is the same as y axis in the data
        checkerboard.transform.localScale = new Vector3(((float)max), 1, ((float)max));
    }

    void SubmitFile(String fileName)
    {
        if (!String.Equals(fileName, ""))
        {
            String previousFileText = fileText.text;
            int previousIndex = index;
            fileName = fileName.Replace(".min.tsv", "");
            fileName = fileName.Replace(".min.csv", ".min");
            fileName = fileName.Replace(".csv", "");
            fileName = fileName.Replace("\n", "");
            fileName = fileName.Replace("\r", "");
            TextAsset fileToLoad = Resources.Load<TextAsset>("maneuvers/" + fileName);
            if (fileToLoad != null)
            {
                ManeuverDataFile = fileToLoad;
                fileText.text = "Current File: " + fileName;
                index = 1;
                LoadFile();
            }
        }
    }

    void ChangeIndex(String num)
    {
        if (!String.Equals(num, ""))
        {
            int idx = int.Parse(num);
            index = idx;
        }
    }
    
}
