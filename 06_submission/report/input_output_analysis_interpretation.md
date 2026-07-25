# Input, Output, Result Analysis, and Interpretation

이 문서는 결과보고서와 발표자료에 넣을 프로젝트 데이터 흐름을 정리한다. 핵심 메시지는 다음과 같다.

> 본 프로젝트는 공정/구조 파라미터를 직접 최종 성능으로 주장하지 않고, TCAD 소자 지표와 FO4 회로 지표로 변환한 뒤 Pareto, robust validation, yield-like pass rate 관점에서 DTCO 후보를 선택한다.

---

## 1. 전체 입출력 흐름

```text
공통 설정(project.yaml)
  -> DOE/anchor/active/local/robust case CSV 생성
  -> TCAD process/device simulation
  -> 소자 metric 추출
  -> unit inverter 및 FO4 circuit simulation
  -> all_results.csv / robust_results.csv 정리
  -> Pareto, robust optimum, yield-like pass rate 분석
  -> 최종 figure/table/report/presentation
```

프로젝트 관점의 최종 input은 `L_sp_S`, `L_sp_D`, `W_low_k`와 고정된 FinFET 조건이고, 최종 output은 단순한 최적 spacer 조합 하나가 아니라 다음 세 가지다.

- Circuit-level DTCO Pareto candidate
- Robust DTCO optimum
- Yield-like spec pass rate가 높은 후보

---

## 2. Input

### 2.1 공통 설정 input

`project.yaml`이 프로젝트 전체의 기준 input이다.

| 항목 | 의미 |
|---|---|
| `fixed` | Gate length, fin height, fin width, EOT, VDD, temperature 등 고정 조건 |
| `materials` | Si fin, SiO2 BOX, HfO2 gate dielectric, TiN gate, Si3N4 spacer, SiO2 low-k |
| `design_space` | `l_sp_s_nm`, `l_sp_d_nm`, `w_low_k_nm` 탐색 범위 |
| `constraints` | `l_sp_d_nm >= l_sp_s_nm`, `w_low_k_nm <= l_sp_d_nm` |
| `circuit_evaluation` | FO4 inverter benchmark와 회로 metric 정의 |
| `robust_validation` | ±0.3/±0.5 nm variation 및 robust guardrail |
| `yield_like` | variation sample pass rate를 계산하기 위한 spec |

### 2.2 설계 변수 input

본 프로젝트에서 의도적으로 바꾸는 변수는 세 개다.

| 변수 | 의미 | 해석 |
|---|---|---|
| `L_sp_S` | Source-side spacer length | Source 쪽 series resistance와 carrier injection에 영향 |
| `L_sp_D` | Drain-side spacer total length | Drain 전계, DIBL, Cgd, parasitic effect에 영향 |
| `W_low_k` | Drain-side spacer 내부 low-k 구간 길이 | Drain-side fringe capacitance와 Cgd 저감에 영향 |

나머지 조건은 가능한 한 고정해서, 결과 차이가 spacer 구조에서 나오도록 한다.

### 2.3 TCAD simulation input

TCAD 단계의 input은 baseline/proposed process deck과 device deck이다.

- Baseline: symmetric `Si3N4` spacer SOI FinFET
- Proposed: source-side short spacer + drain-side low-k composite spacer
- NMOS/PMOS device simulation deck
- DOE case CSV에서 생성된 spacer 파라미터

### 2.4 회로 simulation input

회로 단계의 input은 TCAD에서 얻은 NMOS/PMOS 특성과 회로 benchmark다.

- Unit CMOS inverter: 연결 방향, VTC, switching sanity check
- FO4 inverter benchmark: `IN -> INV_driver -> INV_DUT -> INV_load_4x`
- Proposed device의 drain-side composite spacer는 switching output node를 향하게 배치

---

## 3. Output

### 3.1 Case generation output

| 단계 | 출력 파일 | 역할 |
|---|---|---|
| Initial DOE | `03_doe/cases/initial_doe_cases.csv` | 초기 24개 탐색 case |
| Anchor case | `03_doe/cases/anchor_cases.csv` | baseline, center, feasible corner 기준점 |
| Active DOE | `03_doe/cases/active_suggested_cases.csv` | surrogate가 추천한 추가 실행 후보 |
| Local refinement | `03_doe/cases/local_refinement_cases.csv` | circuit Pareto 후보 주변 grid-snapped 후보 |
| Robust validation | `03_doe/cases/robust_cases.csv` | 최종 후보 주변 variation case |

이 파일들은 "결과"가 아니라 TCAD/회로 시뮬레이션을 돌리기 위한 실행 목록이다.

### 3.2 TCAD/device output

TCAD 결과에서 추출해 `all_results.csv`에 모으는 핵심 소자 output은 다음이다.

| Metric | 방향 | 의미 |
|---|---|---|
| `ion_A` | 클수록 좋음 | 구동 전류, performance 잠재력 |
| `ioff_A` | 작을수록 좋음 | leakage |
| `vth_V` | 목표 범위 | threshold voltage |
| `ss_mV_dec` | 작을수록 좋음 | gate control |
| `dibl_mV_V` | 작을수록 좋음 | drain 전계 억제 |
| `cgd_F` | 작을수록 좋음 | Miller/parasitic capacitance, circuit delay와 연결 |
| `cgs_F`, `cgg_F` | 작을수록 유리한 경우 많음 | input/loading capacitance |
| electric field/current density | 제한 조건 | reliability 해석 보조 |

### 3.3 Circuit output

회로 검증의 핵심 output은 FO4 inverter benchmark metric이다.

| Metric | 방향 | 의미 |
|---|---|---|
| `unit_inverter_ok` | true 필요 | NMOS/PMOS 연결 및 switching sanity check |
| `tpHL_s`, `tpLH_s` | 작을수록 좋음 | rising/falling propagation delay |
| `fo4_delay_s` | 작을수록 좋음 | FO4 기준 대표 성능 지표 |
| `output_slew_s` | 작을수록 좋음 | 출력 transition 품질 |
| `average_power_W` | 작을수록 좋음 | 회로 평균 전력 |
| `energy_per_transition_J` | 작을수록 좋음 | switching energy |
| `edp_Js` | 작을수록 좋음 | energy-delay product |

### 3.4 Analysis output

| 분석 | 출력 파일 | 의미 |
|---|---|---|
| Device screening Pareto | `05_results/summary/device_screening_pareto.csv` | 회로 검증 전 후보 축소 |
| Circuit DTCO Pareto | `05_results/summary/circuit_dtco_pareto.csv` | 최종 DTCO 후보군 |
| Robust optimum | `05_results/summary/robust_optimum.csv` | 공정 편차를 고려한 robust 후보 순위 |
| Yield-like pass rate | `05_results/summary/yield_like.csv` | variation sample 중 spec 통과 비율 |
| Figures | `05_results/figures/` | response map, trade-off, Pareto, robust plot |

---

## 4. 우리가 하는 결과 분석

### 4.1 Baseline verification

먼저 baseline symmetric spacer FinFET이 정상적으로 동작하는지 확인한다.

- Id-Vg/Id-Vd 수렴 여부
- NMOS/PMOS polarity 정상 여부
- Ion/Ioff/Vth/SS/DIBL이 비정상적이지 않은지
- Unit inverter switching 가능 여부

이 단계는 제안 구조의 성능 주장을 하기 전 기준점을 고정하는 과정이다.

### 4.2 Device-level screening

초기 DOE와 anchor case 결과를 이용해 소자 수준에서 후보를 줄인다.

목표:

- `ion_A`는 유지 또는 증가
- `ioff_A`, `dibl_mV_V`, `cgd_F`는 감소
- 특히 `cgd_F` 감소가 회로 delay 개선으로 연결되는지 확인

Device Pareto는 최종 결론이 아니라 비싼 회로 simulation 전에 후보를 줄이는 screening이다.

### 4.3 Circuit-level DTCO Pareto

후보를 FO4 inverter benchmark로 검증한 뒤 회로 metric 기준 Pareto를 계산한다.

최종 DTCO Pareto 목적:

- `fo4_delay_s` 최소화
- `average_power_W` 최소화
- `energy_per_transition_J` 최소화
- `edp_Js` 최소화

여기서부터가 프로젝트의 핵심 DTCO 판단이다. 소자 지표가 좋아도 회로 metric이 나쁘면 최종 후보로 주장하지 않는다.

### 4.4 Active DOE

이미 실행한 case로 Gaussian Process(GP) surrogate model을 만들고 추가 실행 후보를 추천한다.

현재 구현은 다음을 사용한다.

- 여러 device/circuit 지표를 하나의 scalarized utility로 결합 (정규화 후 평균)
- RBF kernel GP surrogate, marginal likelihood 기준 length-scale 소규모 grid search
- GP posterior mean/std 기반 UCB(Upper Confidence Bound) acquisition score
- Sobol candidate pool
- fabrication grid snapping

이는 **single-objective Bayesian optimization(GP + UCB)** 이며, numpy/scipy만으로 구현한 dependency-free 버전이다. 보고서에서는 "GP-based single-objective Bayesian optimization (scalarized utility)"이라고 정확히 쓰고, 실제 구현하지 않은 multi-objective BO(MOBO)/NSGA-II/ANN으로 과장해서 표현하지 않는다.

### 4.5 Local refinement

Circuit-level Pareto 후보 주변을 fabrication grid 기준으로 다시 생성하고 재검증한다.

해석 포인트:

- 연속 DOE 후보를 그대로 최종 공정 후보로 주장하지 않는다.
- 0.5 nm grid로 snap한 후보가 성능을 유지하는지 본다.
- 주변 grid에서도 비슷한 성능이 나오면 local robustness가 있다고 설명할 수 있다.

### 4.6 Robust validation

최종 후보 주변 `±0.3 nm`, `±0.5 nm` variation을 넣어 공정 편차에 대한 민감도를 본다.

계산 항목:

- `ion_retention_min_pct`
- `cgd_variation_max_pct`
- `edp_degradation_max_pct`
- `cgd_reduction_retention_min_pct`
- `compensation_min_pct`
- `passes_guardrails`
- `robust_score`

중요한 점은 nominal optimum과 robust optimum이 다를 수 있다는 것이다. 현업 DTCO 관점에서는 nominal에서 제일 빠른 후보보다, variation에서 spec을 더 잘 만족하는 후보가 더 설득력 있다.

### 4.7 Yield-like pass rate

Robust variation sample 각각이 spec을 통과하는지 계산한다.

예시 해석:

```text
Candidate A: nominal EDP는 가장 낮지만 variation sample pass rate = 70%
Candidate B: nominal EDP는 조금 높지만 variation sample pass rate = 95%
```

이 경우 Candidate B가 robust DTCO 후보로 더 적합하다고 해석할 수 있다.

주의:

- 이 값은 실제 fab yield가 아니다.
- 제한된 variation sample에서 정의한 "spec pass rate"다.
- 보고서에는 "yield-like metric" 또는 "variation sample pass rate"로 표현한다.

---

## 5. 결과 해석 방법

### 5.1 좋은 결과로 해석할 수 있는 경우

다음이 함께 보이면 제안 구조가 설득력 있다.

- `Cgd` 감소
- `DIBL` 및 leakage 악화 없음
- `Ion` 손실이 작거나 유지됨
- FO4 delay 감소
- EDP 감소
- robust variation에서 EDP degradation이 작음
- yield-like pass rate가 높음

해석 문장 예시:

> Drain-side low-k composite spacer가 drain-side parasitic capacitance를 줄이면서도 source-side drive current 손실을 제한하여, device-level Cgd 감소가 FO4 inverter delay 및 EDP 개선으로 이어졌다.

### 5.2 조심해서 해석해야 하는 경우

소자 지표만 좋아 보이지만 회로 지표가 나쁠 수 있다.

| 관찰 | 해석 |
|---|---|
| `Ion` 증가, `Cgd` 증가 | 단품 drive는 좋아졌지만 회로 delay/power에서 손해 가능 |
| `Cgd` 감소, `Ion` 큰 폭 감소 | parasitic은 줄었지만 drive current 손실로 delay 개선 제한 |
| nominal EDP 최저, robust pass rate 낮음 | 공정 편차에 취약한 nominal optimum |
| delay 감소, power 증가 | 고성능 후보지만 저전력/EDP 관점에서는 trade-off |
| device Pareto 포함, circuit Pareto 제외 | 소자 screening은 통과했지만 회로 DTCO 후보는 아님 |

### 5.3 최종 후보 선정 논리

최종 후보는 다음 순서로 고른다.

1. Baseline 대비 device metric이 물리적으로 납득 가능한지 확인한다.
2. Unit inverter가 정상 switching하는 후보만 FO4로 보낸다.
3. FO4 기준 `delay`, `power`, `energy`, `EDP` Pareto에 들어오는지 본다.
4. Grid-snapped local refinement 결과에서도 성능이 유지되는지 확인한다.
5. Robust guardrail을 통과하는지 본다.
6. Yield-like pass rate가 높은 후보를 우선한다.

최종 표현은 "최고 성능 후보"와 "robust DTCO optimum"을 구분해서 쓰는 것이 좋다.

```text
Nominal best:
  nominal FO4 delay 또는 EDP가 가장 좋은 후보

Robust DTCO optimum:
  nominal 성능은 약간 낮더라도 variation, guardrail, pass rate까지 고려했을 때 가장 안정적인 후보
```

---

## 6. 보고서/발표에 넣을 핵심 그림

권장 그림 순서는 다음과 같다.

| 순서 | 그림 | 메시지 |
|---|---|---|
| 1 | Baseline vs proposed structure schematic | 무엇을 바꿨는지 |
| 2 | DOE design space scatter | 어떤 입력 공간을 탐색했는지 |
| 3 | `Cgd` 또는 `Ion` response map | spacer 변화가 소자 지표에 미치는 영향 |
| 4 | `Cgd` vs `Ion` trade-off | parasitic 감소와 drive 손실 균형 |
| 5 | Circuit DTCO Pareto plot | 최종 판단은 회로 metric 기준 |
| 6 | FO4 waveform 또는 delay bar | 회로 수준 개선 근거 |
| 7 | Robust EDP degradation plot | 공정 편차에서 얼마나 버티는지 |
| 8 | Yield-like pass rate table/bar | spec 통과율 관점의 후보 비교 |

---

## 7. 발표용 한 문단 요약

본 프로젝트의 input은 source-side spacer length, drain-side spacer length, drain-side low-k width로 정의한 asymmetric composite spacer 설계공간이다. 각 조합은 TCAD process/device simulation을 통해 Ion, Ioff, DIBL, Cgd 같은 소자 metric으로 변환되고, 최종 후보는 unit inverter와 FO4 inverter benchmark에서 delay, power, energy, EDP로 다시 평가된다. 결과 분석은 device-level screening Pareto로 회로 검증 후보를 줄인 뒤, circuit-level DTCO Pareto에서 최종 후보군을 고르고, fabrication grid snapping, local refinement, robust validation, yield-like pass rate를 통해 nominal 성능뿐 아니라 공정 편차에 대한 안정성까지 비교하는 방식으로 수행한다. 따라서 최종 결론은 "가장 좋은 단일 소자 metric"이 아니라 "회로 성능과 robust성까지 고려한 DTCO optimum"으로 해석한다.
