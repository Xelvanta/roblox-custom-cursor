#include <windows.h>
#include <string>

std::string GetFileExtension(const std::string& filename) {
    size_t pos = filename.find_last_of('.');
    if (pos == std::string::npos) return "";
    std::string ext = filename.substr(pos + 1);
    for (auto& c : ext) c = tolower(c);
    return ext;
}

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int)
{
    int argc = 0;
    LPWSTR* argvW = CommandLineToArgvW(GetCommandLineW(), &argc);
    if (!argvW || argc < 2) {
        MessageBoxA(NULL, "No command line argument received or argvW is null", "Debug", MB_OK | MB_ICONERROR);
        if (argvW) LocalFree(argvW);
        return 0;
    }

    // Convert input path to UTF-8 string
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, argvW[1], -1, NULL, 0, NULL, NULL);
    if (size_needed <= 0) {
        MessageBoxA(NULL, "Failed to calculate UTF-8 buffer size", "Debug", MB_OK | MB_ICONERROR);
        LocalFree(argvW);
        return 1;
    }
    std::string inputFile(size_needed, 0);
    int convResult = WideCharToMultiByte(CP_UTF8, 0, argvW[1], -1, &inputFile[0], size_needed, NULL, NULL);
    if (convResult == 0) {
        MessageBoxA(NULL, "Failed to convert wide char to UTF-8 string", "Debug", MB_OK | MB_ICONERROR);
        LocalFree(argvW);
        return 1;
    }
    LocalFree(argvW);

    MessageBoxA(NULL, ("Input file: " + inputFile).c_str(), "Debug", MB_OK);

    // Get directory of current exe
    char exePath[MAX_PATH];
    DWORD len = GetModuleFileNameA(NULL, exePath, MAX_PATH);
    if (len == 0 || len == MAX_PATH) {
        MessageBoxA(NULL, "Failed to get module file name or path too long", "Debug", MB_OK | MB_ICONERROR);
        return 1;
    }
    std::string exeDir(exePath);
    size_t lastSlash = exeDir.find_last_of("\\/");
    if (lastSlash != std::string::npos) {
        exeDir = exeDir.substr(0, lastSlash);
    }

    MessageBoxA(NULL, ("Executable directory: " + exeDir).c_str(), "Debug", MB_OK);

    // Determine the extension
    std::string ext = GetFileExtension(inputFile);
    MessageBoxA(NULL, ("File extension: " + ext).c_str(), "Debug", MB_OK);

    // Compose pythonw.exe path and command line
    std::string pythonwPath = exeDir + "\\python\\pythonw.exe";
    std::string commandLine = "\"" + pythonwPath + "\" \"" + inputFile + "\"";
    MessageBoxA(NULL, ("Command line: " + commandLine).c_str(), "Debug", MB_OK);

    STARTUPINFOA si = { sizeof(si) };
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;

    PROCESS_INFORMATION pi;

    char* cmdLineMutable = _strdup(commandLine.c_str());
    if (!cmdLineMutable) {
        MessageBoxA(NULL, "Failed to allocate memory for command line", "Debug", MB_OK | MB_ICONERROR);
        return 1;
    }

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

    if (!success) {
        DWORD err = GetLastError();
        char errMsg[256];
        wsprintfA(errMsg, "CreateProcess failed. Error code: %lu", err);
        MessageBoxA(NULL, errMsg, "Debug", MB_OK | MB_ICONERROR);
        free(cmdLineMutable);
        return 1;
    }

    free(cmdLineMutable);

    MessageBoxA(NULL, "Process created successfully!", "Debug", MB_OK);

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return 0;
}
