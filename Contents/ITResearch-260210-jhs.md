# URL 인코딩 정리
---

## 1. URL 인코딩이 필요한 이유

URL은 단순 문자열이 아니라 **의미를 가진 문법 구조**다.  
일부 문자는 URL에서 이미 역할을 가지고 있기 때문에,  
데이터 값으로 그대로 전달되면 서버가 잘못 해석한다.

### URL에서 의미를 가지는 문자

```
?  : Query String 시작
&  : 파라미터 구분
=  : key=value 구분
/  : 경로(Path) 구분
#  : Fragment -> 서버로 보내지진 않고 클라이언트 단에서만 사용됨
    ex) https://example.com/page#section2
    브라우저 동작:
    1. 페이지 로드
    2. `id="section2"` 요소 탐색
    3. 해당 위치로 스크롤 이동 
%  : 인코딩 시작 문자
```

따라서 URL에 들어가는 값은 **인코딩을 통해 안전한 문자로 변환**해야 한다.

---

## 2. URL 인코딩이란?

URL에서 안전하지 않은 문자를  
`% + 16진수(UTF-8 기준)` 형태로 변환하는 과정이다.

```
공백   → %20
&      → %26
?      → %3F
=      → %3D
한글   → %EC%95%84%EC%9D%B4...
```

---

## 3. encodeURI vs encodeURIComponent

### 핵심 차이

```
encodeURI
- URL 전체를 인코딩
- ?, &, = 같은 URL 문법 문자는 인코딩하지 않음
- 즉, URL의 구조(프로토콜, 경로, 쿼리 구분자 등)를 유지한 채, 그 외에 인코잉이 필요한 문자들만 인코딩함
- 용도 : 완성된 URL을 인코딩할 때 쓰

encodeURIComponent
- URL의 값(value)을 인코딩
- ?, &, = 도 전부 인코딩
- 쿼리 문자열의 값, 폼 데이터, 동적으로 URL 일부를 만들 때 적합
- 용도 : URL 쿼리 파라미터 값이나 경로 일부를 인코딩할 때 쓰임
```

### 예제

```javascript
encodeURI("https://example.com/search?q=아이폰&케이스")
// https://example.com/search?q=%EC%95%84%EC%9D%B4%ED%8F%B0 & %EC%BC%80%EC%9D%B4%EC%8A%A4

encodeURIComponent("아이폰&케이스")
// %EC%95%84%EC%9D%B4%ED%8F%B0%26%EC%BC%80%EC%9D%B4%EC%8A%A4
```

---

| 구분            | encodeURI | encodeURIComponent |
| ------------- | --------- | ------------------ |
| 용도            | URL 전체    | URL 일부(값)          |
| `/ ? & =` 인코딩 | ❌ 안 함     | ✅ 함                |
| 실무 사용         | 거의 없음     | **대부분 이걸 사용**      |


## 4. 이중 인코딩(Double Encoding)이란?

이미 인코딩된 값을 **다시 인코딩하는 사고**를 말한다.

```
1회 인코딩 : 아이폰 → %EC%95%84%EC%9D%B4%ED%8F%B0
2회 인코딩 : % → %25
결과       : %25EC%2595%2584...
```

---

### 사례. encodeURI + encodeURIComponent 혼용

```javascript
const keyword = encodeURIComponent("아이폰 케이스");
const url = encodeURI(`/search?q=${keyword}`);
```
