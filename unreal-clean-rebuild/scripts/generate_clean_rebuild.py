#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path


def detect_project_file(project_root: Path) -> Path:
    uprojects = sorted(project_root.glob("*.uproject"))
    if not uprojects:
        raise FileNotFoundError(f"No .uproject found in {project_root}")
    return uprojects[0]


def detect_editor_target(project_root: Path, project_name: str) -> str:
    source_dir = project_root / "Source"
    if source_dir.exists():
        targets = sorted(source_dir.rglob("*Editor.Target.cs"))
        if targets:
            first = targets[0].name
            return first.replace(".Target.cs", "")
    return f"{project_name}Editor"


def build_batch(project_filename: str, project_name: str, editor_target: str) -> str:
    return f"""@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 > nul

echo ========================================
echo Unreal Engine Clean Rebuild Script
echo Project: {project_name}
echo ========================================
echo.

cd /d "%~dp0"

set "PROJECT_FILE={project_filename}"
set "PROJECT_NAME={project_name}"
set "EDITOR_TARGET={editor_target}"
set "PROJECT_PATH=%~dp0%PROJECT_FILE%"
set "PROJECT_PATH=%PROJECT_PATH:\\\\=\\%"

if not exist "%PROJECT_PATH%" (
    echo [ERROR] Project file not found: %PROJECT_PATH%
    goto :end
)

echo [1/6] Cleaning folders...
if exist "Intermediate" rd /s /q "Intermediate"
if exist "Binaries" rd /s /q "Binaries"
if exist ".vs" rd /s /q ".vs"
if exist "Saved\\Intermediate" rd /s /q "Saved\\Intermediate"
echo    - Clean complete
echo.

echo [2/6] Detecting UnrealBuildTool...
set "UBT="

if not "%UE_UBT_PATH%"=="" if exist "%UE_UBT_PATH%" set "UBT=%UE_UBT_PATH%"

if "%UBT%"=="" if not "%UE_ENGINE_ROOT%"=="" (
    if exist "%UE_ENGINE_ROOT%\\Engine\\Binaries\\DotNET\\UnrealBuildTool\\UnrealBuildTool.exe" (
        set "UBT=%UE_ENGINE_ROOT%\\Engine\\Binaries\\DotNET\\UnrealBuildTool\\UnrealBuildTool.exe"
    ) else if exist "%UE_ENGINE_ROOT%\\Engine\\Binaries\\DotNET\\UnrealBuildTool.exe" (
        set "UBT=%UE_ENGINE_ROOT%\\Engine\\Binaries\\DotNET\\UnrealBuildTool.exe"
    )
)

if "%UBT%"=="" (
    set "ENGINE_ASSOC="
    for /f "delims=" %%A in ('powershell -NoProfile -Command "(Get-Content -Raw '%PROJECT_PATH%' ^| ConvertFrom-Json).EngineAssociation"') do set "ENGINE_ASSOC=%%A"
    if not "!ENGINE_ASSOC!"=="" (
        if exist "C:\\Program Files\\Epic Games\\!ENGINE_ASSOC!\\Engine\\Binaries\\DotNET\\UnrealBuildTool\\UnrealBuildTool.exe" (
            set "UBT=C:\\Program Files\\Epic Games\\!ENGINE_ASSOC!\\Engine\\Binaries\\DotNET\\UnrealBuildTool\\UnrealBuildTool.exe"
        ) else if exist "D:\\Program Files\\Epic Games\\!ENGINE_ASSOC!\\Engine\\Binaries\\DotNET\\UnrealBuildTool\\UnrealBuildTool.exe" (
            set "UBT=D:\\Program Files\\Epic Games\\!ENGINE_ASSOC!\\Engine\\Binaries\\DotNET\\UnrealBuildTool\\UnrealBuildTool.exe"
        )
    )
)

if "%UBT%"=="" (
    for /f "tokens=1,*" %%A in ('reg query "HKCU\\Software\\Epic Games\\Unreal Engine\\Builds" 2^>nul ^| findstr /R "REG_SZ"') do (
        set "REG_VALUE=%%A"
        set "REG_PATH=%%B"
        if exist "%%B\\Engine\\Binaries\\DotNET\\UnrealBuildTool\\UnrealBuildTool.exe" (
            set "UBT=%%B\\Engine\\Binaries\\DotNET\\UnrealBuildTool\\UnrealBuildTool.exe"
        ) else if exist "%%B\\Engine\\Binaries\\DotNET\\UnrealBuildTool.exe" (
            set "UBT=%%B\\Engine\\Binaries\\DotNET\\UnrealBuildTool.exe"
        )
    )
)

if "%UBT%"=="" (
    for /f "delims=" %%P in ('where UnrealBuildTool.exe 2^>nul') do (
        if "%UBT%"=="" set "UBT=%%P"
    )
)

if "%UBT%"=="" (
    echo [ERROR] UnrealBuildTool.exe not found.
    echo        Set UE_ENGINE_ROOT or UE_UBT_PATH and retry.
    goto :end
)

echo    - UBT: %UBT%
echo.

echo [3/6] Generating project files...
"%UBT%" -projectfiles -project="%PROJECT_PATH%" -game -engine -progress
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to generate project files.
    goto :end
)
echo    - Project files generated
echo.

echo [4/6] Building Editor target...
echo    - Target: %EDITOR_TARGET% Win64 Development
"%UBT%" %EDITOR_TARGET% Win64 Development -Project="%PROJECT_PATH%" -WaitMutex -NoHotReloadFromIDE
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed.
    goto :end
)
echo.

echo [5/6] Build completed successfully.
echo [6/6] Done.
echo ========================================
echo BUILD SUCCEEDED
echo ========================================

:end
echo.
pause
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CleanRebuild.bat for Unreal C++ projects")
    parser.add_argument("--project-root", default=".", help="Path containing .uproject")
    parser.add_argument("--output", default="CleanRebuild.bat", help="Output batch filename")
    parser.add_argument("--target", default="", help="Override editor target name (e.g., MyGameEditor)")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    project_file = detect_project_file(project_root)
    project_name = project_file.stem
    editor_target = args.target.strip() or detect_editor_target(project_root, project_name)

    output_path = project_root / args.output
    output_path.write_text(
        build_batch(project_file.name, project_name, editor_target),
        encoding="utf-8",
        newline="\r\n",
    )

    print(f"[OK] Generated: {output_path}")
    print(f"[OK] Project: {project_file.name}")
    print(f"[OK] Editor target: {editor_target}")


if __name__ == "__main__":
    main()
