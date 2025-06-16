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

    // Get executable full path
    char exePath[MAX_PATH];
    DWORD len = GetModuleFileNameA(NULL, exePath, MAX_PATH);
    if (len == 0 || len == MAX_PATH) {
        // Failed to get executable path, fallback or exit
        return 1;
    }

    // Strip executable filename to get directory
    std::string exeDir(exePath);
    size_t lastSlash = exeDir.find_last_of("\\/");
    if (lastSlash != std::string::npos) {
        exeDir = exeDir.substr(0, lastSlash);
    }

    // Build path to rcur_importer.pyw relative to exe dir
    std::string scriptPath = exeDir + "\\rcur_importer.pyw";

    // Build command line to run pythonw with script and input file
    std::string commandLine = "pythonw \"" + scriptPath + "\" \"" + inputFile + "\"";

    STARTUPINFOA si = { sizeof(si) };
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;

    PROCESS_INFORMATION pi;

    // CreateProcess requires mutable string
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
