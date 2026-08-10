# @Transactional 정리

## 1. 선언적 트랜잭션이란?
@Transactional을 붙이면 스프링이 프록시 객체를 만들어서, 메서드 실행 후 예외 없으면 `commit`, 런타임 예외 발생 시 `rollback`을 자동으로 처리해준다.

```java
@Service
public class MemberService {

    @Transactional
    public void addMember(MemberDto memberDto) throws Exception {
        // 멤버 삽입 로직
    }
}
```

⭐️주의 : self-invocation 문제 프록시는 외부 호출만 가로챈다. 같은 클래스 안에서 `this.addMember()`처럼 내부 호출하면 프록시를 안 거쳐서 `@Transactional`이 아예 무시된다.

-> 트랜잭션 필요한 로직은 별도 빈으로 분리해야 함.

<br><br>

## 2. 주요 옵션

### isolation (격리 수준)

isolation은 ***"내 트랜잭션이 다른 트랜잭션의 변경 상황을 얼마나 허용하고 볼 것이냐"***를 정하는 옵션이다. 허용 범위를 넓히면(낮은 레벨) 성능은 좋아지지만 아래 3가지 문제가 순서대로 생길 수 있고, 좁히면(높은 레벨) 안전해지는 대신 느려진다.

| 레벨 | 방지하는 문제 | 남는 문제 | 
| --- | --- | --- |
| READ_UNCOMMITTED | - | Dirty Read |
| READ_COMMITTED | Dirty Read | Non-Repeatable Read |
| REPEATABLE_READ | Non-Repeatable Read | Phantom Read |
| SERIALIZABLE | Phantam Read | 성능 저하 (동시성↓) |

- Dirty Read (READ_UNCOMMITTED에서 발생) : A가 데이터를 1->2로 변경 중 (아직 커밋 전)인데, B가 그 값(2)을 읽어버림. 이후 A가 롤백하면 B는 존재한 적도 없는 값을 읽은 셈이 됨
- Non-Repeatable Read (READ_COMMITTED에서 발생) : A가 트랜잭션 안에서 1번 row를 조회 -> 그 사이 B가 1번 row를 수정하고 커밋 -> A가 같은 트랜잭션에서 1번 row를 다시 조회하면 값이 바뀌어 있음. 한 트랜잭션 안에서 "같은 값"이 보장되지 않는 문제.
- Phantom Read (REPEATABLE_READ에서 발생) : A가 트랜잭션 안에서 [1, 2, 3, 4] 범위를 조회 -> 그 사이 B가 [5] row를 추가하고 커밋 -> A가 같은 조건으로 다시 조회하면 [1, 2, 3, 4, 5]가 나옴. row의 "값"이 아니라 "개수/범위"가 바뀌는 문제라 REPEATABLE_READ(row 자체엔 락을 걸지만 새로 추가되는 row까진 막지 못함)로도 못 막는다.

<br>
=> 격리 수준이 높을수록 안전하지만 느려진다. 보통 DB 기본값 (대부분 READ_COMMITTED) 그대로 쓰고, 정합성이 중요한 로직에만 올린다.

<br><br>


### propagation (전파 방식)

| 옵션 | 설명 |
| --- | --- |
| REQUIRED (기본) | 진행 중인 트랜잭션 있으면 참여, 없으면 새로 생성 |
| REQUIRES_NEW | 무조건 새 트랜잭션 생성 (기존 트랜잭션은 잠시 보류) |
| SUPPORTS | 있으면 참여, 없으면 트랜잭션 없이 진행 |
| MANDATORY | 반드시 기존 트랜잭션 필요, 없으면 예외 |
| NOT_SUPPORTED | 트랜잭션 없이 실행 (기존 건 보류) |
| NEVER | 트랜잭션 있으면 예외 발생 |
| NESTED | 기존 트랜잭션 안에 Savepoint로 중첩 실행 (부분 롤백 가능) |

<br>
=> REQUIRED vs REQUIRES_NEW : REQUIRED는 부모와 트랜잭션을 공유해서 자식이 실패하면 부모도 같이 롤백된다. REQUIRES_NEW는 완전히 별개 트랜잭션이라 자식만 롤백되고 부모는 영향 없을 수 있다. 
(예: 로그 저장은 REQUIRES_NEW로 분리해서 주문 실패해도 로그는 남기는 식)

<br><br>

### rollbackFor / noRollbackFor

기본적으로 런타임 예외 -> 롤백, 체크 예외 -> 커밋된다. 이 기반 동작을 바꾸는 옵션

※ 체크 예외 : Exception을 상속하지만 RuntimeException은 아닌 예외 (예 : IOException, SQLException)

``` java
@Transactional(rollbackFor = CustomCheckedException.class) //체크 예외도 롤백시키고 싶을 때
```

<br><br>

### timeout / readOnly
- `timeout` : 지정 시간(초) 안에 안 끝나면 롤백.
- `readOnly = true` : 조회 전용 트랜잭션. 성능 최적화 힌트로 쓰이며, 관례적으로 get / find 메서드에 붙임. (단, 쓰기 작업을 100% 막아주는 건 아니고 DB/드라이버마다 다름)

<br><br>

## 핵심 요약
1. `@Transactional`은 프록시 기반 -> 같은 클래스 내부 호출엔 적용 안됨
2. 기본은 런타임 예외만 롤백, 체크 예외는 커밋됨 -> `rollbackFor`로 조정 가능
3. `REQUIRES_NEW`(완전 별개 트랜잭션) vs `NESTED`(Savepoint 기반 부분 롤백) 구분하기
