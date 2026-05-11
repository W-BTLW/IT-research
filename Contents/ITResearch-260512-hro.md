# ClassLoader
ClassLoader는 JVM의 구성요소 중 하나로, '.class' 바이트 코드를 읽어 들여 class 객체를 생성하는 역할을 담당한다.
즉, 클래스가 요청될 때 class파일로부터 바이트 코드를 읽어 메모리로 로딩하는 역할

자바 클래스들은 한 번에 모든 클래스가 메모리에 올라가지 않는다.
각 클래스들은 필요할 때 어플리케이션에 올라가게 되며, 이 작업을 클래스로더가 해준다.

</br>

### 왜 ClassLocader가 필요할까?
예를 들어 아래 코드를 실행한다고 가정
``` java
UserService service = new UserService();
```

그러면 JVM은 UserService.class 파일을 찾아야 한다.
그런데 Java 프로그램은 클래스가 엄청 많다.
예를들어 String, List, Object, UserService, 외부 라이브러리 , ... 등
이 모든 클래스에서 똑부러지게 특정 클래스를 어떻게 찾는가? ClassLoader가 찾는다

</br>

### ClassLoader는 어디서 클래스를 찾을까?
대표적인 위치
- 내 프로젝트 classes 폴더
- jar 파일 내부
- SpringBoot 라이브러리
- JDK 내부 클래스
- JEUS 공용 라이브러리
즉, Class Loader는 여러 위치를 뒤져서 클래스를 찾는다

</br>

### ClassLoader == 도서관 사서
ClassLoader는 "도서관 사서"와 비슷하다.
개발자: "UserService 책 주세요"
ClassLoader: "찾아볼게요"

사서는
- 중앙도서관(JDK)
- 공용서고(WAS 라이브러리)
- 우리 부서(내 프로젝트)
순서로 찾아본다.

</br>

### ClassLoader 종류
Java에는 기본적으로 3개의 주요 ClassLoader가 있다.
Bootstrap ClassLoader -> Platform ClassLoader -> Application ClassLoader

</br>

##### Bootstrap ClassLoader
가장 상위 ClassLoader
Java 기본 클래스를 담당한다.
ex) String, Integer, Object, System
즉) java.lang.*, java.util.*

</br>

##### Platform ClassLoader
Java 플랫폼 관련 기능 담당
보통 개발자가 직접 의식하는 경우는 많지 않다.

</br>

##### Application ClassLoader
우리가 만든 어플리케이션 담당
ex) 내 프로젝트 클래스, 외부 라이브러리 jar, SpringBoot 라이브러리

</br>


### Parent Delegation Model(부모 위임 모델)
ClassLoader의 가장 중요한 원리다. "내가 먼저 찾지 않고 부모에게 먼저 물어본다."

예를들어 String 클래스를 찾는 경우:
(Application ClassLoader) "나 String 필요해"
(Platform ClassLoader) "나는 없음"
(Bootstrap ClassLoader) "내가 가지고 있음"
Bootstrap이 String 클래스를 로딩한다.

</br>

### 왜 부모에게 먼저 물어볼까?
보안과 안정성 때문이다.
만약 누군가 프로젝트 안에 가짜 String 클래스를 만들면 위험하다
``` java
package java.lang;

public class String {
}
```
이런 가짜 클래스가 진짜 String 대신 사용되면 Java 전체가 망가질 수 있다.
그래서 Java는 안전한 클래스를 우선 사용한다.

</br>

### 왜 로컬에서는 잘 됨?
로컬에서는 보통 구조가 단순하다.
```
내 프로젝트
 ├ 내 라이브러리
 └ Embedded Tomcat
```

더 볼 것도 없이 내가 넣은 라이브러리들만 거의 사용함. (내장Tomcat도 동일)
But, 개발 또는 운영서버에서는 JEUS 기반이라면 단순히 실행만 하지 않는다
```
JEUS
 ├ 공용 라이브러리
 ├ 서버 설정
 ├ JNDI
 └ 내 애플리케이션
```

즉, 내 프로젝트 외에도 JEUS 자체 라이브러리가 존재한다.

* 이 때 충돌 발생 *
```
내 프로젝트 : jackson 2.15
JEUS 공용 : jackson 2.8
```
로컬에서 개발하면서 내 코드는 jackson 2.15 기준으로 작성되었겠지만, 실제 개발서버에 올릴 땐 JEUS 공용 라이브러리인 jackson 2.8 기준으로 실행되면서 문제 발생

보통은 NoSuchMethodError, ClassNotFoundException, ClassCastException, BeanCreationException, No qulifying bean, UnsatisfiedDependencyException 등 발생할 수 있음

</br>

### 실무에서 확인하는 방법
```java
java -verbose:class
```
위 명령어를 실행하면 어떤 jar에서 어떤 클래스가 로드됐는지 확인할 수 있다
