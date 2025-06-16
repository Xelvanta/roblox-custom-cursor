#include <windows.h>
#include <string>

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR lpCmdLine, int)
{
    // Parse command line arguments
    int argc = 0;
    LPWSTR* argvW = CommandLineToArgvW(GetCommandLineW(), &argc);
    if (!argvW || argc < 2) {
        if (argvW) LocalFree(argvW);
        return 0;
    }

    // Convert argvW[1] (input file) to std::string (assuming ASCII or UTF-8 safe)
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, argvW[1], -1, NULL, 0, NULL, NULL);
    std::string inputFile(size_needed, 0);
    WideCharToMultiByte(CP_UTF8, 0, argvW[1], -1, &inputFile[0], size_needed, NULL, NULL);
    LocalFree(argvW);

    // Get SystemDrive
    char sysDrive[MAX_PATH];
    DWORD ret = GetEnvironmentVariableA("SystemDrive", sysDrive, MAX_PATH);
    std::string systemDrive = (ret > 0) ? std::string(sysDrive) : "C:";

    std::string scriptPath = systemDrive + "\\Program Files\\Xelvanta Softworks\\Roblox Custom Cursor\\rcur_importer.pyw";

    std::string commandLine = "pythonw \"" + scriptPath + "\" \"" + inputFile + "\"";

    STARTUPINFOA si = { sizeof(si) };
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;

    PROCESS_INFORMATION pi;

    char* cmdLineMutable = _strdup(commandLine.c_str());

    BOOL success = CreateProcessA(
        NULL,
        cmdLineMutable,
        NULL,
        NULL,
        FALSE,
        CREATE_NO_WINDOW,
        NULL,
        NULL,
        &si,
        &pi
    );

    free(cmdLineMutable);

    if (success) {
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }

    return 0;
}