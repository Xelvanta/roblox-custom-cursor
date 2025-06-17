#include <windows.h>
#include <string>

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR lpCmdLine, int)
{
    // Parse command line arguments
    int argc = 0;
    LPWSTR* argvW = CommandLineToArgvW(GetCommandLineW(), &argc);
    if (!argvW || argc < 2) {
        if (argvW) LocalFree(argvW);
        MessageBoxW(NULL, L"No .rccapp file specified.", L"RCC3 Launcher", MB_ICONERROR);
        return 0;
    }

    // Convert input file path to UTF-8 string
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, argvW[1], -1, NULL, 0, NULL, NULL);
    std::string inputFile(size_needed, 0);
    WideCharToMultiByte(CP_UTF8, 0, argvW[1], -1, &inputFile[0], size_needed, NULL, NULL);
    LocalFree(argvW);

    // Get full path to current executable
    char exePath[MAX_PATH];
    DWORD len = GetModuleFileNameA(NULL, exePath, MAX_PATH);
    if (len == 0 || len == MAX_PATH) {
        MessageBoxA(NULL, "Failed to get executable path.", "RCC3 Launcher", MB_ICONERROR);
        return 1;
    }

    // Get directory containing this executable
    std::string exeDir(exePath);
    size_t lastSlash = exeDir.find_last_of("\\/");
    if (lastSlash != std::string::npos) {
        exeDir = exeDir.substr(0, lastSlash);
    }

    // Build path to embedded pythonw.exe
    std::string pythonwPath = exeDir + "\\python\\pythonw.exe";

    // Final command to run: pythonw.exe "<path to .rccapp>"
    std::string commandLine = "\"" + pythonwPath + "\" \"" + inputFile + "\"";

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
        exeDir.c_str(),  // Set working directory to exeDir
        &si,
        &pi
    );

    free(cmdLineMutable);

    if (success) {
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }
    else {
        MessageBoxA(NULL, "Failed to launch embedded Python.", "RCC3 Launcher", MB_ICONERROR);
    }

    return 0;
}
