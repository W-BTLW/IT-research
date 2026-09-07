# synchronized vs ReentrantLock
 
## 1. 왜 둘 다 알아야 할까?
 
자바에서 여러 스레드가 같은 자원(변수, 컬렉션, 파일 등)에 동시에 접근하면 데이터가 꼬일 수 있습니다.
이를 막기 위한 대표적인 두 가지 방법이 `synchronized`와 `ReentrantLock`입니다.
 
비유하자면 둘 다 "화장실 문에 거는 잠금장치"입니다.
- `synchronized`: 건물에 기본으로 달려 있는 **자동 잠금장치**. 문을 열면 잠기고, 나오면 자동으로 풀립니다. 설정을 바꿀 수 없습니다.
- `ReentrantLock`: 직접 설치하는 **커스텀 잠금장치**. 언제 잠글지, 언제 풀지, 얼마나 기다릴지 세세하게 조절할 수 있습니다.
## 2. synchronized
 
```java
public synchronized void increment() {
    count++;
}
 
// 또는 블록 단위로
public void increment() {
    synchronized (this) {
        count++;
    }
}
```
 
### 특징
- JVM 레벨에서 지원하는 **키워드** (모니터 락 사용)
- 락 획득/해제가 **자동**으로 이루어짐 (메서드/블록을 벗어나면 자동 해제, 예외 발생 시에도 안전하게 해제됨)
- 코드가 간결함
- **재진입(reentrant) 가능**: 같은 스레드가 이미 가진 락을 다시 획득 가능
### 한계
- 락 획득을 **무한정 대기**함 (타임아웃 설정 불가)
- 대기 중인 스레드를 **중간에 인터럽트 불가**
- 여러 조건(Condition)을 나눠서 대기시키는 것이 불가능 (`wait()/notify()`만 가능하고, 대상 스레드를 선택적으로 깨우기 어려움)
- 락 획득 여부를 **즉시 확인(tryLock)** 할 방법이 없음
- 공정성(순서 보장) 제어 불가 — 어떤 스레드가 락을 먼저 가져갈지 보장 안 됨
## 3. ReentrantLock
 
```java
private final ReentrantLock lock = new ReentrantLock();
 
public void increment() {
    lock.lock();
    try {
        count++;
    } finally {
        lock.unlock();  // 반드시 finally에서 해제!
    }
}
```
 
### 특징 (synchronized의 한계를 보완)
1. **tryLock()**: 락을 즉시 시도하거나, 일정 시간만 기다렸다가 포기 가능
```java
   if (lock.tryLock(1, TimeUnit.SECONDS)) {
       try { ... } finally { lock.unlock(); }
   }
```
2. **lockInterruptibly()**: 락을 기다리는 도중 인터럽트로 빠져나올 수 있음
3. **공정성(fairness) 옵션**: `new ReentrantLock(true)`로 생성하면 먼저 기다린 스레드에게 우선권 부여 (단, 성능은 다소 저하됨)
4. **Condition 객체로 세밀한 제어**: 하나의 락에 여러 개의 대기 조건을 만들어, 특정 그룹의 스레드만 깨울 수 있음 (생산자-소비자 패턴에서 유용)
5. **재진입 가능**: synchronized와 동일하게 같은 스레드는 반복 획득 가능
### 주의할 점
- **명시적으로 unlock() 호출 필수** → `try-finally` 패턴을 반드시 지켜야 함. 안 그러면 데드락 위험
- synchronized보다 코드가 길어짐
- 사용이 유연한 만큼 실수할 여지도 커짐
## 4. 비교 정리
 
| 항목 | synchronized | ReentrantLock |
|---|---|---|
| 종류 | 키워드 (언어 차원 지원) | 클래스 (java.util.concurrent.locks) |
| 락 해제 | 자동 | 수동 (finally 필수) |
| 타임아웃 | 불가 | tryLock(timeout) 가능 |
| 인터럽트 | 불가 | lockInterruptibly() 가능 |
| 공정성 설정 | 불가 | 가능 (생성자 옵션) |
| 조건별 대기 | wait/notify (1개 조건) | Condition 다중 생성 가능 |
| 재진입 | 가능 | 가능 |
| 코드 복잡도 | 낮음 | 높음 |
| 성능 | 최신 JVM에서는 큰 차이 없음 (JDK 6+ 이후 최적화) | 비슷하거나 세밀한 제어 시 약간의 오버헤드 |
 
## 5. 언제 뭘 써야 할까?
 
- **synchronized**: 단순한 임계 영역 보호, 짧고 명확한 동기화가 필요할 때 → 대부분의 경우 이걸로 충분
- **ReentrantLock**: 다음 중 하나라도 필요할 때
  - 락 대기에 타임아웃이 필요할 때
  - 대기 중 인터럽트 처리가 필요할 때
  - 여러 조건으로 스레드를 나눠 깨워야 할 때 (예: 생산자-소비자)
  - 공정한 락 획득 순서가 중요할 때
## 6. 한 줄 요약
 
> **synchronized는 "간단하고 안전한 기본 잠금장치", ReentrantLock은 "복잡한 상황을 위한 정밀 제어 잠금장치"**
> 웬만하면 synchronized로 시작하고, 위 5번의 특수한 요구사항이 생기면 ReentrantLock으로 전환하자.
 
