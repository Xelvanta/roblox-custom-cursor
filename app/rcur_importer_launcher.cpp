#include <windows.h>
#include <string>

// Utility to get file extension in lowercase
std::string GetFileExtension(const std::string& filename) {
    size_t pos = filename.find_last_of('.');
    if (pos == std::string::npos) return "";
    std::string ext = filename.substr(pos + 1);
    for (auto& c : ext) c = tolower(c);
    return ext;
}

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR lpCmdLine, int)
{
    int argc = 0;
    LPWSTR* argvW = CommandLineToArgvW(GetCommandLineW(), &argc);
    if (!argvW || argc < 2) {
        if (argvW) LocalFree(argvW);
        return 0;
    }

    // Convert input path to UTF-8 string
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, argvW[1], -1, NULL, 0, NULL, NULL);
    std::string inputFile(size_needed, 0);
    WideCharToMultiByte(CP_UTF8, 0, argvW[1], -1, &inputFile[0], size_needed, NULL, NULL);
    LocalFree(argvW);

    // Get directory of current exe
    char exePath[MAX_PATH];
    DWORD len = GetModuleFileNameA(NULL, exePath, MAX_PATH);
    if (len == 0 || len == MAX_PATH) {
        return 1;
    }
    std::string exeDir(exePath);
    size_t lastSlash = exeDir.find_last_of("\\/");
    if (lastSlash != std::string::npos) {
        exeDir = exeDir.substr(0, lastSlash);
    }

    // Determine the extension and handle accordingly
    std::string ext = GetFileExtension(inputFile);

    // (Optional) You can add different behavior per extension here
    // For now both just run pythonw with the file as argument
    std::string pythonwPath = exeDir + "\\python\\pythonw.exe";
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
        exeDir.c_str(),
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