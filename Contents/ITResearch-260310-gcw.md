# 📦 EAR vs WAR vs JAR vs TAR
## 서버 운영 관점에서 보는 패키징 파일 차이

IT 서버 운영을 하다 보면 다음과 같은 확장자를 자주 보게 된다.

```
.ear
.war
.jar
.tar
```
<img width="536" height="437" alt="image" src="https://github.com/user-attachments/assets/9a57edcc-7541-4821-9707-1d8dbec72204" />

이 파일들은 애플리케이션 배포 또는 파일 패키징을 위해 사용되며  
특히 Java 기반 서버 환경(Tomcat, WebLogic, JBoss 등)에서 많이 등장한다.

이 문서에서는 **서버 운영 / 배포 기준에서** 각각의 차이와 사용 용도를 정리한다.

---

# 1️⃣ JAR (Java Archive)

## 개념

JAR은 **Java 클래스와 라이브러리를 묶은 압축 파일**이다.  
실제로는 ZIP 포맷 기반이며 `.zip`으로 확장자를 바꾸면 압축 해제가 가능하다.

Java 애플리케이션에서 가장 기본적인 배포 단위이다.

---

## 서버 운영에서의 사용

### 1. Java 라이브러리

Java 프로젝트에서 라이브러리 형태로 사용된다.

예시

```
spring-core.jar
log4j.jar
mysql-connector.jar
```

프로젝트 dependency로 사용된다.

---

### 2. 실행 가능한 애플리케이션

Spring Boot 서버에서 가장 많이 사용되는 방식이다.

```
java -jar app.jar
```

Spring Boot는 내부에 Tomcat 같은 WAS를 포함하여  
단일 JAR 파일로 서버를 실행할 수 있다.

---

## 특징

| 항목 | 설명 |
|-----|-----|
| 목적 | Java 라이브러리 / 애플리케이션 |
| 실행 방식 | java -jar |
| 서버 필요 여부 | 독립 실행 가능 |
| 사용 환경 | Spring Boot |

---

# 2️⃣ WAR (Web Application Archive)

## 개념

WAR은 **웹 애플리케이션을 배포하기 위한 패키지 형식**이다.

```
Web Application Archive
```

Servlet 기반 웹 서버(WAS)에 배포한다.

대표적인 서버

- Tomcat
- Jetty
- JBoss
- WebLogic

---

## 서버 운영에서의 사용

### 웹 애플리케이션 배포

Tomcat 서버 기준

```
/webapps/app.war
```

해당 위치에 WAR 파일을 넣으면  
Tomcat이 자동으로 압축을 풀고 서비스를 시작한다.

---

### 기업 내부 웹 서비스

예시

```
portal.war
admin.war
api.war
```

각 WAR 파일이 하나의 웹 애플리케이션이 된다.

---

## 특징

| 항목 | 설명 |
|-----|-----|
| 목적 | 웹 애플리케이션 |
| 실행 방식 | WAS 필요 |
| 서버 | Tomcat / JBoss |
| 특징 | JSP / Servlet 포함 |

---

# 3️⃣ EAR (Enterprise Archive)

## 개념

EAR은 **대규모 엔터프라이즈 애플리케이션을 위한 패키지 형식**이다.

```
Enterprise Archive
```

여러 애플리케이션 모듈을 하나의 패키지로 묶어 배포할 수 있다.

주로 대기업 또는 금융 시스템에서 사용된다.

---

## 서버 운영에서의 사용

EAR은 다음과 같은 Enterprise WAS에서 많이 사용된다.

- WebLogic
- WebSphere
- JBoss

대형 시스템에서는 여러 서비스를 하나의 패키지로 묶어 배포한다.

예시 시스템

```
인터넷뱅킹
보험 시스템
대형 ERP
```

---

## 특징

| 항목 | 설명 |
|-----|-----|
| 목적 | 대형 엔터프라이즈 시스템 |
| 실행 방식 | WAS 필요 |
| 서버 | WebLogic / WebSphere |
| 특징 | 여러 모듈을 통합 배포 |

---

# 4️⃣ TAR (Tape Archive)

## 개념

TAR은 **Linux / Unix 환경에서 파일을 하나로 묶는 패키징 방식**이다.

```
Tape Archive
```

Java와 직접적인 관계는 없으며  
일반적인 서버 파일 패키징에 사용된다.

---

## 서버 운영에서의 사용

### 1. 서버 배포 패키지

운영 서버에 프로그램을 전달할 때 사용된다.

예시

```
app.tar.gz
deploy.tar
```

---

### 2. 로그 백업

로그 파일을 묶어서 보관할 때 사용된다.

예시

```
logs.tar
```

---

### 3. 서버 데이터 백업

```
tar -czvf backup.tar.gz /data
```

운영 서버에서 정기 백업을 만들 때 사용된다.

---

## 특징

| 항목 | 설명 |
|-----|-----|
| 목적 | 파일 묶기 |
| 실행 | 없음 |
| 서버 | Linux |
| 특징 | gzip과 함께 사용 가능 |

---

# 📊 정리

| 파일 | 의미 | 사용처 | 서버 |
|-----|-----|-----|-----|
| JAR | Java Archive | Java 라이브러리 / Spring Boot | Java |
| WAR | Web Archive | 웹 애플리케이션 | Tomcat |
| EAR | Enterprise Archive | 엔터프라이즈 시스템 | WebLogic |
| TAR | Tape Archive | 파일 패키징 | Linux |

---

# 🔚 한줄 정리

```
JAR → Java 실행 프로그램 또는 라이브러리
WAR → 웹 애플리케이션 배포 파일
EAR → 대형 엔터프라이즈 시스템 패키지
TAR → 리눅스 파일 묶기
```
