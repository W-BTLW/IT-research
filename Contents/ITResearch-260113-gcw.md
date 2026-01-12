# Oracle SQL Hard Parse

Oracle Database에서 SQL 성능을 이야기할 때 가장 먼저 점검해야 하는 영역 중 하나가 **Hard Parse**이다.  
Hard Parse는 SQL 실행 이전 단계에서 수행되는 고비용 작업으로, OLTP 환경에서는 DB CPU 병목과 장애의 직접적인 원인이 되기도 한다.


## 1. SQL 실행 흐름에서 Hard Parse의 위치

<img width="338" height="558" alt="image" src="https://github.com/user-attachments/assets/24511a0e-65af-4c3b-80ce-9566f842c09c" />


Oracle에서 SQL은 다음과 같은 단계를 거쳐 실행된다.

1. **Parse**
2. Execute
3. Fetch

이 중 **Hard Parse는 Parse 단계에서 발생하는 가장 무거운 작업**이다.  
SQL이 처음 들어오거나, 기존 실행 정보를 재사용할 수 없는 경우 수행된다.

> **Hard Parse가 실행 이전 단계에 위치하며, 모든 실행의 출발점**이다.

---

## 2. Hard Parse란 무엇인가

Hard Parse는 Oracle이 SQL을 처음 인식했을 때 수행하는 **완전한 분석 및 최적화 과정**이다.

Hard Parse가 발생하면 Oracle은 다음 작업을 수행한다.

- SQL 문장 분석
- 객체 및 권한 확인
- 통계 정보 조회
- 실행계획 후보 생성
- 비용(Cost) 계산
- 최적 실행계획 선택
- Shared Pool에 커서(Cursor) 캐시

이 과정은 단순 문자열 비교 수준이 아니라 **옵티마이저(Cost-Based Optimizer)가 깊게 개입하는 CPU 집약적 작업**이다.

---

## 3. Hard Parse 내부 처리 단계

Hard Parse 단계에서 Oracle은 내부적으로 아래와 같은 절차를 수행한다.

---

### 3.1 SQL 문법 체크 (Syntax Check)
- SQL 문장이 Oracle 문법에 맞는지 검사
- 토큰화(Tokenizing) 및 파스 트리(Parse Tree) 생성
- 문법 오류는 이 단계에서 즉시 실패

> 문법 오류는 실행 단계로 넘어가지 않으며 Hard Parse 단계에서 바로 반환된다.

---

### 3.2 객체 및 권한 확인 (Semantic Check)
- 참조하는 테이블, 컬럼, 인덱스, 뷰 존재 여부 확인
- 사용자 권한 검증
- 동의어(Synonym), 뷰(View) 확장 처리

> 문법이 맞더라도 **객체가 없거나 권한이 없으면 Hard Parse 단계에서 실패**한다.

---

### 3.3 통계 정보 조회 (Statistics Lookup)

옵티마이저는 실행계획을 선택하기 위해 다양한 통계 정보를 참조한다.

- 테이블 통계  
  - 총 행 수, 블록 수
- 컬럼 통계  
  - NDV(고유값 개수), NULL 비율
- 인덱스 통계  
  - Leaf Blocks, Clustering Factor
- 히스토그램 (선택)
- 옵티마이저 관련 파라미터

> 통계 정보는 **실행계획의 품질과 Hard Parse 비용에 직접적인 영향을 준다.**

---

### 3.4 후보 실행계획 생성 (Plan Enumeration)

옵티마이저는 가능한 실행 전략을 조합하여  
**복수의 실행계획 후보**를 생성한다.

예:
- 접근 경로  
  - Index Scan / Full Table Scan
- 조인 방식  
  - Nested Loop / Hash Join / Sort Merge Join
- 조인 순서 변경
- 파티션 프루닝 여부
- 병렬 실행 가능성

---

### 3.5 Cost 계산 (Costing)

<img width="1024" height="522" alt="image" src="https://github.com/user-attachments/assets/41bc5d71-5b2a-4c98-bceb-04670d949b9c" />


각 실행계획 후보에 대해 비용을 계산한다.

- 예상 논리 I/O
- 예상 물리 I/O
- CPU 사용량
- 카디널리티(Cardinality) 추정
- 선택도(Selectivity) 추정

Oracle은 **비용이 가장 낮다고 판단되는 실행계획**을 선택한다.

---

### 3.6 최적 실행계획 선택

- Cost 기반으로 최종 실행계획 결정
- 해당 계획은 SQL 실행의 “설계도” 역할을 수행한다

---

### 3.7 Shared Pool에 커서 캐시

- 선택된 실행계획은 **Cursor 형태로 Shared Pool에 저장**
- Shared Pool 내부의 **Library Cache 영역**에 위치
- 이후 동일 SQL이 들어오면 재사용 가능

> Hard Parse는 **Cursor가 Shared Pool에 적재되는 시점에 완료**된다.

---

### 3.8 Cursor란 무엇인가 (Hard Parse 관점)

Cursor는 Oracle이 SQL을 처리하기 위해 내부적으로 생성하는 **실행 단위 객체**이다.  
Hard Parse 과정의 최종 결과물은 단순한 실행계획이 아니라, **실행계획을 포함한 Cursor 생성**이다.

즉, Hard Parse는 다음 질문에 대한 Oracle의 답을 만드는 과정이다.

> “이 SQL을 **어떤 방식으로**, **어디서**, **어떤 순서로** 실행할 것인가?”

그 답변이 Cursor 형태로 Shared Pool에 저장된다.

#### Cursor에 포함되는 주요 정보

하나의 Cursor에는 다음과 같은 정보들이 함께 묶여 있다.

- SQL 텍스트
- 파싱 결과(Parse Tree)
- 실행계획(Execution Plan)
- 옵티마이저 관련 환경 정보
- 객체/권한 메타데이터
- 바인드 변수 메타정보
- Child Cursor 식별 정보

따라서 Cursor는 단순한 “계획”이 아니라 **SQL 실행을 위한 모든 판단 결과의 집합체**라고 볼 수 있다.


---

## 4. 왜 Hard Parse가 DB CPU 병목의 주범이 되는가

<img width="666" height="527" alt="image" src="https://github.com/user-attachments/assets/5ac98131-2a8d-490f-827e-78bcdd0aaee4" />

Hard Parse는 다음 이유로 시스템 전체에 부담을 준다.

### 4.1 CPU 집약적 작업
- 옵티마이저가 다수의 후보 실행계획을 계산
- SQL 수가 많을수록 CPU 사용량 급증

### 4.2 Shared Pool 경합
- 다수 세션이 동시에 Hard Parse 수행
- Library Cache 보호를 위한 락/래치 경합 발생
- 결과:
  - 대기 시간 증가
  - 처리량 감소
  - DB 전체 성능 급락

### 4.3 커서 폭증 문제
- SQL 문자열이 계속 달라질 경우
- 커서가 과도하게 생성
- Shared Pool 압박 → 커서 Aging Out → 재 Hard Parse 발생

---

## 한 줄 결론

> Hard Parse는 **“SQL을 실행하는 비용”이 아니라 “SQL을 실행하기 위해 판단하는 비용”이다.**
