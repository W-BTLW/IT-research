# Oracle SQL 성능 측정 방법

## 1. SQL 성능 측정이란?

SQL 실행 시 얼마나 빠르게 처리되는지, DB 자원을 얼마나 사용하는지 확인하는 작업.

| 항목 | 의미 |
|---|---|
| Elapsed Time | SQL 실행에 걸린 시간 |
| Buffers | 메모리에서 접근한 블록 수(논리적 읽기) |
| Reads | 디스크에서 읽은 블록 수(물리적 읽기) |
| A-Rows | 실제 처리한 행 수 |
| E-Rows | 옵티마이저가 예상한 행 수 |
| Execution Plan | SQL 실행계획 |

**핵심: 실행시간 + Buffers + 실행계획을 함께 확인!**

---

## 2. SQL 성능 측정 방법

### STEP 1. 실행 통계 활성화

```sql
ALTER SESSION SET statistics_level = ALL;
```

### STEP 2. 측정할 SQL 실행

```sql
SELECT /*+ gather_plan_statistics */
       *
FROM TEST_LARGE
WHERE SEND_DT >= '20250101'
  AND SEND_DT < '20260101';
```

### STEP 3. 실제 실행계획 조회

```sql
SELECT *
FROM TABLE(
    DBMS_XPLAN.DISPLAY_CURSOR(
        NULL,
        NULL,
        'ALLSTATS LAST +PREDICATE'
    )
);
```

※ 동일 세션에서 STEP 2와 STEP 3을 연속 실행.

※ 다른 SQL이 끼어들면 SQL_ID를 직접 지정.

※ 실행계획 조회 시 관련 권한이 필요할 수 있음.

---

## 3. 실행계획 확인 포인트

| 항목 | 확인할 내용 |
|---|---|
| A-Time | 실제 수행시간 |
| Buffers | 논리적 블록 접근량 |
| Reads | 디스크 읽기량 |
| A-Rows | 실제 처리 건수 |
| E-Rows | 예상 처리 건수 |
| Operation | Full Scan, Index Scan 등 |

### 중요 포인트

- Buffers가 적을수록 일반적으로 효율적
- A-Rows와 E-Rows 차이가 크면 통계정보 확인
- Full Scan이 무조건 나쁜 것은 아님
- 인덱스 사용이 무조건 빠른 것도 아님

---

## 4. SQL 튜닝 전후 비교 예시

| 구분 | 튜닝 전 | 튜닝 후 |
|---|---:|---:|
| 실행시간 | 5.2초 | 0.8초 |
| Buffers | 150,000 | 8,000 |
| Reads | 12,000 | 300 |
| 실행계획 | Full Scan | Index Range Scan |

※ 위 수치는 예시이며 실제 측정값이 아님.

### 튜닝 성공 기준

1. SQL 결과가 동일한가?
2. 실행시간이 감소했는가?
3. Buffers / Reads가 감소했는가?
4. 불필요한 연산이 줄었는가?

---

## 5. 실무 체크리스트

- [ ] 튜닝 전후 조회 결과 동일
- [ ] 실행시간 비교
- [ ] Buffers 비교
- [ ] Reads 비교
- [ ] 실행계획 확인
- [ ] 인덱스 사용 여부 확인
- [ ] 동일한 데이터와 조건에서 여러 번 측정

---

## 핵심 3줄 요약

1. **Elapsed Time** → SQL 실행속도
2. **Buffers / Reads** → DB 자원 사용량
3. **Execution Plan** → SQL 처리 방식

**결론: 동일한 결과를 더 빠르고 적은 자원으로 처리하는 것이 SQL 튜닝의 목표다.**
