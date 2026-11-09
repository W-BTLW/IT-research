# Oracle SQL 심화 문법

> **주요 문법:** `WITH`, 재귀 쿼리, `CONNECT BY`, 윈도우 함수, `EXISTS`, `MERGE`, `CASE WHEN`  
> **기준:** Oracle SQL. Tibero는 버전별 지원 문법 확인 필요.

---

## 1. WITH — 복잡한 SQL을 나누어 작성하기

`WITH`(CTE)는 **쿼리 안에서 이름을 붙인 중간 결과**를 정의하는 문법이다. 여러 단계의 집계나 서브쿼리를 읽기 쉽게 분리할 때 활용한다.

```sql
WITH DEPT_AVG AS (
    SELECT DEPT_ID, AVG(SALARY) AS AVG_SALARY
    FROM EMPLOYEE
    GROUP BY DEPT_ID
)
SELECT E.EMP_NAME, E.SALARY, D.AVG_SALARY
FROM EMPLOYEE E
JOIN DEPT_AVG D ON E.DEPT_ID = D.DEPT_ID
WHERE E.SALARY > D.AVG_SALARY;
```

**결과:** 본인 부서 평균보다 급여가 높은 직원 조회.

- **장점:** 복잡한 로직 분리, 가독성 향상, 같은 중간 결과 재참조
- **주의:** `WITH` 사용 자체가 성능 향상을 보장하지는 않는다. 실행 계획 확인 필요

---

## 2. 재귀 쿼리 — 하위 데이터를 반복해서 찾기

재귀 쿼리는 **이전 조회 결과를 다시 참조해 다음 계층을 찾는 방식**이다. 메뉴 트리, 조직도, 댓글 구조처럼 계층의 깊이가 정해져 있지 않을 때 사용한다.

### 예제: 메뉴 구조

| MENU_ID | MENU_NAME | PARENT_ID |
|---:|---|---:|
| 1 | 관리자 | NULL |
| 2 | 사용자 관리 | 1 |
| 3 | 시스템 관리 | 1 |
| 4 | 권한 관리 | 2 |
| 5 | 공통코드 관리 | 3 |

```text
관리자(1)
├─ 사용자 관리(2)
│  └─ 권한 관리(4)
└─ 시스템 관리(3)
   └─ 공통코드 관리(5)
```

### Oracle 재귀 WITH

```sql
WITH MENU_TREE (MENU_ID, MENU_NAME, PARENT_ID, DEPTH) AS (
    -- 시작점(Anchor)
    SELECT MENU_ID, MENU_NAME, PARENT_ID, 1
    FROM MENU
    WHERE MENU_ID = 1

    UNION ALL

    -- 이전 결과의 자식 조회(Recursive)
    SELECT M.MENU_ID, M.MENU_NAME, M.PARENT_ID, T.DEPTH + 1
    FROM MENU M
    JOIN MENU_TREE T ON M.PARENT_ID = T.MENU_ID
)
SELECT MENU_ID, MENU_NAME, DEPTH
FROM MENU_TREE
ORDER BY DEPTH, MENU_ID;
```

| MENU_NAME | DEPTH |
|---|---:|
| 관리자 | 1 |
| 사용자 관리 | 2 |
| 시스템 관리 | 2 |
| 권한 관리 | 3 |
| 공통코드 관리 | 3 |

**실행 원리**

```text
Anchor: 관리자
   ↓
1차: 사용자 관리, 시스템 관리
   ↓
2차: 권한 관리, 공통코드 관리
   ↓
더 이상 자식이 없으면 종료
```

**기억할 점:** `Anchor`는 시작 데이터, `UNION ALL` 아래는 반복할 쿼리이다. Oracle은 `WITH RECURSIVE`가 아니라 **자기 참조 `WITH`**를 사용한다. 순환 참조가 가능하다면 `CYCLE` 처리도 고려한다.

---

## 3. CONNECT BY — Oracle의 계층형 조회

Oracle에서는 재귀 `WITH` 대신 `START WITH ... CONNECT BY`로 계층을 간결하게 조회할 수 있다.

```sql
SELECT
    MENU_NAME,
    LEVEL AS DEPTH,
    SYS_CONNECT_BY_PATH(MENU_NAME, ' > ') AS MENU_PATH
FROM MENU
START WITH MENU_ID = 1
CONNECT BY NOCYCLE PRIOR MENU_ID = PARENT_ID
ORDER SIBLINGS BY MENU_ID;
```

| 구문 | 의미 |
|---|---|
| `START WITH` | 탐색 시작점 |
| `CONNECT BY PRIOR` | 부모·자식 연결 조건 |
| `LEVEL` | 계층 깊이(루트 1) |
| `SYS_CONNECT_BY_PATH` | 루트부터 현재 행까지 경로 |
| `NOCYCLE` | 순환 참조 방지 |
| `ORDER SIBLINGS BY` | 같은 부모 아래 형제 정렬 |

`PRIOR MENU_ID = PARENT_ID`는 **부모의 ID = 자식의 부모 ID**를 뜻한다.

예를 들어 `권한 관리`의 경로는 `> 관리자 > 사용자 관리 > 권한 관리`로 표현된다. `ORDER SIBLINGS BY`를 쓰면 계층 구조를 유지한 채 형제 메뉴를 정렬할 수 있다.

**차이:** 재귀 `WITH`는 일반적인 반복 탐색에도 활용 가능하고, `CONNECT BY`는 Oracle 계층형 데이터에 특화되어 있다.

---

## 4. 윈도우 함수 — 원본 행을 유지한 채 순위·집계

`GROUP BY`는 행을 그룹별로 합치지만, **윈도우 함수는 각 행을 유지**하면서 순위·누적합·이전 행 값을 계산할 수 있다.

### 예제: 부서별 급여 순위

```sql
SELECT
    DEPT_ID, EMP_NAME, SALARY,
    RANK() OVER (
        PARTITION BY DEPT_ID
        ORDER BY SALARY DESC
    ) AS SALARY_RANK
FROM EMPLOYEE;
```

- `PARTITION BY`: 계산 그룹(부서)
- `ORDER BY`: 그룹 내 정렬 기준

### 순위 함수 비교

급여가 `500, 400, 400, 300`이라면:

| 급여 | RANK | DENSE_RANK | ROW_NUMBER |
|---:|---:|---:|---:|
| 500 | 1 | 1 | 1 |
| 400 | 2 | 2 | 2 또는 3 |
| 400 | 2 | 2 | 2 또는 3 |
| 300 | 4 | 3 | 4 |

- `RANK`: 동점 다음 순위를 건너뜀
- `DENSE_RANK`: 동점 다음 순위를 건너뛰지 않음
- `ROW_NUMBER`: 모든 행에 고유 번호 부여

### 실무 예제: 부서별 상위 3명

```sql
WITH RANKED AS (
    SELECT E.*,
           ROW_NUMBER() OVER (
               PARTITION BY DEPT_ID
               ORDER BY SALARY DESC, EMP_ID
           ) AS RN
    FROM EMPLOYEE E
)
SELECT DEPT_ID, EMP_NAME, SALARY
FROM RANKED
WHERE RN <= 3;
```

**왜 WITH로 감쌀까?** 같은 SELECT 블록의 `WHERE`에서는 계산한 윈도우 함수 결과를 직접 필터링할 수 없기 때문이다.

### 이전 행과 비교하기

```sql
SELECT
    EMP_ID, SALARY,
    LAG(SALARY) OVER (ORDER BY EMP_ID) AS PREV_SALARY
FROM EMPLOYEE;
```

`LAG()`는 정렬 순서상 **이전 행의 값**을 가져온다. 반대로 `LEAD()`는 다음 행을 가져오며, `SUM() OVER(ORDER BY ...)`는 누적합 계산에 사용할 수 있다. 거래 이력의 직전 상태 비교나 날짜별 실적 증감 분석에 유용하다.

---

## 5. EXISTS / NOT EXISTS — 데이터 존재 여부 확인

`EXISTS`는 관련 행이 **하나라도 존재하는지**, `NOT EXISTS`는 **하나도 없는지** 판단한다.

### 예제: 작업이 하나도 없는 프로젝트

```sql
SELECT P.PROJECT_ID, P.PROJECT_NAME
FROM PROJECT P
WHERE NOT EXISTS (
    SELECT 1
    FROM PROJECT_TASK T
    WHERE T.PROJECT_ID = P.PROJECT_ID
);
```

`NOT EXISTS`를 `EXISTS`로 바꾸면 **작업이 있는 프로젝트**를 찾는다.

| 비교 | JOIN | EXISTS |
|---|---|---|
| 목적 | 연결된 데이터 조회 | 연결된 데이터 존재 확인 |
| 1:N 연결 | 부모 행이 중복될 수 있음 | 부모 행 중복 없이 조건 판단 |

**주의:** `NOT IN`은 하위 조회 결과에 `NULL`이 있으면 예상과 다른 결과가 발생할 수 있다. 미존재 조건은 `NOT EXISTS`를 우선 고려할 만하다.

---

## 6. MERGE — 있으면 UPDATE, 없으면 INSERT

`MERGE`는 **대상에 데이터가 있는지에 따라 수정 또는 등록**하는 문법이다. 기준정보 동기화나 배치 데이터 적재에 유용하다.

```sql
MERGE INTO EMPLOYEE E
USING (
    SELECT 101 AS EMP_ID,
           '김개발' AS EMP_NAME,
           5000 AS SALARY
    FROM DUAL
) S
ON (E.EMP_ID = S.EMP_ID)
WHEN MATCHED THEN
    UPDATE SET E.EMP_NAME = S.EMP_NAME,
               E.SALARY = S.SALARY
WHEN NOT MATCHED THEN
    INSERT (EMP_ID, EMP_NAME, SALARY)
    VALUES (S.EMP_ID, S.EMP_NAME, S.SALARY);
```

```text
EMP_ID = 101 존재?
├─ YES → UPDATE
└─ NO  → INSERT
```

**주의사항**

- `ON` 조건은 대상 행을 정확히 식별해야 한다.
- 소스에 동일 키가 중복되면 오류가 발생할 수 있다.
- `MERGE`만으로 동시성 문제까지 해결되지는 않는다. 고유 제약조건과 트랜잭션 관리도 필요하다.

---

## 7. CASE WHEN — 조건별 분류와 집계

`CASE WHEN`은 SQL 안에서 조건에 따라 다른 값을 만드는 표현식이다.

```sql
SELECT
    EMP_NAME,
    CASE
        WHEN SALARY >= 5000 THEN '상'
        WHEN SALARY >= 3000 THEN '중'
        ELSE '하'
    END AS SALARY_GRADE
FROM EMPLOYEE;
```

### 실무 예제: 배치 성공·실패 건수 집계

```sql
SELECT
    COUNT(*) AS TOTAL_CNT,
    SUM(CASE WHEN STATUS = 'SUCCESS' THEN 1 ELSE 0 END) AS SUCCESS_CNT,
    SUM(CASE WHEN STATUS = 'FAIL' THEN 1 ELSE 0 END) AS FAIL_CNT
FROM BATCH_HISTORY;
```

| TOTAL_CNT | SUCCESS_CNT | FAIL_CNT |
|---:|---:|---:|
| 100 | 92 | 8 |

**활용:** 배치 결과 대시보드, 거래 상태 통계, 코드별 분류. 위 결과는 예시이며 다른 상태가 존재하면 합계가 전체 건수와 다를 수 있다.

---

## 8. 상황별 문법 선택

| 실무 요구사항 | 문법 |
|---|---|
| 복잡한 서브쿼리 정리 | `WITH` |
| 조직도·메뉴의 하위 항목 조회 | 재귀 `WITH` / `CONNECT BY` |
| 그룹별 상위 N건, 이전 값 비교 | `ROW_NUMBER`, `LAG` |
| 관련 데이터가 없는 행 조회 | `NOT EXISTS` |
| 기존 데이터 수정 및 신규 등록 | `MERGE` |
| 상태별 건수 통계 | `SUM(CASE WHEN ...)` |

**추가로 기억하면 좋은 차이**

- `UNION`: 결과 합치기 + 중복 제거 / `UNION ALL`: 중복 유지
- `GROUP BY`: 그룹별로 행 축약 / `OVER(...)`: 행을 유지하며 계산
- **SQL의 길이와 성능은 비례하지 않는다.** 인덱스, 실행 계획, 처리 건수 확인이 중요하다.

**실무 체크 포인트:** 조건에 맞는 결과를 반환하는지 확인한 후, 대량 데이터에서도 동일하게 작동하는지 검증한다. `ROW_NUMBER()`에는 동점 시 순서를 고정할 기준을 두고, 재귀 쿼리에는 순환 데이터 가능성을 점검하며, `MERGE`에는 키 중복 여부를 확인하는 것이 좋다.

---

## 9. 핵심 정리 및 예상 질문

**Q. 재귀 쿼리는 언제 쓰나요?**  
A. 이전 결과를 참조하면서 깊이가 일정하지 않은 조직도·메뉴 트리 등을 탐색할 때 사용합니다.

**Q. `WITH`를 사용하면 무조건 빨라지나요?**  
A. 아닙니다. 주된 장점은 가독성이며, 성능은 실행 계획을 확인해야 합니다.

**Q. `RANK`와 `ROW_NUMBER`의 차이는?**  
A. `RANK`는 동점에 같은 순위를 주고, `ROW_NUMBER`는 모든 행에 서로 다른 번호를 부여합니다.

**Q. `JOIN` 대신 `EXISTS`를 쓰는 이유는?**  
A. 연결된 행의 값이 아닌 존재 여부만 필요할 때 적합하며, 1:N JOIN으로 인한 중복도 피할 수 있습니다.

**Q. `MERGE`를 쓰면 무엇이 편해지나요?**  
A. 데이터 존재 여부에 따라 INSERT/UPDATE를 분기하는 처리를 하나의 SQL문으로 표현할 수 있습니다.


