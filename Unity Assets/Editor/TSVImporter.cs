using System.IO;
using UnityEditor;

using UnityEngine;

[UnityEditor.Experimental.AssetImporters.ScriptedImporterAttribute(1, "tsv")]
public class TSVImporter : UnityEditor.Experimental.AssetImporters.ScriptedImporter
{
    public override void OnImportAsset(UnityEditor.Experimental.AssetImporters.AssetImportContext ctx)
    {
        TextAsset textAsset = new TextAsset(File.ReadAllText(ctx.assetPath));
        ctx.AddObjectToAsset(Path.GetFileNameWithoutExtension(ctx.assetPath), textAsset);
        ctx.SetMainObject(textAsset);
        AssetDatabase.SaveAssets();
    }
}