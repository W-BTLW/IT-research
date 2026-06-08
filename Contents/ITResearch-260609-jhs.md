## MCP

REST API가 사람과 시스템을 연결했다면, MCP는 AI와 시스템을 연결하는 표준이 될 수 있을까?


## 1. MCP란?

MCP(Model Context Protocol)는 AI 모델이 외부 시스템과 통신하기 위한 표준 프로토콜(규약)이다.

쉽게 말하면,

> "USB가 키보드, 마우스, 프린터 등의 연결 방식을 통일한 것처럼,
> MCP는 AI가 Github, Jira, DB, 파일시스템 등 다양한 도구와 연결하는 방식을 통일한 것"

이라고 이해할 수 있다.

---

### 기존 방식

AI가 외부 시스템을 사용하려면 각각 별도의 API 연동이 필요했다.

```text
AI ↔ Github API
AI ↔ Jira API
AI ↔ Slack API
AI ↔ Database API
```

서비스가 늘어날수록 AI와 외부 시스템의 연결이 복잡해진다.

---

### MCP 방식

MCP는 AI와 외부 시스템 사이에 표준 인터페이스를 제공한다.

```text
AI
 ↓
MCP
 ↓
Github
Jira
Slack
Database
Filesystem
```

AI는 MCP 규격만 이해하면 다양한 시스템과 연결할 수 있다.

---

### HTTP와의 차이

많은 사람들이 MCP를 HTTP 같은 새로운 통신 프로토콜로 오해한다.

실제로는 HTTP를 대체하는 것이 아니다.

```text
AI
 ↓ MCP
MCP Server
 ↓ HTTP
Github API
```

- HTTP : 시스템과 시스템 간 통신 규약
- MCP : AI와 Tool 간 통신 규약

즉 MCP는 네트워크 프로토콜이라기보다 AI용 표준 인터페이스에 가깝다.

---

## 2. 왜 갑자기 MCP가 뜨는가?

AI Agent 시대가 시작되면서 AI가 단순 채팅을 넘어 실제 업무를 수행해야 하기 때문이다.

예를 들어 사용자가 다음과 같이 요청한다고 가정하자.

```text
이번 주 내 Jira 작업 보여줘
```

AI는 기본적으로 Jira에 접근할 수 없다.

따라서 외부 시스템을 조회할 수 있는 Tool이 필요하다.

---

### 기존 문제점

각 AI 서비스마다 Tool을 별도로 개발해야 했다.

```text
ChatGPT용 Github 연동
Claude용 Github 연동
Cursor용 Github 연동
```

같은 기능인데도 여러 번 개발해야 하는 비효율이 존재했다.

---

### MCP의 등장

MCP는 Tool 연동 방식을 표준화한다.

```text
Github MCP Server
```

하나만 만들면

```text
ChatGPT
Claude
Cursor
기타 AI Agent
```

가 공통으로 사용할 수 있다.

---

### OpenAPI와 비교

MCP를 이해하는 가장 쉬운 방법은 OpenAPI와 비교하는 것이다.

```text
OpenAPI
= 사람이 API를 이해하기 위한 표준

MCP
= AI가 Tool을 이해하기 위한 표준
```
---

## 3. 실제 적용 사례

### 3.1 Github 연동

사용자

```text
내가 어제 올린 PR 보여줘
```

동작 흐름

```text
AI
 ↓
Github MCP Server
 ↓
Github API
```

AI는 Github API를 직접 알 필요 없이 MCP Tool만 호출하면 된다.

---

### 3.2 Jira 연동

사용자

```text
이번 스프린트 내 작업 보여줘
```

동작 흐름

```text
AI
 ↓
Jira MCP Server
 ↓
Jira API
```

결과 예시

```text
- 로그인 개선
- 이체 한도 변경
- PUSH 알림 수정
```

---

### 3.3 Slack 연동

사용자

```text
개발팀 채널 최근 논의사항 요약해줘
```

동작 흐름

```text
AI
 ↓
Slack MCP Server
 ↓
메시지 조회
 ↓
요약 생성
```

---
## MCP는 Tool마다 따로 존재하는 것 아닌가?

맞다.

Github, Jira, Slack, Database 등 각 시스템마다 MCP Server는 따로 존재한다.

예시)

```text
Github MCP Server
Jira MCP Server
Slack MCP Server
Database MCP Server
```

따라서 MCP가 모든 Tool을 하나로 통합하는 것은 아니다.

---

## 그렇다면 기존 API 연동과 무엇이 다른가?

핵심은 **Tool 자체를 통합하는 것이 아니라 Tool을 연결하는 방식을 표준화하는 것**이다.

### REST API와 비교

현재도 서비스별 API는 모두 다르다.

```http
Github API
GET /repos/{owner}/{repo}/pulls

Jira API
GET /rest/api/3/search

Slack API
GET /conversations.history
```

하지만 모두 HTTP라는 공통 규약을 사용한다.

---

MCP도 동일한 개념이다.

```text
github.list_pull_requests

jira.search_issue

slack.get_messages
```

Tool은 다르지만 AI가 사용하는 방식은 동일하다.

---

## MCP가 해결하는 진짜 문제

MCP 이전에는 AI마다 별도 연동이 필요했다.

```text
ChatGPT용 Github 연동
Claude용 Github 연동
Cursor용 Github 연동
```

같은 기능을 여러 번 개발해야 했다.

---

MCP 이후에는

```text
Github MCP Server
```

하나만 구현하면

```text
ChatGPT
Claude
Cursor
기타 AI Agent
```

모두 동일하게 사용할 수 있다.

---

## 핵심 요약

- MCP는 Tool을 하나로 만드는 기술이 아니다.
- Github, Jira, Slack 등 시스템별 MCP Server는 따로 존재한다.
- MCP는 AI와 Tool 간 연결 방식을 표준화하는 규약이다.
- 한 번 만든 MCP Server를 여러 AI가 재사용할 수 있다는 것이 가장 큰 장점이다.
```
