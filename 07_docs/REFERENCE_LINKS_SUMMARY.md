# OASIS-FinFET 핵심 참고문헌 링크 요약

이 파일은 보고서/발표 작성과 연구윤리 확인을 위해 실제로 열어볼 핵심 출처만 따로 정리한 요약본이다. 기존 `references.bib`, `REFERENCES.md`, `SOURCE_MAPPING.csv`를 대체하지 않고, 빠른 확인용 링크 맵으로 사용한다.

## PDF 보관 원칙

- IEEE/Elsevier/IET 등 유료 논문 PDF는 학교 구독 또는 저자 공개본 등 합법 경로에서만 내려받아 개인 연구용으로 보관한다.
- 저작권이 불명확한 PDF는 Git에 올리지 않는다.
- 공개 PDF가 확인된 경우에도 보고서에는 원문 그림/문장을 그대로 복제하지 않고, 직접 재작성한 그림과 요약 문장만 사용한다.
- Git에는 원칙적으로 PDF 원본보다 DOI/공식 링크와 요약을 남긴다.

## 1. 반드시 확인해야 할 직접 중복 선행연구

| ID | 논문/자료 | 링크/PDF 접근 | 프로젝트에서의 의미 | 안전한 사용 |
|---|---|---|---|---|
| R01 | P. K. Pal et al., "Asymmetric Dual-Spacer Trigate FinFET Device-Circuit Codesign and Its Variability Analysis," IEEE TED, 2015. | DOI: https://doi.org/10.1109/TED.2015.2400053 / 저자 업로드 ResearchGate: https://www.researchgate.net/publication/273004101_Asymmetric_Dual-Spacer_Trigate_FinFET_Device-Circuit_Codesign_and_Its_Variability_Analysis | 비대칭 dual-spacer FinFET, device-circuit codesign, variability가 우리 주제와 가장 직접적으로 겹친다. | 구조 자체를 최초라고 주장하지 않는다. 우리 기여는 SOI seed deck 기반 재현, low-k composite 설계공간, 회로 중심 Pareto/robust workflow로 제한해서 설명한다. |
| R02 | P. K. Pal et al., "High-Performance and Robust SRAM Cell Based on Asymmetric Dual-k Spacer FinFETs," IEEE TED, 2013. | DOI: https://doi.org/10.1109/TED.2013.2278201 | asymmetric dual-k spacer를 회로 수준 SRAM 성능 및 robust성과 연결한다. | "spacer 구조를 회로 지표와 연결하는 것"이 이미 선행연구에 있음을 명시한다. |
| R03 | P. K. Pal et al., "Investigation of Symmetric Dual-k Spacer Trigate FinFETs From Delay Perspective," IEEE TED, 2014. | DOI: https://doi.org/10.1109/TED.2014.2351616 | dual-k spacer, fringe capacitance, circuit delay 관계의 핵심 근거다. | Cgd/Miller capacitance와 delay 해석의 선행근거로 인용한다. |
| R04 | P. K. Pal et al., "A Comparative Analysis of Symmetric and Asymmetric Dual-k Spacer FinFETs from Device and Circuit Perspectives," ISQED, 2015. | DOI: https://doi.org/10.1109/ISQED.2015.7085494 | baseline 대칭 spacer와 proposed 비대칭 spacer를 device/circuit 관점에서 비교하는 프레임이 우리 흐름과 겹친다. | 비교 구조와 지표 선정 근거로 인용하되, 그림 구성과 문장 표현은 직접 작성한다. |
| R05 | P. K. Pal et al., "A Detailed Capacitive Analysis of Symmetric and Asymmetric Dual-k FinFETs for Improved Circuit Delay Metrics," ICEDSS, 2016. | DOI: https://doi.org/10.1109/ICEDSS.2016.7587790 / 색인 페이지: https://eurekamag.com/research/107/832/107832931.php | Cgd와 inverter delay를 직접 연결한다. | 회로 검증 자체를 신규성으로 주장하지 않고, 본 연구의 DTCO 평가 지표 근거로 사용한다. |
| R06 | A. Dutta et al., "Physical Insights Into Electric Field Modulation in Dual-k Spacer Asymmetric Underlap FinFET," IEEE TED, 2016. | DOI: https://doi.org/10.1109/TED.2016.2580625 / ResearchGate 정보: https://www.researchgate.net/publication/304365614_Physical_Insights_Into_Electric_Field_Modulation_in_Dual-k_Spacer_Asymmetric_Underlap_FinFET | dual-k spacer가 전계, inversion charge, parasitic capacitance를 어떻게 바꾸는지 설명한다. | 전계 contour와 trade-off 해석의 물리 근거로 인용한다. |
| R07 | K. P. Pradhan et al., "Benefits of Asymmetric Underlap Dual-k Spacer Hybrid Fin Field-Effect Transistor over Bulk Fin Field-Effect Transistor," IET CDS, 2016. | DOI: https://doi.org/10.1049/IET-CDS.2016.0125 | SOI/FinFET 맥락에서 asymmetric underlap dual-k spacer의 장점을 다룬다. | SOI + asymmetric dual-k 조합도 완전 신규가 아님을 명시한다. |

## 2. Spacer 물리, trade-off, 재료 근거

| ID | 논문/자료 | 링크/PDF 접근 | 프로젝트에서의 의미 | 안전한 사용 |
|---|---|---|---|---|
| R08 | A. B. Sachid et al., "Gate Fringe-Induced Barrier Lowering in Underlap FinFET Structures and Its Optimization," IEEE EDL, 2008. | DOI: https://doi.org/10.1109/LED.2007.911974 / IIT Bombay DSpace PDF: https://dspace.library.iitb.ac.in/jspui/handle/10054/8332 | underlap/spacer에서 gate fringe field가 barrier와 Ion/delay에 미치는 영향을 설명한다. | spacer 길이가 무조건 길수록 좋다는 단순 주장을 피하고, trade-off 근거로 쓴다. |
| R09 | V. Bharath Sreenivasulu and V. Narendar, "Performance Improvement of Spacer Engineered n-Type SOI FinFET at 3-nm Gate Length," AEU, 2021. | DOI: https://doi.org/10.1016/j.aeue.2021.153803 | SOI FinFET에서 spacer engineering이 device metric에 미치는 영향 근거다. | SOI spacer engineering 배경과 비교 지표 선정에 사용한다. |
| R10 | N. Huang et al., "Thermal and Electrical Performance Investigation of FinFET with Encased Air-gap Gate Sidewalls...," Microelectronics Journal, 2020. | ScienceDirect: https://www.sciencedirect.com/science/article/pii/S0026269220304456 / DOI: https://doi.org/10.1016/j.mejo.2020.104846 | air-gap/low-k spacer 계열이 전기 및 열 특성에 미치는 영향을 다룬다. | air-gap 확장안을 언급할 때만 제한적으로 사용한다. |
| R11 | T. Yamashita et al., "A Novel ALD SiBCN Low-k Spacer for Parasitic Capacitance Reduction in FinFETs," VLSI Technology, 2015. | DOI: https://doi.org/10.1109/VLSIT.2015.7223659 | 실제 low-k spacer 공정 사례와 parasitic capacitance reduction 근거다. | SiO2를 고급 low-k 신소재처럼 과장하지 않고, low-k spacer 공정 배경으로만 인용한다. |
| R12 | M. Gu et al., "Hybrid Low-k Spacer Scheme for Advanced FinFET Technology Parasitic Capacitance Reduction," Electronics Letters, 2020. | DOI: https://doi.org/10.1049/el.2019.3954 | hybrid low-k spacer로 parasitic capacitance를 줄이는 선행 사례다. | composite/hybrid spacer 자체가 신규라고 쓰지 않는다. |
| R13 | V. B. Sreenivasulu et al., "Spacer Engineering on Multi-channel FinFET for Advanced Wireless Applications," AEU, 2024. | DOI: https://doi.org/10.1016/j.aeue.2024.155298 | 최신 FinFET spacer engineering 동향과 회로/응용 지표 근거다. | 최신 동향 근거로만 사용하고 구조 독창성 주장은 피한다. |

## 3. FinFET/SOI 기초

| ID | 논문/자료 | 링크/PDF 접근 | 프로젝트에서의 의미 | 안전한 사용 |
|---|---|---|---|---|
| R14 | D. Hisamoto et al., "A Fully Depleted Lean-Channel Transistor (DELTA)-A Novel Vertical Ultra Thin SOI MOSFET," IEDM, 1989. | DOI: https://doi.org/10.1109/IEDM.1989.74182 | SOI multi-gate/vertical thin body 계열의 초기 배경이다. | 배경에서 짧게 인용한다. |
| R15 | D. Hisamoto et al., "FinFET-A Self-Aligned Double-Gate MOSFET Scalable to 20 nm," IEEE TED, 2000. | DOI: https://doi.org/10.1109/16.887014 / CiNii 정보: https://cir.nii.ac.jp/crid/1361418521225332736 | FinFET 구조와 short-channel control의 대표 기초문헌이다. | FinFET 구조 설명과 scaling 배경에 인용한다. |

## 4. DOE, Pareto, Robust 최적화 방법

| ID | 논문/자료 | 링크/PDF 접근 | 프로젝트에서의 의미 | 안전한 사용 |
|---|---|---|---|---|
| R16 | M. D. McKay et al., "A Comparison of Three Methods for Selecting Values of Input Variables in the Analysis of Output from a Computer Code," Technometrics, 1979. | DOI: https://doi.org/10.1080/00401706.1979.10489755 / JSTOR stable page may require access: https://www.jstor.org/stable/1268522 | Latin Hypercube Sampling의 고전적 근거다. | DOE case 생성 방법 근거로 인용하고 seed/case list를 공개한다. |
| R17 | K. Deb et al., "A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II," IEEE TEC, 2002. | DOI: https://doi.org/10.1109/4235.996017 | 다목적 Pareto 최적화 방법론의 대표 논문이다. | NSGA-II를 실제 구현하지 않는다면 "NSGA-II 사용"이라고 쓰지 않고, Pareto/non-dominated concept 배경으로만 제한한다. |
| R18 | S. Daulton et al., "Differentiable Expected Hypervolume Improvement for Parallel Multi-Objective Bayesian Optimization," NeurIPS, 2020. | arXiv abstract: https://arxiv.org/abs/2006.05078 / PDF: https://arxiv.org/pdf/2006.05078 | Bayesian multi-objective optimization 확장 근거다. | 현재 코드는 MOBO가 아니므로, 실제 구현 전까지는 참고 후보로만 둔다. |
| R19 | H. Jeong et al., "ML-Driven Optimization of Standard Cell Performance and Timing in Advanced Nodes," JSTS, 2026. | DOI: https://doi.org/10.5573/JSTS.2026.26.2.130 / 색인: https://pure.skku.edu/en/publications/ml-driven-optimization-of-standard-cell-performance-and-timing-in/ | 회로 성능/타이밍 최적화에서 ML surrogate와 multi-objective optimization을 사용하는 최신 배경이다. | 본 프로젝트의 `suggest_active_cases.py`는 ANN/MOBO 구현이 아니므로, 직접 방법론 근거가 아니라 배경/향후 확장으로만 사용한다. |

## 5. TCAD/Sentaurus 공식 자료와 예제 위치

| ID | 자료 | 링크/PDF 접근 | 프로젝트에서의 의미 | 안전한 사용 |
|---|---|---|---|---|
| R23 | Synopsys, "Sentaurus TCAD: Industry-Standard Process and Device Simulators," datasheet. | PDF: https://www.synopsys.com/content/dam/synopsys/silicon/datasheets/sentaurus_ds.pdf | Sentaurus suite가 process/device simulation을 연결한다는 공식 근거다. | 툴 기능 설명에만 사용한다. 학교 PC의 실제 라이선스와 버전은 별도 확인한다. |
| R24 | Synopsys, "Sentaurus Device," official product page. | https://www.synopsys.com/manufacturing/tcad/device-simulation/sentaurus-device.html | Sentaurus Device의 FinFET/FDSOI 및 3D device simulation 지원 근거다. | "Sentaurus가 FinFET/FDSOI를 지원한다"는 공식 근거로 사용한다. |
| R25 | Synopsys, "Sentaurus Workbench," official product page. | https://www.synopsys.com/manufacturing/tcad/framework.html | parameterization, project execution, result management의 공식 근거다. | 학교 설치본에서 실제 사용 가능 여부를 확인한 뒤 사용한다. |
| R26 | Sentaurus Training Application Index, FinFET examples. | https://ghzphy.github.io/Sentaurus_Training/search/app_index.html | `Applications_Library/FinFET/FinFET_10nm`, `FinFET_14nm`, `FinFET_22nm`, `GettingStarted/sde/FinFET` 등 seed deck 후보가 실제로 있음을 확인하는 근거다. | 공개 training index는 위치 확인용으로 사용하고, 실제 deck은 학교 라이선스/설치본에서 합법적으로 사용한다. |
| R27 | Sentaurus TCAD-to-SPICE training. | https://ghzphy.github.io/Sentaurus_Training/tcadtospice/t2s_01.html | TCAD 결과를 SPICE/회로 평가와 연결하는 flow의 배경 자료다. | 실제 본 프로젝트에서 compact/SPICE 연결을 구현한 범위만큼만 언급한다. |

## 6. 보고서에서 특히 조심할 문장

쓰면 안 되는 표현:

- "비대칭 dual-k/composite spacer FinFET을 최초로 제안하였다."
- "spacer engineering과 circuit delay를 최초로 연결하였다."
- "robust/variability analysis를 최초로 수행하였다."
- "SiO2 low-k spacer가 기존에 없던 신공정이다."
- "ANN/MOBO/NSGA-II 기반 최적화를 구현하였다." 단, 실제 구현 및 검증한 경우는 제외한다.
- "TCAD 결과를 실제 fabrication 또는 실측 결과로 검증하였다."

권장 표현:

- "선행연구의 asymmetric/dual-k spacer FinFET 흐름을 바탕으로, 본 프로젝트는 SOI FinFET seed deck에서 drain-side low-k composite spacer 설계공간을 정의하고 TCAD 기반 device-circuit 평가 및 robust optimum workflow를 구축한다."
- "구조 자체의 최초성보다, 동일한 평가 흐름에서 `L_sp_S`, `L_sp_D`, `W_low_k`의 trade-off, 회로 성능 feedback, 공정 편차 방어율을 정량화하는 데 초점을 둔다."
- "Pareto 후보 선정은 회로 성능 지표를 중심으로 하되, Ion/Ioff/DIBL/Cgd는 device-level guardrail과 물리 해석 근거로 사용한다."
- "제한된 TCAD 실행 예산 안에서 lightweight surrogate-assisted active DOE를 사용하여 추가 후보를 추천하였다."

## 7. 현재 프로젝트에서 직접 써야 할 최소 인용 세트

보고서가 너무 길어지지 않는다면 최소 아래는 포함하는 것을 권장한다.

1. R01: 비대칭 dual-spacer + device-circuit codesign + variability 직접 중복 선행연구
2. R03 또는 R05: spacer capacitance와 circuit delay 연결 근거
3. R06 또는 R08: electric field / underlap / spacer trade-off 물리 근거
4. R12 또는 R11: hybrid/low-k spacer 공정 및 capacitance reduction 근거
5. R15: FinFET 기본 구조 배경
6. R16: DOE/LHS 근거
7. R24 또는 R26: Sentaurus FinFET/3D TCAD 지원 및 seed example 근거
