# KUFET — Surrogate-Assisted TCAD DTCO of a Fabrication-Aware Asymmetric Low-k Composite Spacer in SOI FinFETs

솔로 캡스톤/연구 프로젝트. **항상 한국어로 답변한다.**

## 시작 전 필수

작업을 시작하기 전에 항상 아래 4개 문서를 읽고 최신 규칙/진행상황을 파악한다 (한 번 읽고 끝이 아니라 매 세션 다시 확인하는 running brief로 취급):

- `README.md` — 연구 방향, 윤리/표현 경계, 실행 예시
- `TODO.md` — 진행 체크리스트 (진행상황/새 결정은 여기에만 반영, **새 계획 문서를 만들지 말 것**)
- `07_docs/FILE_GUIDE.md` — 파일별 역할과 수정 원칙
- `project.yaml` — 공통 변수, DOE/active DOE/local refinement/robust validation 설정

## 연구 개요

- 기존 SOI FinFET은 source/drain에 대칭 Si3N4 spacer. 제안 구조는 source-side spacer를 짧게, drain-side spacer를 길게 하고 drain-side 내부에 SiO2 low-k 구간을 삽입 — drain-side Cgd/field crowding/DIBL/leakage 감소, source-side 구동전류 손실 최소화가 목표.
- 최종 판단 기준은 소자 지표가 아니라 **FO4 inverter benchmark**의 delay/power/energy/EDP.
- 알고리즘: 24-sample initial LHS DOE + anchor case → device-level screening → GP(RBF kernel) + UCB acquisition 기반 **single-objective** Bayesian optimization으로 active DOE 후보 추천 (`03_doe/suggest_active_cases.py`, numpy/scipy만 사용, sklearn/ANN/MOBO/NSGA-II 없음) → 0.5nm fabrication grid snapping → circuit-level FO4 Pareto → ±0.3/±0.5nm robust validation → robust DTCO optimum 선정 (nominal optimum 아님).

### 좌표축 / 변수
- x: Source→Drain, y: Fin width, z: Fin height
- `L_sp_S` source-side spacer length, `L_sp_D` drain-side spacer total length, `W_low_k` drain-side 내부 SiO2 low-k length

### 설계공간 / 제약
- `l_sp_s_nm`: 3.0~7.0, `l_sp_d_nm`: 5.0~11.0, `w_low_k_nm`: 0.0~4.0
- `l_sp_d_nm >= l_sp_s_nm`, `w_low_k_nm <= l_sp_d_nm`

## 디렉토리 레이아웃

- `00_original_example/` — 학교 제공 원본 TCAD deck (**절대 수정 금지**, 현재 미확보/비어있음)
- `01_baseline/`, `02_proposed/` — sprocess/sdevice `.cmd.template` (현재 placeholder)
- `03_doe/` — DOE/anchor/active/local-refinement/robust case generator (Python, 구현 완료)
- `04_circuit/` — inverter 단품 sanity check + FO4 benchmark template
- `05_results/` — `pareto.py`, `robust_optimum.py`, `yield_like.py`, `predicted_vs_actual.py`, `plot_figures.py` (구현 완료)
- `06_submission/` — report/poster/presentation (대부분 비어있음)
- `07_docs/` — `FILE_GUIDE.md`, `PROMPT.txt`(구 버전 브리핑, 이 CLAUDE.md로 대체됨), `daily_schedule.html/.pdf`

## TCAD 도구

메인 툴은 **Synopsys Sentaurus (sprocess/sdevice)**. 작업은 두 대의 머신(코드/문서 작업용 노트북, sprocess/sdevice 실행용 학교 TCAD PC)에 걸쳐 git으로 동기화된다. `.tdr`/`.plt`/`.log` 등 대용량 raw TCAD output은 **절대 커밋하지 않음** — deck 텍스트와 summary CSV/figure만 커밋.

## 절대 지켜야 할 것 (연구 윤리/표현)

- "비대칭 dual-k/composite spacer FinFET 최초 제안" 이라고 쓰지 않는다.
- "spacer engineering과 circuit delay를 최초로 연결" 했다고 쓰지 않는다.
- "실제 제작/실측 검증" 이라고 쓰지 않는다.
- ANN, MOBO(multi-objective BO), NSGA-II를 실제 구현한 것처럼 쓰지 않는다 — 실제 구현된 것은 GP 기반 **single-objective** Bayesian optimization(active DOE)뿐이며 정확히 그렇게 표현한다.
- Pal et al. 2015 (R01)을 asymmetric/dual-k spacer 또는 device-circuit codesign 논의 시 직접 선행연구로 반드시 인용한다. 이 프로젝트의 기여는 workflow와 제한된 TCAD 예산 하의 DTCO/robust validation.
- TCAD simulation 결과, mock/test 결과, 실측을 항상 명확히 구분한다. **결과를 지어내거나 mock 결과를 실제 TCAD 결과처럼 쓰지 않는다** — `00_original_example/`이 비어있고 모든 deck template이 placeholder인 현재 상태에서 실제 TCAD 결과는 아직 존재하지 않음.
- 논문 figure, 유료 PDF, proprietary TCAD deck을 커밋하거나 복제하지 않는다.

## 작업 원칙

- 작업 전 항상 현재 git 상태와 관련 파일을 먼저 확인한다.
- `00_original_example/`은 수정하지 않는다.
- baseline이 안정화되기 전에는 DOE를 과하게 확장하지 않는다.
- Baseline과 Proposed는 spacer 조건 외에는 동일 조건을 유지한다.
- 최종 후보는 continuous DOE 값이 아니라 fabrication grid로 snap 후 재시뮬레이션한 결과만 주장한다.
- 새 결정/진행률은 `TODO.md`에 반영하고, 불필요한 별도 계획 문서를 만들지 않는다.
- 작업 요청을 받으면 먼저 관련 문서/스크립트를 읽고 현재 상태를 짧게 요약한 뒤 바로 필요한 수정/분석을 진행한다.
