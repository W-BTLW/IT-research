**1️⃣ e.preventDefault()**
👉 브라우저 기본 동작(링크 이동, 폼 제출 등)을 막음
<img width="868" height="452" alt="image" src="https://github.com/user-attachments/assets/2e0a509c-dcac-452d-bbca-7efa079dae5a" />
- 원래는 클릭하면 https://google.com 으로 이동해야 함.
- 하지만 e.preventDefault() 때문에 링크 이동 X

**2️⃣ e.stopPropagation()**
👉 이벤트가 부모로 전파(버블링)되는 걸 막음
<img width="1057" height="593" alt="image" src="https://github.com/user-attachments/assets/3f17876e-50a8-4ab0-96d1-12303555de6e" />

캡처링(Capturing)은 이벤트가 위에서 아래로 전파되는 과정으로, 기본적으로는 잘 사용되지 않지만 보안상 특정 이벤트를 미리 가로채거나, 하위 요소에서 이벤트를 처리하기 전에 제어해야 하는 상황에서 활용된다.
반면에, 버블링(Bubbling)은 이벤트가 아래에서 위로 전파되는 과정이며, 자바스크립트의 기본 이벤트 흐름으로 대부분의 UI 이벤트 처리(예: 클릭, 입력 등)가 이 단계에서 이루어짐

<img width="860" height="560" alt="image" src="https://github.com/user-attachments/assets/ab18f4d2-384f-4e4e-9b3d-54fc2181e772" />

- 자바스크립트의 이벤트는 가장 하위 뎁스의 엘리먼트부터 실행되고 상위로 전파되는 방식으로 실행됨
- 버튼 클릭 시 원래는 자식 버튼 클릭됨 →부모 div 클릭됨 순서로 실행되어야 함
- 하지만 stopPropagation() 때문에 부모 이벤트 실행 X


👉 즉
- 폼 제출, 링크 이동 등 브라우저 동작 제어 = preventDefault()
- 이벤트 핸들러 실행 제어 (부모/상위) = stopPropagation()

**e.preventDefault() + e.stopPropagation()가 쓰이는경우**
<img width="683" height="692" alt="image" src="https://github.com/user-attachments/assets/ea1e4a1c-c1e7-4709-9a23-d1acadc1e95d" />

🔎 동작 설명
1. label 클릭 시 원래는 input check 가 체크/언체크됨. → e.preventDefault() 로 막음.
2. 동시에 label 의 클릭 이벤트가 div 로 전파되어 부모 div 클릭됨 alert 가 떠야 함. → e.stopPropagation() 으로 막음.
3. 따라서 라벨 클릭 시 체크박스도 안 바뀌고, 부모 이벤트도 실행되지 않음.
