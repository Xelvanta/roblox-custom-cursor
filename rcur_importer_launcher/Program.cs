using System;
using System.Diagnostics;

class Program
{
    static void Main(string[] args)
    {
        if (args.Length == 0) return;

        string systemDrive = Environment.GetEnvironmentVariable("SystemDrive") ?? "C:";
        string scriptPath = $"{systemDrive}\\Program Files\\Xelvanta Softworks\\Roblox Custom Cursor\\rcur_importer.pyw";
        string inputFile = args[0];

        var psi = new ProcessStartInfo
        {
            FileName = "pythonw",
            Arguments = $"\"{scriptPath}\" \"{inputFile}\"",
            UseShellExecute = false,
            CreateNoWindow = true
        };

        Process.Start(psi);
    }
}