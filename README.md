# Unreal Rebuild Skill

Portable Codex skill for generating `CleanRebuild.bat` in Unreal Engine C++ projects.

## What It Does
- Detect `.uproject` automatically
- Infer Editor target from `Source/*Editor.Target.cs` (fallback: `<ProjectName>Editor`)
- Generate a reusable `CleanRebuild.bat`
- Include UnrealBuildTool detection logic (env var, EngineAssociation, registry, PATH)

## Repository Structure
```text
unreal-clean-rebuild/
  SKILL.md
  agents/openai.yaml
  scripts/generate_clean_rebuild.py
```

## Generate CleanRebuild.bat
```powershell
python unreal-clean-rebuild/scripts/generate_clean_rebuild.py --project-root .
```

Optional:
```powershell
python unreal-clean-rebuild/scripts/generate_clean_rebuild.py --project-root . --output RebuildEditor.bat
python unreal-clean-rebuild/scripts/generate_clean_rebuild.py --project-root . --target MyGameEditor
```

## Runtime Notes
If UnrealBuildTool is not found automatically, set one of:
- `UE_ENGINE_ROOT` (engine root path)
- `UE_UBT_PATH` (direct path to `UnrealBuildTool.exe`)
