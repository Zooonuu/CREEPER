from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parent
required = [
    "README.md",
    "TODO.md",
    "FILE_GUIDE.md",
    "project.yaml",
    "00_original_example",
    "01_baseline/process",
    "01_baseline/device",
    "02_proposed/process",
    "02_proposed/device",
    "03_doe",
    "03_doe/generate_cases.py",
    "03_doe/generate_anchor_cases.py",
    "03_doe/suggest_active_cases.py",
    "03_doe/generate_local_refinement_cases.py",
    "03_doe/generate_robust_cases.py",
    "04_circuit",
    "04_circuit/fo4/fo4_inverter_benchmark.cmd.template",
    "05_results",
    "05_results/pareto.py",
    "05_results/robust_optimum.py",
    "05_results/yield_like.py",
    "06_submission",
]

missing = [item for item in required if not (ROOT / item).exists()]

try:
    with (ROOT / "project.yaml").open(encoding="utf-8") as f:
        yaml.safe_load(f)
except Exception as exc:
    missing.append(f"project.yaml error: {exc}")

if missing:
    print("[FAIL]")
    for item in missing:
        print(" -", item)
    sys.exit(1)

print("[OK] 프로젝트 구조가 정상입니다.")
