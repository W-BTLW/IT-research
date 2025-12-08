# React.Memo 란 ?!

✅ 1. React에서 렌더링되면 일어나는 일

React 컴포넌트가 렌더링되면 다음 과정이 일어난다.

✔️ (1) 컴포넌트 함수 호출
내부의 모든 변수, 함수, 객체, 배열 전부 다시 생성됨
JSX도 다시 계산됨

✔️ (2) Virtual DOM 생성
새로 계산된 UI 구조를 Virtual DOM 형태로 만듦

✔️ (3) 이전 Virtual DOM과 비교(diffing)
UI에 실제 변화가 필요한지 판단

✔️ (4) 필요한 부분만 실제 DOM 업데이트
React는 최소 변경만 실제 브라우저에 반영함

포인트: 렌더링 자체는 “비싼 작업이 아님”, 실제 문제는 렌더링이 하위 컴포넌트까지 전파되는 것.

<br />
✅ 2. React.memo 동작 설명

✔️ 어떻게 동작하나?

부모가 렌더링됨
자식 컴포넌트가 렌더링될지 말지 React.memo가 체크함

props가 이전 렌더와 완전히 같으면
→ 자식 컴포넌트를 아예 다시 호출하지 않음, 어딘가 메모리영역에 저장해둔 컴포넌트를 재사용함

props가 달라졌으면
→ 자식 컴포넌트도 다시 렌더링됨

<br />
✅ 3. React.memo 남발하면 안되는 이유와 그럼에도 필요한 이유

❌ 비교 비용이 발생한다
React.memo는 렌더링을 막기 위해 props를 비교하는 비용을 쓴다.
렌더링을 막으려고 사용했지만, 오히려 비교 비용이 더 클 수 있음.
재생성 비용은 그리 크지않음

👌 자주 랜더링되는 부모가 자식에게 props를 넘기는데, 그 props가 자주 바뀌지 않을 때

👌 자식이 무겁고 렌더링 비용이 큰 컴포넌트일 때


<br />
✅ 4. 코드예시
<br />
<img width="682" height="560" alt="image" src="https://github.com/user-attachments/assets/75f8d2d4-caee-4062-bdf3-5934a39a874d" />

✔️ React.memo 적용X

<img width="1161" height="651" alt="image" src="https://github.com/user-attachments/assets/90ddb19e-91e1-4d52-a813-78a96d6fb2cf" />

✔️ React.memo 적용O

<img width="1163" height="650" alt="image" src="https://github.com/user-attachments/assets/6aa15f31-a020-4c4d-bc6d-997507f4b1e9" />


