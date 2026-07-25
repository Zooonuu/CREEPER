# FILE GUIDE

이 문서는 `OASIS-FinFET` 프로젝트에 존재하는 주요 파일과 폴더의 역할, 수정 시점, 생성 주체를 정리한다.

프로젝트 연구 배경은 `README.md`, 실제 진행률은 `TODO.md`, 공통 설정은 `project.yaml`에 둔다. 새 결정과 진행 상황은 별도 계획 문서를 만들지 말고 `TODO.md`와 관련 설정 파일에 반영한다.

---

## 1. 최상위 파일

### `README.md`

프로젝트의 대표 설명 문서다.

포함 내용:

- 연구 주제
- Baseline/Proposed 소자 구조
- Surrogate-assisted active DOE 알고리즘
- Fabrication-aware grid snapping
- Local refinement와 robust validation
- 실행 예시
- 파일 관리 원칙

수정 시점:

- 연구 주제, 방법론, 평가 기준처럼 프로젝트 전체 방향이 바뀔 때
- 제출물에서 사용할 공식 표현이 바뀔 때

주의:

- TCAD 결과를 실제 제작 결과처럼 표현하지 않는다.
- Initial DOE 48개를 최종 통계 검증으로 과장하지 않는다.
- Asymmetric/dual-k/composite spacer 구조 자체의 최초성을 주장하지 않는다.
- Pal et al. 2015 등 직접 중복 선행연구를 본문에서 반드시 인용한다.

### `TODO.md`

현재 해야 할 일을 체크박스로 관리한다.

포함 내용:

- 환경 및 원본 example 확보
- Baseline/Proposed TCAD 구현
- DOE 및 anchor case
- Surrogate-assisted active DOE
- Fabrication-aware local refinement
- Robust validation
- 회로 검증
- 제출물 제작

수정 시점:

- 실제 작업을 시작하거나 완료했을 때
- 프로젝트 흐름이 바뀌었을 때

### `project.yaml`

프로젝트의 공통 설정 파일이다.

주요 섹션:

- `project`: 프로젝트명, 소자 종류, 방법론
- `fixed`: gate length, fin height, fin width, EOT, VDD, 온도
- `design_space`: `L_sp_S`, `L_sp_D`, `W_low_k` 범위
- `doe`: initial DOE sample 수, 방법, seed, 출력 경로
- `anchor_cases`: baseline, center, feasible corner 생성 설정
- `fabrication_grid`: 최종 후보 snapping 단위
- `active_doe`: device screening과 circuit DTCO 모드별 surrogate-assisted active DOE 설정
- `local_refinement`: circuit-level DTCO Pareto 후보 주변 grid 탐색 설정
- `robust_validation`: 공정 편차 검증 및 guardrail 설정

주의:

- 결과를 확인한 뒤 좋은 결과가 나오도록 범위나 목적함수를 몰래 바꾸지 않는다.
- 범위 변경 시 commit과 이유를 남긴다.
- `active_doe`에 실제 구현하지 않은 ANN, MOBO, NSGA-II 같은 알고리즘명을 넣지 않는다.

### `requirements.txt`

Python 분석 환경에서 필요한 패키지 목록이다.

현재 패키지:

- `numpy`
- `pandas`
- `scipy`
- `matplotlib`
- `PyYAML`

### `check_project.py`

필수 파일과 폴더가 존재하는지 검사한다.

실행:

```bash
python3 check_project.py
```

정상 출력:

```text
[OK] 프로젝트 구조가 정상입니다.
```

수정 시점:

- 필수 폴더나 핵심 스크립트가 추가/삭제될 때

### `.gitignore`

Git에 올리지 않을 파일을 지정한다.

제외 대상:

- Python 가상환경과 cache
- TCAD 대용량 raw output
- mesh/structure/log 파일
- 자동 생성 case CSV
- raw result 파일

요약 CSV와 최종 figure는 Git에 올릴 수 있다.

주의:

- 유료 논문 PDF, 논문 원본 그림, proprietary TCAD deck은 Git에 올리지 않는다.
- 학교 설치본에서 가져온 Sentaurus/Silvaco example은 공개 가능 여부를 확인하기 전까지 raw deck 그대로 commit하지 않는다.

---

## 2. TCAD 구조 폴더

### `00_original_example/`

학교 TCAD PC에서 확보한 원본 3D FinFET example을 수정 없이 보존한다.

원칙:

- 원본 파일은 직접 수정하지 않는다.
- baseline 작업은 `01_baseline/`로 복사한 뒤 시작한다.
- 학교 라이선스에 포함된 proprietary example은 공개 Git 저장소에 올리지 않는다.
- 공개 가능한 경우에도 출처와 tool/version 정보를 기록한다.

### `01_baseline/`

대칭 `Si3N4` spacer SOI FinFET baseline을 만든다.

주요 파일:

- `process/baseline_sprocess.cmd.template`
- `device/baseline_nmos_sdevice.cmd.template`
- `device/baseline_pmos_sdevice.cmd.template`
- `output/.gitkeep`

목표:

- 3D mesh 수렴
- NMOS/PMOS Id-Vg, Id-Vd 수렴
- Ion, Ioff, Vth, SS, DIBL 추출
- baseline 구조와 지표 동결

### `02_proposed/`

비대칭 drain-side low-k composite spacer 구조를 만든다.

주요 파일:

- `process/proposed_sprocess.cmd.template`
- `device/proposed_nmos_sdevice.cmd.template`
- `device/proposed_pmos_sdevice.cmd.template`
- `output/.gitkeep`

핵심 변수:

- `L_sp_S`
- `L_sp_D`
- `W_low_k`

목표:

- baseline과 동일 조건에서 spacer 효과만 비교
- Cgd, DIBL, electric field, current density 변화 확인

---

## 3. DOE 및 알고리즘 폴더

### `03_doe/generate_cases.py`

Initial DOE case를 생성한다.

현재 기본 설정:

- sample 수: `project.yaml`의 `doe.initial_samples`, 기본 48개
- 방법: LHS 또는 Sobol
- 출력: `03_doe/cases/initial_doe_cases.csv`

역할:

- 연속 설계공간을 탐색하기 위한 초기 sample 생성
- 최종 공정 가능성 주장이 아니라 surrogate 학습 및 Pareto 방향 탐색용 데이터 생성

### `03_doe/generate_anchor_cases.py`

Baseline reference, center, feasible corner case를 생성한다.

출력:

- `03_doe/cases/anchor_cases.csv`

역할:

- LHS/Sobol sample만으로 부족한 기준점과 극단 조건 보강
- 48개 DOE의 해석 신뢰성 보조

### `03_doe/suggest_active_cases.py`

완료된 TCAD 결과를 바탕으로 추가 실행할 active DOE 후보를 추천한다.

입력:

- `05_results/summary/all_results.csv`

출력:

- `03_doe/cases/active_suggested_cases.csv`

알고리즘:

- 완료된 결과로 간단한 surrogate model 학습
- 성능 예측값과 surrogate uncertainty를 함께 고려
- 기존 sample과 너무 가까운 후보 제거
- fabrication grid로 snapping된 후보 추천
- `--mode device_screening`은 Ion/Ioff/DIBL/Cgd 기준으로 회로 검증 전 후보를 줄인다.
- `--mode circuit_dtco`는 FO4 inverter benchmark의 delay/power/energy/EDP 기준으로 최종 DTCO 후보를 추천한다.

주의:

- 이 스크립트는 거대한 AI 모델이 아니라 제한된 TCAD 예산을 효율적으로 쓰기 위한 lightweight surrogate-assisted sampler다.
- 보고서에는 ANN, MOBO, NSGA-II를 실제 구현한 것처럼 쓰지 않는다.
- Bayesian optimization이나 genetic algorithm은 실제 구현 전까지 배경 또는 향후 확장으로만 언급한다.

### `03_doe/generate_local_refinement_cases.py`

Circuit-level DTCO Pareto 후보 주변의 fabrication-aware grid case를 생성한다.

입력:

- `05_results/summary/circuit_dtco_pareto.csv`

출력:

- `03_doe/cases/local_refinement_cases.csv`

역할:

- `3.12 nm` 같은 연속 DOE 후보를 최종 DTCO 주장에 직접 쓰지 않도록 방지
- `0.5 nm` 또는 설정된 grid 단위로 후보를 snap
- circuit-level 후보 주변을 작은 grid로 다시 검증

### `03_doe/generate_robust_cases.py`

최종 후보 주변 공정 편차 검증 case를 생성한다.

입력:

- `05_results/summary/circuit_dtco_pareto.csv` 또는 local refinement 결과에서 고른 후보 CSV

출력:

- `03_doe/cases/robust_cases.csv` 또는 지정한 경로

역할:

- nominal candidate 주변 `±0.3 nm`, `±0.5 nm` variation 생성
- one-at-a-time variation과 combined corner variation 생성
- robust optimum 계산용 입력 준비

### `03_doe/template/master_case.cmd.template`

DOE case를 실제 TCAD deck으로 변환할 때 사용할 master template이다.

---

## 4. 회로 폴더

### `04_circuit/inverter/inverter.cmd.template`

Unit CMOS inverter 검증용 template이다.

목표:

- NMOS/PMOS 연결 방향 확인
- VTC와 switching 정상 동작 확인

### `04_circuit/fo4/fo4_inverter_benchmark.cmd.template`

FO4 inverter benchmark 검증용 template이다.

목표:

- tpHL/tpLH
- FO4 delay
- output slew
- average power
- energy per transition
- PDP 또는 EDP

주의:

- DUT inverter가 4x load inverter input을 구동하도록 구성한다.
- Proposed device의 drain-side composite spacer가 switching output node를 향하도록 배치한다.

---

## 5. 결과 분석 폴더

### `05_results/pareto.py`

Pareto front를 계산한다.

Device screening 예시:

```bash
python3 05_results/pareto.py \
  --input 05_results/summary/all_results.csv \
  --maximize ion_A \
  --minimize ioff_A dibl_mV_V cgd_F \
  --output 05_results/summary/device_screening_pareto.csv
```

Circuit-level DTCO 예시:

```bash
python3 05_results/pareto.py \
  --input 05_results/summary/all_results.csv \
  --minimize fo4_delay_s average_power_W energy_per_transition_J edp_Js \
  --output 05_results/summary/circuit_dtco_pareto.csv
```

특징:

- `Ion`처럼 클수록 좋은 지표와 `Cgd`, `fo4_delay_s`, `EDP`처럼 작을수록 좋은 지표를 함께 처리한다.
- 소자 지표 Pareto는 screening용이고, 최종 DTCO Pareto는 회로 지표 기준으로 계산한다.
- 기존 `--objectives` 인자는 backward-compatible minimization 용도로만 남긴다.

### `05_results/robust_optimum.py`

공정 편차 case 결과를 요약하고 robust optimum을 고른다.

입력:

- robust result CSV
- 선택적으로 baseline reference CSV

출력:

- `05_results/summary/robust_optimum.csv`

계산 항목:

- Ion 유지율
- EDP 열화율
- Cgd 개선 유지율
- Cgd 개선 대비 Ion 손실 보상율
- FO4 delay, average power, energy per transition 기준 회로 DTCO 열화율
- guardrail 통과 여부
- robust score

### `05_results/yield_like.py`

Robust variation 결과에서 yield-like spec pass rate를 계산한다.

입력:

- `05_results/summary/robust_results.csv`
- 각 `base_case_id`마다 `variation_kind=nominal` 행과 variation sample 행

출력:

- `05_results/summary/yield_like.csv`

계산 항목:

- variation sample 수
- spec 통과/실패 개수
- spec pass rate
- Ion retention, Cgd variation, EDP/FO4 delay/power/energy degradation별 pass rate
- 실패한 variation label

### `05_results/plot_figures.py`

최종 figure 생성을 담당한다.

목표 figure:

- Id-Vg 및 핵심 지표
- Cgd/전계 heatmap
- Device screening Pareto front
- Circuit-level DTCO Pareto front
- Active DOE 전후 비교
- Robust optimum summary

### `05_results/raw/`

TCAD raw output의 로컬 보관 위치다.

주의:

- 대용량 raw 파일은 Git에 올리지 않는다.
- 필요한 요약 CSV와 핵심 figure만 Git에 반영한다.

### `05_results/summary/`

분석용 요약 CSV를 둔다.

예상 파일:

- `all_results.csv`
- `device_screening_pareto.csv`
- `circuit_dtco_pareto.csv`
- `robust_results.csv`
- `robust_optimum.csv`

주의:

- Mock/test 결과, TCAD simulation 결과, 실제 측정 결과를 파일명 또는 `source_type`/`note` 컬럼으로 구분한다.
- 제출용 표와 그림 caption에는 TCAD simulation 결과인지 실제 측정값인지 명확히 적는다.

### `05_results/figures/`

보고서, 포스터, 발표자료에 들어갈 최종 그림을 둔다.

---

## 6. 제출 폴더

### `06_submission/report/`

보고서 파일을 둔다.

### `06_submission/poster/`

포스터 파일을 둔다.

### `06_submission/presentation/`

발표자료 파일을 둔다.

---

## 7. 권장 작업 순서

```text
1. 원본 3D FinFET example 확보
2. baseline 구조 재현
3. proposed 구조 구현
4. initial DOE 48개 + anchor case 생성
5. TCAD 실행 및 all_results.csv 정리
6. Device screening Pareto 계산
7. device active DOE 후보 추천 및 실행
8. 회로 검증 후 circuit-level DTCO Pareto 계산
9. grid-snapped local refinement 실행
10. robust validation 실행
11. 최종 그림과 제출물 작성
```

---

## 8. 결과 CSV 권장 스키마

```text
case_id, case_group, structure,
l_sp_s_nm, l_sp_d_nm, w_low_k_nm,
grid_snapped, grid_step_nm,
ion_A, ioff_A, vth_V, ss_mV_dec, dibl_mV_V,
cgd_F, cgs_F, cgg_F,
fo4_delay_s, tpHL_s, tpLH_s, output_slew_s, average_power_W, energy_per_transition_J, edp_Js,
status, note
```

Robust 결과 CSV 권장 스키마:

```text
robust_case_id, base_case_id, variation_kind, delta_nm,
l_sp_s_nm, l_sp_d_nm, w_low_k_nm,
ion_A, cgd_F, edp_Js,
status, note
```

---

## 9. 연구윤리 및 참고문헌 사용 원칙

직접 중복 선행연구는 `references/REFERENCE_LINKS_SUMMARY.md`의 R01-R07을 우선 확인한다. 특히 R01은 asymmetric dual-spacer FinFET, device-circuit codesign, variability, inverter 평가가 본 프로젝트와 직접 겹치므로 반드시 인용한다.

안전한 기여 표현:

```text
선행연구의 asymmetric/dual-k spacer FinFET 및 device-circuit codesign 흐름을 바탕으로,
본 프로젝트는 SOI FinFET seed deck에서 drain-side low-k composite spacer 설계공간을
정의하고, 제한된 TCAD 실행 예산 안에서 device screening, circuit-level DTCO Pareto,
fabrication-aware grid snapping, robust validation workflow를 구축한다.
```

피해야 할 표현:

- 비대칭 dual-k/composite spacer FinFET을 최초로 제안하였다.
- spacer engineering과 circuit delay를 최초로 연결하였다.
- robust/variability analysis를 최초로 수행하였다.
- SiO2 low-k spacer가 기존에 없던 신공정이다.
- TCAD 결과를 실제 fabrication 또는 실측 결과로 검증하였다.
- ANN/MOBO/NSGA-II 기반 최적화를 수행하였다. 단, 실제 구현 및 검증한 경우는 제외한다.

그림 사용 원칙:

- 논문 figure는 그대로 복제하지 않는다.
- 직접 작성한 conceptual schematic을 사용하고, caption 또는 본문에 관련 선행연구를 인용한다.
- `picture.png` 같은 손그림은 내부 개념 정리용이며, 제출용 그림은 새로 정리해 작성한다.

인용 최소 세트:

- R01: asymmetric dual-spacer + device-circuit codesign + variability 직접 선행연구
- R03 또는 R05: spacer capacitance와 circuit delay 연결 근거
- R06 또는 R08: electric field / underlap / spacer trade-off 물리 근거
- R11 또는 R12: low-k/hybrid spacer 공정 및 capacitance reduction 근거
- R15: FinFET 기본 구조 배경
- R16: DOE/LHS 근거
- R24 또는 R26: Sentaurus FinFET/3D TCAD 지원 및 seed example 근거
