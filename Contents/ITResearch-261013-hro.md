# Gradle Build Lifecycle

## 1. Gradle Lifecycle이란?

Gradle에서 **Build Lifecycle**이란,

**Gradle 명령어가 실행된 순간부터 실제 Task가 수행될 때까지 Gradle이 빌드를 처리하는 전체 흐름**을 의미한다.

Gradle의 Build Lifecycle은 크게 3단계로 나뉜다.

```text
Initialization
      ↓
Configuration
      ↓
Execution
```

| 단계 | 핵심 역할 |
|---|---|
| Initialization | 어떤 프로젝트를 빌드할지 결정 |
| Configuration | 어떤 Task를 실행해야 하는지 구성 |
| Execution | 실제 Task 실행 |

---

# 2. Initialization Phase

## "어떤 프로젝트를 빌드할 것인가?"

Gradle이 가장 먼저 수행하는 단계이다.

주로 `settings.gradle` 또는 `settings.gradle.kts`를 읽는다.

예를 들어 Multi-Project 구조라면,

```groovy
rootProject.name = 'bank-framework'

include 'common'
include 'online'
include 'batch'
```

Gradle은 이 정보를 보고

```text
bank-framework
 ├─ common
 ├─ online
 └─ batch
```

어떤 프로젝트들이 이번 Build에 참여하는지 결정한다.

즉,

> **Initialization = Build 대상 프로젝트 구조를 결정하는 단계**

이다.

---

# 3. Configuration Phase

## "무슨 일을 해야 하는가?"

Initialization이 끝나면 각 프로젝트의 `build.gradle`을 읽는다.

이 과정에서 Gradle은

- Plugin 설정
- Dependency 설정
- Task 등록 및 설정
- Task 간 의존관계

등을 확인한다.

예를 들어,

```groovy
tasks.register("hello") {
    println("Configuration")

    doLast {
        println("Hello Gradle")
    }
}
```

여기서 중요한 점은

```groovy
println("Configuration")
```

과

```groovy
doLast {
    println("Hello Gradle")
}
```

의 실행 시점이 다르다는 것이다.

`println("Configuration")`은 **Configuration 단계**에서 실행되고,

`doLast` 내부 코드는 **Execution 단계**에서 실행된다.

Gradle은 이 단계에서 Task들의 관계를 분석하여 **Task Graph(DAG)** 를 만든다.

예를 들어,

```text
build
 └─ check
     └─ test
```

처럼 어떤 Task를 어떤 순서로 실행해야 하는지 결정한다.

즉,

> **Configuration = build.gradle을 해석하고 실행할 Task Graph를 구성하는 단계**

이다.

---

# 4. Execution Phase

## "실제로 일을 수행한다."

Configuration 단계에서 만들어진 Task Graph를 기반으로 실제 Task를 실행한다.

예를 들어,

```bash
./gradlew build
```

를 실행하면 Java 프로젝트에서는 대략 다음과 같은 Task들이 의존관계에 따라 수행될 수 있다.

```text
compileJava
    ↓
processResources
    ↓
classes
    ↓
test
    ↓
jar
    ↓
build
```

모든 Task를 무조건 실행하는 것이 아니라,

**요청한 Task와 해당 Task를 실행하는 데 필요한 의존 Task들을 실행한다.**

즉,

> **Execution = 구성된 Task Graph를 기준으로 실제 작업을 수행하는 단계**

이다.

---

# 5. 전체 흐름으로 보기

사용자가 다음 명령어를 실행했다고 가정한다.

```bash
./gradlew build
```

Gradle 내부에서는 다음과 같은 흐름으로 처리된다.

```text
./gradlew build
      │
      ▼
① Initialization
   settings.gradle 확인
   프로젝트 구조 결정
      │
      ▼
② Configuration
   build.gradle 확인
   Plugin / Dependency / Task 설정
   Task Graph 생성
      │
      ▼
③ Execution
   필요한 Task 실제 실행
   compile → test → jar → build
```

한 문장으로 정리하면,

> **프로젝트를 찾고 → 해야 할 일을 정하고 → 실제로 실행한다.**

---

# 6. 왜 알아야 할까?

Gradle Lifecycle을 이해하면 `build.gradle`에서 작성한 코드가

**언제 실행되는지** 이해할 수 있다.

예를 들어 다음 코드가 있다고 하자.

```groovy
println("A")

tasks.register("hello") {

    println("B")

    doLast {
        println("C")
    }
}
```

개념적으로 보면,

```text
Configuration Phase
A
B

Execution Phase
C
```

처럼 실행 시점이 구분된다.

따라서 무거운 로직이나 불필요한 작업을 Configuration 단계에서 수행하면

```text
Gradle 시작
   ↓
Configuration 시간이 길어짐
   ↓
전체 Build 속도 저하
```

가 발생할 수 있다.

그래서 Gradle에서는 필요한 Task만 구성하도록 하는 **Task Configuration Avoidance**와  
Configuration 결과를 재사용하는 **Configuration Cache** 같은 최적화 기능도 제공한다.

---

# 7. Maven Lifecycle과 헷갈리지 않기

Maven의 Lifecycle은 보통

```text
validate
compile
test
package
verify
install
deploy
```

같은 **Build 단계(Phase)** 를 의미한다.

반면 Gradle에서 말하는 Build Lifecycle은

```text
Initialization
Configuration
Execution
```

이라는 **Gradle 자체의 Build 처리 과정**을 의미한다.

Gradle에서는 `compileJava`, `test`, `build` 등은 Lifecycle의 단계라기보다 **Task**이다.

---

# 정리

## 30초 정리

> Gradle Build Lifecycle은 Gradle이 빌드를 처리하는 전체 과정으로  
> **Initialization, Configuration, Execution 세 단계**로 구성됩니다.
>
> Initialization에서는 `settings.gradle`을 기준으로 빌드에 참여할 프로젝트를 결정하고,  
> Configuration에서는 `build.gradle`을 평가하면서 Task와 의존관계를 구성해 Task Graph를 만듭니다.
>
> 마지막 Execution에서는 만들어진 Task Graph를 기준으로 사용자가 요청한 Task와 필요한 의존 Task를 실제로 실행합니다.

---

```text
Gradle Build Lifecycle

1. Initialization
   → 어떤 프로젝트?

2. Configuration
   → 어떤 Task?

3. Execution
   → Task 실행
```
