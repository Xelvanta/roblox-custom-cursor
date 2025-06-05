#include <windows.h>
#include <string>

int main(int argc, char* argv[])
{
    if (argc < 2)
        return 0;

    char sysDrive[MAX_PATH];
    DWORD ret = GetEnvironmentVariableA("SystemDrive", sysDrive, MAX_PATH);
    std::string systemDrive = (ret > 0) ? std::string(sysDrive) : "C:";

    std::string scriptPath = systemDrive + "\\Program Files\\Xelvanta Softworks\\Roblox Custom Cursor\\rcur_importer.pyw";
    std::string inputFile = argv[1];

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

    // Close handles if process started
    if (success) {
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }

    // Fail silently (do nothing if it didn't start)
    return 0;
}