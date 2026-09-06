# 사내 SSL/TLS 인증서 통신 구조 정리

## 1. 개요

사내 시스템에서 SSL/TLS 인증서는 단순히 웹서버에 설치하는 파일이 아니라,  
**통신 구간마다 “누가 TLS 연결을 종료하고, 누가 상대방 인증서를 신뢰할지”를 결정하는 구조**로 이해하는 것이 중요함.

대표적으로 인증서는 다음과 같은 위치에 설치될 수 있음.

- L7 / Load Balancer / Reverse Proxy
- Nginx
- WebtoB
- Apache
- Tomcat
- JEUS 등 WAS
- Java TrustStore / KeyStore
- OS Root CA 저장소

인증서를 어디에 설치하는지는 결국 아래 두 가지 기준으로 결정됨.

1. **TLS 종료 지점(TLS Termination)이 어디인가**
2. **TLS Client가 상대 인증서를 어떤 TrustStore로 검증하는가**

---

# 2. SSL/TLS 통신의 기본 개념

HTTPS 통신은 일반 HTTP 통신 앞에 TLS 인증 절차가 추가된 구조임.

```text
Client
  │
  │ HTTPS 요청
  ▼
Server
```

실제 내부에서는 다음과 같은 순서로 진행됨.

```text
Client
  │
  │ 1. TLS 연결 요청
  ▼
Server
  │
  │ 2. 서버 인증서 전달
  ▼
Client
  │
  │ 3. 인증서 검증
  │
  │   - 도메인 일치 여부
  │   - 유효기간
  │   - 인증서 체인
  │   - Root CA 신뢰 여부
  ▼
Client
  │
  │ 4. 암호화 방식 및 세션 키 협상
  ▼
Server
  │
  │ 5. TLS 연결 완료
  ▼
Client ↔ Server
      암호화 통신
```

핵심은 **서버가 인증서를 가지고 있고, Client가 그 인증서를 검증한다는 것**임.

---

# 3. 서버 인증서와 Root CA의 역할

일반적인 인증서 구조는 다음과 같음.

```text
Root CA
   │
   ▼
Intermediate CA
   │
   ▼
Server Certificate
```

예를 들어 서버 인증서가 다음과 같다고 가정함.

```text
CN = api.abc.test.com
```

서버는 TLS 연결 시 자신의 인증서와 보통 Intermediate CA 인증서를 Client에게 전달함.

```text
Server Certificate
      │
      ▼
Intermediate CA
      │
      ▼
Root CA
```

Client는 이 체인을 따라가면서 최종 Root CA가 자신의 신뢰 저장소에 존재하는지 확인함.

즉,

```text
서버 인증서
    ↓
Intermediate CA
    ↓
Root CA
    ↓
Client TrustStore에 존재?
```

존재하면 신뢰 가능함.

존재하지 않으면 대표적으로 다음과 같은 오류가 발생할 수 있음.

```text
PKIX path building failed
SunCertPathBuilderException
unable to find valid certification path to requested target
```

---

# 4. 인증서에서 가장 중요한 두 가지 파일

인증서를 이해할 때 크게 다음 두 가지를 구분해야 함.

## 4.1 Server Certificate

서버의 신원을 나타내는 인증서임.

예:

```text
server.crt
server.pem
```

서버가 Client에게 전달함.

---

## 4.2 Private Key

서버 인증서와 한 쌍을 이루는 개인키임.

예:

```text
server.key
private.key
```

외부로 전달되지 않으며 서버에만 존재해야 함.

```text
Server Certificate + Private Key
```

이 둘을 이용해 서버가 해당 인증서의 실제 소유자임을 증명함.

---

# 5. 인증서를 어디에 설치해야 하는가

인증서를 설치해야 하는 위치는 **HTTPS 연결을 실제로 종료하는 위치**임.

예를 들어 다음 구조가 있다고 가정함.

```text
사용자
  │
  │ HTTPS
  ▼
L7
  │
  │ HTTP
  ▼
WebtoB
  │
  ▼
JEUS
```

이 구조에서 HTTPS는 L7에서 끝남.

따라서 서버 인증서는 L7에 설치됨.

```text
Client
   │
   │ HTTPS
   ▼
┌─────────────┐
│     L7      │
│ SSL 인증서   │
└─────────────┘
   │
   │ HTTP
   ▼
WebtoB
   │
   ▼
JEUS
```

이 방식을 일반적으로 **SSL Offloading 또는 TLS Termination**이라고 부름.

---

# 6. L7에 인증서를 설치하는 구조

대표적인 구조는 다음과 같음.

```text
Internet / Client
        │
        │ HTTPS
        ▼
┌─────────────────┐
│       L7        │
│ Server Cert     │
│ Private Key     │
└─────────────────┘
        │
        │ HTTP
        ▼
┌─────────────────┐
│ Web Server      │
│ Nginx / WebtoB  │
└─────────────────┘
        │
        ▼
       WAS
```

이 경우 Client와 TLS 통신을 하는 주체는 L7임.

따라서 Nginx/WebtoB에는 인증서가 없어도 됨.

장점은 다음과 같음.

- 인증서를 L7에서 중앙 관리 가능
- Web Server의 SSL 처리 부하 감소
- 다수 서버의 인증서 관리 단순화

단점은 L7 이후 구간이 HTTP라면 내부망에서는 암호화되지 않는다는 점임.

---

# 7. WebtoB / Nginx에 인증서를 설치하는 구조

다음과 같은 구조도 가능함.

```text
Client
   │
   │ HTTPS
   ▼
L7
   │
   │ HTTPS Pass-through
   ▼
WebtoB / Nginx
   │
   │ TLS Termination
   ▼
WAS
```

이 경우 인증서는 WebtoB 또는 Nginx에 존재함.

```text
Client
    │
    ▼
L7
    │
    │ HTTPS 그대로 전달
    ▼
┌──────────────────┐
│ WebtoB / Nginx   │
│ Server Cert      │
│ Private Key      │
└──────────────────┘
```

L7은 단순히 TCP 연결을 전달하고 실제 TLS Handshake는 Web Server가 수행함.

---

# 8. Tomcat / JEUS 같은 WAS에 인증서를 설치하는 경우

Web Server 없이 WAS가 직접 HTTPS를 제공할 수도 있음.

```text
Client
   │
   │ HTTPS
   ▼
Tomcat / JEUS
   │
   ▼
Application
```

이 경우 인증서는 WAS Connector에 설정됨.

예를 들어 Tomcat 구조는 개념적으로 다음과 같음.

```text
Tomcat HTTPS Connector
        │
        ├─ Server Certificate
        └─ Private Key
```

외부 Client와 직접 TLS Handshake를 수행함.

다만 일반적인 기업 환경에서는 보통

```text
L7
 ↓
Web Server
 ↓
WAS
```

구조를 사용하기 때문에 WAS가 직접 외부 TLS를 종료하지 않는 경우도 많음.

---

# 9. 사용자 → 웹서비스 접속 시 인증서 동작

다음 구조를 예로 들 수 있음.

```text
사용자 Browser
      │
      │ https://bank.test.com
      ▼
L7
      │
      ▼
WebtoB
      │
      ▼
JEUS
```

L7에서 TLS를 종료한다면 동작은 다음과 같음.

```text
Browser
   │
   │ ① HTTPS 연결
   ▼
L7
   │
   │ ② bank.test.com 인증서 전달
   ▼
Browser
   │
   │ ③ 인증서 검증
   │
   │   - CN/SAN
   │   - 기간
   │   - CA Chain
   │   - Root CA
   ▼
L7
   │
   │ ④ TLS 세션 생성
   ▼
암호화 통신
```

이때 Browser가 사내 Root CA를 신뢰하고 있어야 함.

사내 Private CA를 사용하는 경우 회사 PC에 다음과 같이 Root 인증서를 배포하는 이유가 이것임.

```text
Windows Certificate Store
macOS Keychain
Linux CA Store
```

---

# 10. AP → 타 AP HTTPS 호출

인증서 문제에서 가장 혼동이 많은 부분임.

예를 들어 다음 구조가 있다고 가정함.

```text
AP Server A
     │
     │ HTTPS REST API
     ▼
AP Server B
```

이 경우 역할은 다음과 같음.

```text
A = TLS Client
B = TLS Server
```

따라서 B는 서버 인증서를 제공함.

```text
AP A
  │
  │ HTTPS
  ▼
AP B
  │
  │ Server Certificate
  ▼
AP A
```

그리고 A가 B의 인증서를 검증함.

즉 중요한 것은 B의 인증서를 A 서버에 넣는 것이 아니라,

**A가 사용하는 TrustStore에서 B 인증서의 Root CA를 신뢰할 수 있어야 함.**

---

# 11. Java에서 Root 인증서가 필요한 이유

Java 애플리케이션에서 HTTPS 호출을 하면 Java 자체 TLS Stack이 인증서를 검증함.

예:

```text
Spring Application
     │
     │ RestTemplate
     ▼
https://api.test.com
```

실제 구조는 다음과 같음.

```text
Java Application
      │
      ▼
JSSE
(Java SSL/TLS)
      │
      ▼
Java TrustStore
      │
      ▼
상대 서버 인증서 검증
```

대표적인 Java 기본 TrustStore는 다음과 같음.

```text
$JAVA_HOME/lib/security/cacerts
```

또는 별도 TrustStore를 지정할 수도 있음.

```text
-Djavax.net.ssl.trustStore=/app/cert/truststore.jks
```

---

# 12. Java TrustStore와 OS 인증서 저장소의 차이

특히 사내 환경에서 중요함.

OS에 Root CA를 설치했다고 해서 항상 Java가 신뢰하는 것은 아님.

예를 들어 다음과 같은 상황이 가능함.

```text
RHEL OS
 └─ 사내 Root CA 존재

Java cacerts
 └─ 사내 Root CA 없음
```

curl은 정상일 수 있음.

```bash
curl https://api.test.com
```

하지만 Java에서는 다음 오류가 발생할 수 있음.

```text
PKIX path building failed
```

이유는 각각 사용하는 TrustStore가 다르기 때문임.

```text
curl
 ↓
OS CA Store

Java
 ↓
Java cacerts / 별도 TrustStore
```

---

# 13. AP → L7 → AP 구조에서 인증서 검증

실제 기업 환경에서는 AP끼리 직접 연결하지 않고 L7을 통하는 경우가 많음.

```text
AP A
 │
 │ HTTPS
 ▼
L7
 │
 │ HTTP
 ▼
AP B
```

이 경우 TLS Server는 AP B가 아니라 L7임.

따라서 AP A는 **L7이 제공하는 인증서**를 검증함.

```text
AP A
  │
  │ TLS Handshake
  ▼
L7
  │
  │ Server Certificate
  ▼
AP A TrustStore
```

L7 뒤에 있는 AP B의 인증서는 이 통신에서는 관계가 없음.

---

# 14. AP → L7 → Web Server → WAS 구조

좀 더 일반적인 사내 구조는 다음과 같음.

```text
AP A
 │
 │ HTTPS
 ▼
L7
 │
 │ HTTP
 ▼
WebtoB
 │
 │ 내부 연계
 ▼
JEUS / AP B
```

인증서가 사용되는 구간은 다음뿐임.

```text
AP A
  │
  │ HTTPS
  ▼
L7
```

따라서

```text
L7
 ├─ Server Certificate
 └─ Private Key

AP A
 └─ Root CA Trust
```

구조가 됨.

---

# 15. 모든 구간을 HTTPS로 구성하는 경우

보안 수준이 높은 환경에서는 모든 구간을 TLS로 구성하기도 함.

```text
Client
 │ HTTPS
 ▼
L7
 │ HTTPS
 ▼
WebtoB
 │ HTTPS
 ▼
WAS
 │ HTTPS
 ▼
Backend API
```

이 경우 각 연결마다 별도의 TLS Handshake가 발생함.

```text
Client → L7
L7 → WebtoB
WebtoB → WAS
WAS → Backend API
```

각 구간별로

```text
TLS Client
TLS Server
Certificate
TrustStore
```

관계가 별도로 존재함.

---

# 16. 인증서 검증의 핵심 기준

Client는 일반적으로 다음 항목을 검사함.

## 16.1 인증서 유효기간

```text
Not Before
Not After
```

현재 시간이 인증서 유효기간 안에 존재해야 함.

---

## 16.2 도메인 검증

예를 들어 요청 주소가

```text
https://api.test.com
```

이라면 인증서 SAN에 다음 값이 존재해야 함.

```text
DNS:api.test.com
```

과거에는 CN을 중심으로 검증했으나 현재는 SAN이 중요함.

---

## 16.3 인증서 Chain 검증

```text
Server Certificate
      ↓
Intermediate CA
      ↓
Root CA
```

각 인증서의 서명 관계를 검증함.

---

## 16.4 Root CA Trust

최종 Root CA가 Client TrustStore에 존재해야 함.

```text
Client TrustStore
      │
      └─ Root CA
```

---

# 17. 인증서 Chain 파일이 필요한 이유

서버에서는 보통 서버 인증서만 전달하면 충분하지 않을 수 있음.

예:

```text
Server Certificate
Intermediate CA
```

를 같이 제공해야 Client가 Root CA까지 연결할 수 있음.

따라서 다음과 같은 파일이 사용됨.

```text
server.pem
chain.pem
fullchain.pem
```

예를 들어

```text
fullchain.pem
```

은 개념적으로 다음과 같음.

```text
Server Certificate
+
Intermediate Certificate
```

---

# 18. 인증서 설치 위치를 판단하는 방법

가장 먼저 확인해야 할 것은 다음임.

```text
HTTPS가 어디에서 끝나는가?
```

예:

```text
Client
 ↓ HTTPS
L7
 ↓ HTTP
WebtoB
```

→ 인증서 위치

```text
L7
```

반면

```text
Client
 ↓ HTTPS
L7
 ↓ HTTPS Pass-through
WebtoB
```

→ 인증서 위치

```text
WebtoB
```

---

# 19. TLS Client가 누구인지 판단하는 방법

다음으로 확인해야 할 것은

```text
HTTPS 요청을 시작하는 주체가 누구인가?
```

임.

예를 들어

```text
Browser → Server
```

에서는

```text
Browser = TLS Client
```

이고,

```text
AP A → AP B
```

에서는

```text
AP A = TLS Client
```

임.

따라서 인증서 신뢰 설정은 항상 TLS Client 쪽에서 확인해야 함.

---

# 20. 대표적인 환경별 인증서 위치

| 환경 | 서버 인증서 위치 | Root CA 신뢰 위치 |
|---|---|---|
| Browser → L7 | L7 | Browser / OS |
| Browser → Nginx | Nginx | Browser / OS |
| Browser → WebtoB | WebtoB | Browser / OS |
| Browser → Tomcat | Tomcat | Browser / OS |
| AP → L7 | L7 | AP TrustStore |
| Java AP → HTTPS API | 상대 서버 | Java cacerts |
| curl → HTTPS API | 상대 서버 | OS CA Store |
| Nginx → HTTPS Backend | Backend | Nginx/OS CA |
| L7 → HTTPS Web Server | Web Server | L7 TrustStore |

---

# 21. KeyStore와 TrustStore 차이

Java에서 특히 혼동하기 쉬움.

## KeyStore

자신의 인증서와 Private Key를 보관함.

```text
KeyStore
 ├─ Server Certificate
 └─ Private Key
```

즉 TLS Server 역할을 할 때 사용됨.

---

## TrustStore

상대 서버의 인증서를 신뢰하기 위한 CA 인증서를 보관함.

```text
TrustStore
 └─ Root CA
```

즉 TLS Client 역할을 할 때 주로 사용됨.

---

# 22. 예시 1 — 사용자가 웹페이지 접속

```text
사용자 PC
   │
   │ HTTPS
   ▼
L7
   │
   │ HTTP
   ▼
WebtoB
   │
   ▼
JEUS
```

구성:

```text
L7
 ├─ bank.test.com 인증서
 └─ Private Key

사용자 PC
 └─ 사내 Root CA
```

TLS 검증:

```text
사용자 PC
 ↓
L7 인증서 확인
 ↓
Intermediate CA 확인
 ↓
사내 Root CA 확인
```

---

# 23. 예시 2 — AP에서 타 AP 호출

```text
AP A
 │
 │ https://api.test.com
 ▼
L7
 │
 │ HTTP
 ▼
AP B
```

구성:

```text
L7
 ├─ api.test.com 인증서
 └─ Private Key

AP A
 └─ Java TrustStore
       └─ 사내 Root CA
```

여기서 AP B에 인증서가 없어도 HTTPS 통신에는 문제가 없음.

TLS가 L7에서 종료되기 때문임.

---

# 24. 예시 3 — AP가 직접 HTTPS WAS 호출

```text
AP A
 │
 │ HTTPS
 ▼
Tomcat B
```

구성:

```text
Tomcat B
 ├─ Server Certificate
 └─ Private Key

AP A
 └─ Java TrustStore
       └─ Root CA
```

이 경우 Tomcat B가 직접 TLS Server 역할을 수행함.

---

# 25. PKIX 오류를 보는 방법

대표 오류:

```text
PKIX path building failed
SunCertPathBuilderException
unable to find valid certification path to requested target
```

이 오류는 대부분 TLS Client가 인증서 Chain을 Root CA까지 완성하지 못했다는 의미임.

점검 순서는 다음과 같음.

```text
1. 실제 TLS 종료 지점 확인

2. 서버 인증서 확인

3. Intermediate 인증서 전달 여부 확인

4. Root CA 확인

5. Client가 사용하는 TrustStore 확인

6. TrustStore에 Root CA 존재 여부 확인
```

Java라면 특히 다음을 확인해야 함.

```text
현재 실행중인 Java의 JAVA_HOME
```

그리고

```text
$JAVA_HOME/lib/security/cacerts
```

가 실제 애플리케이션에서 사용되는지 확인해야 함.

---

# 26. curl은 되고 Java는 안 되는 이유

사내 환경에서 매우 흔한 상황임.

```text
curl https://api.test.com
→ 성공

Java RestTemplate
→ PKIX 오류
```

가능한 구조:

```text
OS TrustStore
 └─ 사내 Root CA 존재

Java cacerts
 └─ 사내 Root CA 없음
```

따라서 curl은 성공하지만 Java는 실패함.

반대로 Java에만 Root CA가 존재하면 Java는 성공하고 OS 기반 프로그램은 실패할 수도 있음.

---

# 27. 인증서 교체 시 확인해야 하는 항목

서버 인증서를 교체하면 단순히 파일 하나만 바꾸는 것이 아니라 다음 구조를 확인해야 함.

```text
Server Certificate
Intermediate CA
Root CA
```

특히 사내 인증서가 다음처럼 변경될 수 있음.

기존:

```text
Server Cert
 ↓
Private CA A
 ↓
Root CA A
```

변경:

```text
Server Cert
 ↓
Private CA B
 ↓
Root CA B
```

이 경우 Client가 Root CA B를 신뢰하지 않으면 기존 통신이 실패할 수 있음.

---

# 28. 사내 인증서 교체 이후 장애가 발생하는 대표 패턴

## 패턴 1

브라우저 정상 / Java API 실패

```text
Browser
→ OS Root CA 사용
→ 정상

Java
→ cacerts 사용
→ Root CA 없음
→ PKIX 오류
```

---

## 패턴 2

Web 접속 정상 / AP 연계 실패

```text
사용자
→ L7
→ 정상

AP
→ Backend HTTPS
→ Backend CA 미신뢰
→ 실패
```

---

## 패턴 3

L7 인증서 변경 이후 AP 호출 실패

```text
AP
 ↓
L7
```

L7 인증서의 CA Chain이 변경되었는데 AP TrustStore에는 새로운 Root CA가 없는 경우임.

---

# 29. SSL 인증서 문제를 보는 핵심 사고방식

인증서 장애가 발생하면 아래 순서로 보는 것이 가장 중요함.

```text
① HTTPS 요청을 누가 시작하는가?
        ↓
   TLS Client 확인

② HTTPS가 어디에서 종료되는가?
        ↓
   TLS Server 확인

③ TLS Server가 어떤 인증서를 주는가?
        ↓
   Server Certificate 확인

④ TLS Client가 무엇을 신뢰하는가?
        ↓
   TrustStore 확인
```

이를 한 줄로 표현하면 다음과 같음.

```text
TLS Client
    │
    │ 상대 인증서 검증
    ▼
TLS Server
    │
    └─ Server Certificate + Private Key
```

그리고

```text
TLS Client
    │
    └─ TrustStore
          └─ Root CA
```

구조임.

---

# 30. 전체 구조 요약

대표적인 사내 시스템을 예로 들면 다음과 같음.

```text
[사용자 Browser]
      │
      │ HTTPS
      ▼
┌────────────────────┐
│        L7          │
│ Server Certificate │
│ Private Key        │
└────────────────────┘
      │
      │ HTTP
      ▼
┌────────────────────┐
│ WebtoB / Nginx     │
└────────────────────┘
      │
      ▼
┌────────────────────┐
│ JEUS / Tomcat      │
│ Application        │
└────────────────────┘
      │
      │ HTTPS API
      ▼
┌────────────────────┐
│ Backend L7         │
│ Server Certificate │
└────────────────────┘
      │
      ▼
Backend AP
```

이 구조에서는 인증서가 두 번 사용됨.

첫 번째:

```text
Browser
 ↓ HTTPS
L7
```

두 번째:

```text
Application
 ↓ HTTPS
Backend L7
```

각 구간은 완전히 별도의 TLS 연결임.

따라서 각각 별도의 인증서와 Trust 관계가 존재함.

---

# 31. 핵심 정리

SSL/TLS 인증서를 이해할 때 가장 중요한 것은  
**“인증서를 어느 서버에 설치했는가” 자체가 아니라 TLS Client와 TLS Server가 누구인지 파악하는 것**임.

기본 원칙은 다음과 같음.

```text
TLS Server
→ Server Certificate + Private Key 보유

TLS Client
→ Root CA / TrustStore 보유
```

그리고

```text
HTTPS가 종료되는 장비
=
Server Certificate가 설치되는 위치
```

라고 보면 대부분의 사내 SSL 구조를 이해할 수 있음.

특히 Java 기반 AP 연계에서는

```text
OS Root CA
≠
Java TrustStore
```

일 수 있기 때문에 브라우저나 curl이 정상이라고 해서 Java 통신까지 정상이라고 판단하면 안 됨.

인증서 장애가 발생했을 때는 항상

```text
HTTPS 호출 주체
→ TLS 종료 지점
→ 서버 인증서 Chain
→ Client TrustStore
```

순서로 확인하는 것이 가장 효율적임.
