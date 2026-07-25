# TODO

이 문서는 프로젝트 전체 진행을 **일정 캘린더(0절)에 맞춘 주차별 순서**로 정리한다. 실제 작업은 혼자 진행하고, 매 TCAD 세션 시작 시 이 문서 기준으로 어디까지 했는지/다음에 뭘 할지 확인하고 진행한다.

전체 목표:

```text
SOI FinFET에서 drain-side low-k composite spacer 구조를 설계하고,
소자 지표뿐 아니라 FO4 회로 성능과 공정 편차 robust성까지 기준으로 최적 후보를 선정한다.
```

전체 흐름:

```text
환경 확인
→ Baseline 소자 확보
→ Proposed 소자 확보
→ DOE/device screening
→ 회로 DTCO
→ local refinement
→ robust validation
→ 최종 발표/보고서
```

---

## 0. 일정 캘린더 (2026-07-25 ~ 2026-08-31)

평일 = 학교 TCAD PC 실행, 주말 = 결과 정리 및 보고서/발표자료 준비. 확인된 TCAD 툴은 Synopsys Sentaurus(SWB, sprocess/sdevice)다. 진행이 늦어지면 6절 "최소 성공 기준"으로 범위를 축소한다. 각 항목의 상세 체크리스트는 1절의 같은 주차 번호를 참고한다.

- [ ] 2026-07-25(토)~07-26(일) — Week0: 준비 및 프로젝트 이해
- [ ] 2026-07-27(월)~07-31(금) — Week1: 환경 확인 + baseline 구조/지표 확보
- [ ] 2026-08-01(토)~08-02(일) — Weekend1: baseline 결과 정리, 보고서 배경/선행연구 초안
- [ ] 2026-08-03(월)~08-07(금) — Week2: proposed 구현 + initial DOE/anchor 생성 및 실행 착수
- [ ] 2026-08-08(토)~08-09(일) — Weekend2: all_results.csv 누적 정리, baseline vs proposed 비교, 회로 조건 사전 확정
- [ ] 2026-08-10(월)~08-14(금) — Week3: DOE 실행 마무리 + device screening + 회로 실행 환경 확인
- [ ] 2026-08-15(토)~08-16(일) — Weekend3: device Pareto 정리, 회로 검증 후보 확정, 보고서 소자 섹션
- [ ] 2026-08-17(월)~08-21(금) — Week4: unit inverter + FO4 회로 DTCO 실행
- [ ] 2026-08-22(토)~08-23(일) — Weekend4: circuit Pareto 정리, 최종 후보 압축, 보고서 회로 섹션
- [ ] 2026-08-24(월)~08-28(금) — Week5: local refinement + robust validation 실행
- [ ] 2026-08-29(토)~08-30(일) — Weekend5: robust summary 정리, nominal vs robust 최종 스토리
- [ ] 2026-08-31(월) — 마감: 최종 그림/표/표현 검토, 제출물 마무리

---

## 1. 주차별 상세 체크리스트

### Week0 (07-25~07-26, 주말/준비)

- [ ] `project.yaml`의 `fixed` 항목이 뭘 채워야 하는지만 목록 확인 (실제 숫자는 Week1에 원본 example을 열어서 읽어온 뒤 채운다 — 임의로 정하지 않음)
- [ ] `fabrication_grid.step_nm` 가안 검토: 원본 example에서 읽어오는 값이 아니라 최종 후보 반올림에 쓸 프로젝트 차원의 가정값. 우선 0.5nm 유지, Week1에 원본 example의 spacer 공정 step과 비교해 현실성만 점검
- [ ] `baseline_sprocess`, `proposed_sprocess`, `inverter`, `fo4_inverter_benchmark` template 내용 재검토
- [ ] 노트북 ↔ 학교 PC repo 동기화 절차 점검 (`git clone`/`git pull` 가능 여부)

### Week1 (07-27~07-31, 평일): 환경 확인 + Baseline

환경 확인:

- [ ] 학교 TCAD PC 로그인
- [ ] Sentaurus 실행 환경 로드 방법 기록
- [ ] Sentaurus Process(sprocess) 실행 확인
- [ ] Sentaurus Device(sdevice) 실행 확인
- [ ] Sentaurus Visual/Inspect 실행 확인
- [ ] 실행 가능한 3D FinFET example 확보
- [ ] 원본 example을 수정하지 않고 1회 실행
- [ ] structure/mesh/Id-Vg 결과 확인
- [ ] 결과 파일 USB/외장 SSD로 복사 테스트
- [ ] 우리 repo를 TCAD PC로 복사 또는 `git clone` 가능 여부 확인
- [ ] 원본 example의 gate_length, fin_height, fin_width, EOT, VDD 실제 값 확인 → `project.yaml`의 `fixed`에 기록
- [ ] 원본 example의 spacer 공정 step(치수 단위)을 참고해 `fabrication_grid.step_nm`(현재 0.5nm 가안) 현실성 점검

Baseline (대칭 Si3N4 spacer, source/drain 동일 길이):

- [ ] 원본 FinFET example을 baseline 작업 폴더로 복사
- [ ] substrate/BOX/fin/gate/spacer/source/drain/contact 구조 확인
- [ ] 대칭 Si3N4 spacer 구조 확인
- [ ] 3D mesh 생성 및 viewer에서 확인
- [ ] NMOS Id-Vg 수렴
- [ ] NMOS Id-Vd 수렴
- [ ] PMOS Id-Vg 수렴
- [ ] PMOS Id-Vd 수렴
- [ ] Ion, Ioff, Vth, SS, DIBL, Cgd 추출
- [ ] baseline 구조와 지표 동결

산출물: 원본 example 경로, TCAD tool/version, 실행 순서, 실행 성공 스크린샷, 결과 회수 방법, baseline structure 그림, baseline Id-Vg/Id-Vd 그래프, baseline metric CSV

### Weekend1 (08-01~08-02): 정리

- [ ] baseline 결과 정리 (구조 그림, Id-Vg/Id-Vd 그래프, metric CSV)
- [ ] 보고서 배경/선행연구(R01 Pal et al. 등) 섹션 초안

### Week2 (08-03~08-07, 평일): Proposed + DOE 착수

Proposed (source-side 짧은 Si3N4 + drain-side 긴 composite spacer + 내부 SiO2 low-k):

- [ ] source-side 짧은 Si3N4 spacer 구현
- [ ] drain-side 긴 spacer 구현
- [ ] drain-side SiO2 low-k 구간 구현
- [ ] 실제 생성된 `L_sp_S`, `L_sp_D`, `W_low_k` 확인
- [ ] source/drain 방향 고정: x축 = Source → Drain
- [ ] proposed NMOS Id-Vg/Id-Vd 수렴
- [ ] proposed PMOS Id-Vg/Id-Vd 수렴
- [ ] baseline과 동일 bias/mesh/physics 조건인지 확인
- [ ] Ion, Ioff, Vth, SS, DIBL, Cgd 비교
- [ ] electric field, current density, Cgd 변화 확인

DOE 착수:

- [ ] `project.yaml`의 설계공간 확정
- [ ] `python3 03_doe/generate_cases.py`로 initial DOE case 생성
- [ ] `python3 03_doe/generate_anchor_cases.py`로 anchor case 생성
- [ ] baseline, center, feasible corner 우선 실행
- [ ] DOE case 실행 시작

산출물: proposed structure 그림, baseline vs proposed 비교표, Id-Vg/Id-Vd 비교 그래프, Cgd/Ion/DIBL 변화율, `03_doe/cases/initial_doe_cases.csv`, `03_doe/cases/anchor_cases.csv`

### Weekend2 (08-08~08-09): 정리 + 회로 조건 사전 확정

- [ ] 그 주까지의 결과를 `05_results/summary/all_results.csv`로 누적 정리
- [ ] 실패 case와 원인 기록
- [ ] baseline vs proposed 비교표 업데이트
- [ ] `04_circuit/inverter/inverter.cmd.template`, `04_circuit/fo4/fo4_inverter_benchmark.cmd.template` 내용 확인
- [ ] unit inverter 구성 정리, FO4 구성 정리: `IN -> INV_driver -> INV_DUT -> INV_load_4x`
- [ ] VDD, temperature, input pulse rise/fall/time period, transient simulation time, load 조건 확정
- [ ] tpHL/tpLH, output slew, average power, energy per transition, EDP 측정/계산 기준 확정
- [ ] 회로 결과 CSV 템플릿 작성

산출물: 회로 측정 기준 문서, delay/power/energy/EDP 계산식, 회로 결과 CSV 템플릿

### Week3 (08-10~08-14, 평일): DOE 마무리 + Device Screening + 회로 환경 확인

- [ ] 남은 DOE case 실행 완료
- [ ] 실패 case와 원인 기록
- [ ] 모든 결과를 `05_results/summary/all_results.csv`로 정리
- [ ] device screening 목적함수 확정: maximize Ion, minimize Ioff/DIBL/Cgd
- [ ] `python3 05_results/pareto.py`로 device Pareto 계산
- [ ] Cgd-Ion trade-off 확인
- [ ] `python3 03_doe/suggest_active_cases.py --mode device_screening`으로 active DOE 후보 추천
- [ ] 회로 검증 후보 3~5개 선정
- [ ] MixedMode 또는 회로 시뮬레이션 사용 가능 여부 확인 (TCAD PC에서)

산출물: `05_results/summary/all_results.csv`, 실패 case 목록, device Pareto plot, Cgd vs Ion trade-off 그래프, 회로 검증 후보 3~5개 목록

### Weekend3 (08-15~08-16): 정리

- [ ] device Pareto plot, Cgd-Ion trade-off 그래프 최종 정리
- [ ] 회로 검증 후보 3~5개 CSV 확정 (case_id, `L_sp_S`/`L_sp_D`/`W_low_k`, NMOS/PMOS 파일, Ion/Ioff/Vth/SS/DIBL/Cgd, source/drain 방향 — 2절 스키마 참고)
- [ ] 보고서 소자 섹션 작성

### Week4 (08-17~08-21, 평일): 회로 DTCO

Baseline 회로 sanity check:

- [ ] PMOS source = VDD, NMOS source = GND / PMOS·NMOS gate = IN / PMOS·NMOS drain = OUT 연결 확인
- [ ] unit inverter VTC 실행, switching 정상 여부 확인
- [ ] baseline FO4 transient 실행
- [ ] baseline tpHL/tpLH/delay/power/energy/EDP 추출

Proposed 후보 회로 검증 (drain-side composite spacer는 반드시 switching output node, 즉 OUT 쪽을 향하게 배치):

- [ ] 후보별 NMOS/PMOS 파일·source/drain 방향 확인
- [ ] unit inverter VTC 실행, 정상 switching 후보만 FO4로 이동
- [ ] FO4 transient 실행 → tpHL/tpLH, FO4 delay, output slew, average power, energy per transition, EDP 추출
- [ ] `python3 05_results/pareto.py`(circuit_dtco)로 circuit Pareto 계산
- [ ] 필요시 `python3 03_doe/suggest_active_cases.py --mode circuit_dtco`로 추가 후보 추천

산출물: baseline/후보별 inverter VTC, FO4 waveform, delay/power/energy/EDP 표, circuit Pareto plot

### Weekend4 (08-22~08-23): 정리

- [ ] circuit Pareto plot 정리, 회로 기준 최종 후보 1~2개 압축
- [ ] 보고서 회로 섹션 작성

### Week5 (08-24~08-28, 평일): Local Refinement + Robust Validation

- [ ] 회로 DTCO 결과 기준 최종 후보 1~2개 선정
- [ ] `python3 03_doe/generate_local_refinement_cases.py`로 grid-snapped case 생성/실행
- [ ] local refinement 결과를 `all_results.csv`에 병합, FO4 재평가, circuit Pareto 업데이트
- [ ] `python3 03_doe/generate_robust_cases.py`로 ±0.3/±0.5 nm variation case 생성/실행
- [ ] robust result CSV 작성, Ion 유지율/Cgd 개선 유지율 계산
- [ ] robust case의 FO4 delay/EDP 열화율 계산, nominal optimum과 robust optimum 비교

산출물: grid-snapped 최종 후보, robust 소자/회로 결과 CSV, robust summary table

### Weekend5 (08-29~08-30): 정리

- [ ] robust summary table/plot 최종 정리
- [ ] nominal vs robust 최종 스토리 정리

### 마감일 (08-31): 최종 정리

- [ ] 3절(최종 제출물), 4절(연구윤리) 체크리스트 전체 확인
- [ ] 보고서/포스터/발표자료 최종본

---

## 2. 결과 CSV 스키마

소자 결과 → 회로 입력:

```csv
case_id,structure,l_sp_s_nm,l_sp_d_nm,w_low_k_nm,nmos_file,pmos_file,ion_A,ioff_A,vth_V,ss_mV_dec,dibl_mV_V,cgd_F,vdd_V,temperature_K,drain_direction,status,note
```

필수 항목: case_id / structure(baseline·proposed·doe·local_refinement·robust) / `L_sp_S`·`L_sp_D`·`W_low_k` / NMOS·PMOS 결과 파일 / Ion·Ioff·Vth·SS·DIBL·Cgd / source-drain 방향 / VDD·temperature / 수렴 여부와 warning

회로 결과:

```csv
case_id,unit_inverter_ok,tpHL_s,tpLH_s,fo4_delay_s,output_slew_s,average_power_W,energy_per_transition_J,edp_Js,status,note
```

필수 항목: unit inverter 정상 switching 여부 / tpHL / tpLH / FO4 delay / output slew / average power / energy per transition / EDP / 회로 수렴 여부와 실패 원인 / waveform 파일

---

## 3. 최종 제출물

소자 중심 그림/표:

- [ ] baseline/proposed 3D 구조 비교
- [ ] 공정 흐름도
- [ ] Id-Vg 및 Id-Vd 그래프
- [ ] Ion/Ioff/Vth/SS/DIBL/Cgd 비교표
- [ ] electric field/current density contour
- [ ] DOE response map
- [ ] device Pareto plot
- [ ] Cgd-Ion trade-off 그래프

회로 중심 그림/표:

- [ ] unit inverter schematic
- [ ] FO4 benchmark schematic
- [ ] inverter VTC
- [ ] FO4 transient waveform
- [ ] delay/power/energy/EDP 비교표
- [ ] circuit Pareto plot
- [ ] robust EDP degradation plot

공통 문서:

- [ ] 선행연구 비교표
- [ ] 연구윤리/표절 방지 문장
- [ ] 보고서
- [ ] 포스터
- [ ] 발표자료
- [ ] 예상 질문 답변

최종 스토리:

```text
기존 asymmetric/low-k spacer 연구는 존재한다.
본 프로젝트는 SOI FinFET에서 drain-side low-k composite spacer 설계공간을 정의하고,
device metric뿐 아니라 FO4 회로 성능과 공정 편차 robust성까지 기준으로 최적 후보를 선정했다.
```

---

## 4. 연구윤리 및 표절 방지

- [ ] R01 Pal et al. 2015를 asymmetric dual-spacer/device-circuit codesign 직접 선행연구로 본문에 인용
- [ ] R03 또는 R05를 spacer capacitance와 inverter delay 연결 근거로 인용
- [ ] R06 또는 R08을 electric field, underlap, spacer trade-off 물리 근거로 인용
- [ ] R11 또는 R12를 low-k/hybrid spacer 공정 및 parasitic capacitance reduction 근거로 인용
- [ ] R16을 LHS/DOE 방법론 근거로 인용
- [ ] "최초 제안", "최초 연결", "실제 제작 검증", "실측 결과" 표현이 남아 있지 않은지 확인
- [ ] `suggest_active_cases.py` 구현 범위를 "GP(Gaussian Process) surrogate + UCB acquisition 기반 single-objective Bayesian optimization"으로 정확히 설명 (여러 지표는 scalarized utility로 결합한 단일 목적함수임을 명시)
- [ ] 실제 구현하지 않은 ANN/MOBO(multi-objective BO)/NSGA-II 사용 주장을 제거
- [ ] 논문 figure를 그대로 복제하지 않고 직접 작성한 schematic과 출처 인용만 사용
- [ ] 유료 논문 PDF와 proprietary Sentaurus deck이 Git에 포함되지 않았는지 확인
- [ ] TCAD 결과, mock 결과, 실제 측정 결과를 표/그림 caption에서 명확히 구분

---

## 5. 세션 진행 시 알려줄 정보 양식

매 TCAD 세션 시작 시 Claude가 먼저 이 문서(0절 캘린더, 1절 주차별 체크리스트) 기준으로 진행 상황과 다음 할 일을 제시한다. 다음 정보를 화면 캡처/로그와 함께 주면 바로 진행할 수 있다:

```text
현재 주차 (0절 기준):
내가 하려는 작업:
현재 가진 파일/결과:
막힌 부분:
오늘 확보해야 하는 산출물:
```

TCAD 실행 1건마다 기록할 내용:

```text
날짜:
case_id:
structure: baseline / proposed / doe / fo4 / robust
사용 deck:
변수:
  L_sp_S:
  L_sp_D:
  W_low_k:
실행 명령어:
결과:
  success / fail / partial
생성 파일:
에러 메시지 또는 warning:
다음에 확인할 점:
```

에러를 물어볼 때 붙여 넣을 최소 정보:

- [ ] 실행한 deck 파일 또는 수정한 부분
- [ ] terminal/log의 마지막 50~100줄
- [ ] structure/mesh 또는 plot screenshot
- [ ] 기대한 결과와 실제 결과의 차이
- [ ] case_id와 변수값

---

## 6. 최소 성공 기준

- [ ] 환경 확인: 원본 example 1회 실행
- [ ] Baseline: baseline NMOS Id-Vg 확보
- [ ] Proposed: proposed NMOS Id-Vg 확보
- [ ] DOE: anchor + DOE 15~20개 이상 확보
- [ ] Device screening: 회로 후보 3~5개 선정
- [ ] 회로 DTCO: 최소 1~2개 후보 FO4 delay/EDP 확보
- [ ] Robust validation: 최종 후보 1개 variation 검증
- [ ] 제출: 표절 위험 표현 제거, 직접 만든 그림 사용
