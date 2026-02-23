---
name: unreal-clean-rebuild
description: Generate or update a portable `CleanRebuild.bat` for Unreal Engine C++ projects. Use when the user asks to clean/rebuild Unreal projects, wants a reusable clean build script for multiple projects, or needs a safer batch file that auto-detects `.uproject`, Editor target, and UnrealBuildTool path.
---

# Unreal Clean Rebuild

## Workflow
1. Detect the Unreal project root.
   - Prefer user-provided path.
   - Otherwise use current working directory.
2. Generate `CleanRebuild.bat` with the bundled script:
   - Run `python scripts/generate_clean_rebuild.py --project-root "<path>"`.
   - Optionally set `--output` and `--target`.
3. Verify the generated file exists and includes:
   - Clean steps (`Intermediate`, `Binaries`, `.vs`, `Saved/Intermediate`)
   - `.uproject` auto-detection
   - UBT path detection
   - `-projectfiles` and Editor target build command
4. If detection in the target environment fails, instruct to set one of:
   - `UE_ENGINE_ROOT` (engine root path)
   - `UE_UBT_PATH` (direct UnrealBuildTool.exe path)

## Commands
```powershell
# Generate in current Unreal project root
python scripts/generate_clean_rebuild.py --project-root .

# Generate custom file name
python scripts/generate_clean_rebuild.py --project-root . --output RebuildEditor.bat

# Override editor target explicitly
python scripts/generate_clean_rebuild.py --project-root . --target MyGameEditor
```

## Script
- `scripts/generate_clean_rebuild.py`
  - Find `.uproject` and infer project name.
  - Infer Editor target from `Source/*Editor.Target.cs` (fallback: `<ProjectName>Editor`).
  - Emit a portable batch script that:
    - Auto-detects UBT from environment, EngineAssociation, registry, or PATH.
    - Regenerates project files.
    - Builds `<EditorTarget> Win64 Development`.
