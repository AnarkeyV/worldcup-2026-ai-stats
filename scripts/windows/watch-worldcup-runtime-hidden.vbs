Option Explicit

Dim shell, fso, windowsDir, scriptsDir, projectDir, psScript, command, exitCode

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

windowsDir = fso.GetParentFolderName(WScript.ScriptFullName)
scriptsDir = fso.GetParentFolderName(windowsDir)
projectDir = fso.GetParentFolderName(scriptsDir)

psScript = fso.BuildPath(windowsDir, "watch-worldcup-runtime.ps1")

shell.CurrentDirectory = projectDir

command = "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File " & Chr(34) & psScript & Chr(34)

exitCode = shell.Run(command, 0, True)

WScript.Quit exitCode
