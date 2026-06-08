# CLOB vs BLOB vs String

## 1. 왜 이걸 알아야 할까?

DB에 데이터를 저장할 때 `VARCHAR`로 다 때우다가 아래같은 상황을 만날 때가 있음.

- 게시글 본문이 길어서 **잘리거나** 저장 오류가 남
- 이미지/파일을 DB에 넣으려니 **타입을 모르겠음**
- ORM 쓰다가 **CLOB 타입 매핑 오류** 발생

→ CLOB, BLOB, String(VARCHAR)의 차이를 제대로 알면 이런 문제를 예방할 수 있음.

---

## 2. 핵심 개념 한눈에 보기

| 구분 | **String (VARCHAR)** | **CLOB** | **BLOB** |
|------|----------------------|----------|----------|
| 풀네임 | Character Varying | Character Large Object | Binary Large Object |
| 데이터 종류 | 짧은 문자열 | **대용량 텍스트** | **대용량 이진 데이터** |
| 저장 방식 | 인라인 (행 내부) | 별도 세그먼트 (포인터 참조) | 별도 세그먼트 (포인터 참조) |
| 최대 크기 | 4,000 ~ 65,535 bytes | 수 GB ~ TB | 수 GB ~ TB |
| 검색 가능 여부 | ✅ 인덱싱 가능 | ⚠️ 제한적 (Full-text) | ❌ 불가 |
| 인코딩 | 문자셋 적용 | 문자셋 적용 | 없음 (Raw bytes) |

> 💡 **한 줄 요약**  
> - `String` = 짧고 자주 쓰는 텍스트  
> - `CLOB` = 긴 텍스트 문서  
> - `BLOB` = 이미지, 파일, 바이너리

---
 

## 3. CLOB 검색이 "제한적"인 이유

CLOB은 데이터가 행(Row) 밖 별도 공간에 저장되기 때문에 일반 `VARCHAR`처럼 인덱스를 걸 수 없음.
그래서 아래 같은 일반 검색은 **풀스캔이 발생**하거나 아예 지원 안 됨.

```sql
-- ❌ CLOB 컬럼에 이런 거 쓰면 안 됨 (풀스캔 발생)
WHERE content LIKE '%키워드%'
```

대신 DB 전용 **전문 검색(Full-text Search)** 기능을 따로 써야 함.

```sql
-- Oracle / Tibero: Oracle Text 방식
WHERE CONTAINS(content, '키워드') > 0

-- MySQL: FULLTEXT INDEX 생성 후 사용
WHERE MATCH(content) AGAINST('키워드')
```

즉 "검색 못 하는 건 아닌데, 일반 인덱스는 안 되고 전용 기능 써야 함" → **제한적**이라고 표현한 것임.

---

## 4. 각 타입 상세 설명

### 4-1. String / VARCHAR

```sql
name    VARCHAR(100)  -- 최대 100자
email   VARCHAR(255)
status  CHAR(1)       -- 고정 길이
```

- 행(Row) 안에 **직접 저장**되므로 조회 속도가 가장 빠름
- `WHERE`, `LIKE`, `INDEX` 모두 자유롭게 사용 가능

| DB | VARCHAR 최대 | 비고 |
|----|-------------|------|
| MySQL | 65,535 bytes | Row 전체 크기 기준 |
| Oracle | 4,000 bytes | `MAX_STRING_SIZE=EXTENDED` 시 32,767 bytes |
| PostgreSQL | 제한 없음 | `text` 타입 권장 |
| **Tibero** | **4,000 bytes** | Oracle 호환, 동일하게 적용됨 |

- **제한을 넘으면?** → 오류 or 자동 잘림 발생

---

### 4-2. CLOB (Character Large Object)

```sql
-- Oracle
content  CLOB

-- MySQL
content  LONGTEXT  -- MySQL에서는 LONGTEXT = CLOB 역할

-- PostgreSQL
content  TEXT

```

- 행 외부의 **별도 저장 공간**에 저장, 행에는 **포인터**만 남김
- 일반 텍스트와 동일하게 **문자 인코딩(UTF-8 등) 적용**
- 수 GB의 텍스트 저장 가능
- 검색은 `CONTAINS()`, `LIKE` 등 Full-text 방식으로 제한적 지원
	⁃	Tibero는 Oracle과 동일하게 `CLOB` 타입 사용

**실무 사용 예시:**

- 게시판 본문, 블로그 포스트
- 계약서·약관 전체 텍스트
- 이메일 본문
- JSON/XML 대용량 데이터
- 로그 데이터

---

### 3-3. BLOB (Binary Large Object)

```sql
-- Oracle / Tibero
file_data  BLOB

-- MySQL
file_data  LONGBLOB    -- 최대 4GB

-- PostgreSQL
file_data  BYTEA
```

- 텍스트가 아닌 **이진(Binary) 데이터** 저장
- 인코딩 개념 없음 → 파일 그대로 byte 단위 저장
- 이미지, 영상, PDF, 압축파일 등 저장 가능
- 검색, 정렬 불가 → 식별자(ID)로만 참조

**실무 사용 예시:**

- 프로필 이미지 (소규모 서비스)
- 첨부파일 저장
- 암호화된 데이터
- 인증서 (`.cer`, `.pem`)
- 음성 메모, 서명 이미지

---

## 5. 공통점

- 셋 다 DB의 **컬럼 타입**으로 사용
- 모두 **NULL 허용** 가능
- ORM(JPA, SQLAlchemy 등)에서 **타입 매핑** 필요
- **트랜잭션** 내에서 일관성 보장
- CLOB / BLOB은 **스트리밍 방식**으로 읽기/쓰기 지원 (메모리 효율)

---

## 6. 실무에서의 선택 기준

```
데이터가 텍스트인가?
  ├── YES → 몇 자나 되는가?
  │         ├── 수백 자 이내 → VARCHAR / String
  │         └── 수천 자 이상 → CLOB (LONGTEXT, TEXT)
  └── NO  → 이진 파일인가?
             └── YES → BLOB (LONGBLOB, BYTEA)
```

 

### 실무 팁: BLOB vs 파일 서버

| | **BLOB (DB 저장)** | **파일 서버 (S3 등)** |
|--|----|----|
| 장점 | 트랜잭션 일관성, 백업 용이 | 성능 우수, 비용 저렴 |
| 단점 | DB 부하 증가, 용량 폭증 | 별도 관리 포인트 |
| 적합한 경우 | 소규모, 보안 민감 파일 | 대규모 미디어 서비스 |

> 💡 **현업 권장**: 파일은 S3/GCS 같은 스토리지에 저장하고,  
> DB에는 **URL 문자열(VARCHAR)** 만 저장하는 패턴을 주로 사용


---

## 7. 코드로 보는 실제 사용법

### Java / JPA

```java

@Entity
public class Article {
    @Id
    private Long id;

    @Column(length = 255)
    private String title;          // VARCHAR

    @Lob
    @Column(columnDefinition = "CLOB")
    private String content;        // CLOB - @Lob 어노테이션 필수

    @Lob
    @Column(columnDefinition = "BLOB")
    private byte[] thumbnail;      // BLOB
}

```
> `@Lob` 빠뜨리면 Hibernate가 VARCHAR로 매핑해버려서 저장 오류 남. 필수임.
 

### Java / MyBatis

MyBatis는 XML Mapper에서 `jdbcType`을 명시해줘야 정상적으로 동작함.

**Mapper XML**

```xml
<!-- 조회 resultMap -->
<resultMap id="articleResultMap" type="Article">
    <id     property="id"        column="id" />
    <result property="title"     column="title"     jdbcType="VARCHAR" />
    <result property="content"   column="content"   jdbcType="CLOB"
            typeHandler="org.apache.ibatis.type.ClobTypeHandler" />
    <result property="thumbnail" column="thumbnail" jdbcType="BLOB"
            typeHandler="org.apache.ibatis.type.BlobTypeHandler" />
</resultMap>

<!-- 등록 INSERT -->
<insert id="insertArticle" parameterType="Article">
    INSERT INTO article (id, title, content, thumbnail)
    VALUES (
        #{id},
        #{title,        jdbcType=VARCHAR},
        #{content,      jdbcType=CLOB},
        #{thumbnail,    jdbcType=BLOB}
    )
</insert>

<!-- 조회 SELECT -->
<select id="selectArticle" resultMap="articleResultMap">
    SELECT id, title, content, thumbnail
    FROM article
    WHERE id = #{id}
</select>

```

 

**VO 클래스**

```java

public class Article {
    private Long   id;
    private String title;      // VARCHAR
    private String content;    // CLOB  → MyBatis ClobTypeHandler가 String으로 변환해줌
    private byte[] thumbnail;  // BLOB  → MyBatis BlobTypeHandler가 byte[]로 변환해줌
}

```

---


### CLOB 스트리밍 읽기 (대용량일 때)

```java

// CLOB을 한 번에 읽으면 OOM 위험 → 스트리밍으로 읽는 게 안전함
Clob clob = resultSet.getClob("content");
Reader reader = clob.getCharacterStream();
BufferedReader br = new BufferedReader(reader);

StringBuilder sb = new StringBuilder();
String line;
while ((line = br.readLine()) != null) {
    sb.append(line);
}

```

---

 

## 8. 흔한 실수와 주의사항

| ❌ 실수 | ✅ 올바른 방법 |
|--------|-------------|
| CLOB에 `LIKE '%값%'` 인덱스 기대 | Full-text 검색 기능 사용 |
| BLOB 이미지를 API 응답에 직접 포함 | Base64 인코딩 후 전송 or URL 반환 |
| 대용량 CLOB을 `getString()`으로 한 번에 로드 | 스트리밍 방식으로 읽기 |
| JPA에서 `@Lob` 없이 CLOB 매핑 | 반드시 `@Lob` 어노테이션 추가 |
| MyBatis에서 `jdbcType` 생략 | `jdbcType=CLOB` / `jdbcType=BLOB` 명시 |
| BLOB에 텍스트 저장 | CLOB 또는 TEXT 타입 사용 |


--- 

## 9. 정리

> **"맞는 타입을 쓰는 것이 최적화의 시작임"**

- **VARCHAR/String** → 짧고 검색이 필요한 텍스트
- **CLOB** → 긴 텍스트 (본문, 계약서, 로그)
- **BLOB** → 이미지, 파일 등 바이너리 데이터
- **Tibero** → Oracle 호환이라 CLOB/BLOB 문법 동일하게 쓰면 됨
- 대용량 파일은 S3 같은 **오브젝트 스토리지 + URL 저장** 패턴 권장

- CLOB/BLOB은 반드시 **스트리밍 처리** 고려할 것

