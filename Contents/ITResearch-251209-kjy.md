## forEach()와 map()의 공통점

| 공통점 | 설명 |
| --- | --- |
| 둘 다 배열의 각 요소를 순회한다 | callback 함수를 이용해 배열의 각 요소에 접근 |
| 인덱스, 요소, 배열 전체를 인자로 받을 수 있다 | `(element, index, array)` |
| 원본 배열을 변경하지 않는다 (단, callback에서 직접 수정하면 변경됨) | 순수하게 순회 기능 제공 |

## forEach()와 map의 차이점

### forEach()

- 반환값 없음(아무것도 리턴하지 않음)

```jsx
const arr = [1, 2, 3];

const a = arr.forEach(x => x * 2); 
console.log(a); // undefined
```

- 콜백 함수에서 호출된 배열 변경 가능

```jsx
const arr = [1, 2, 3];

arr.forEach((value, index, array) => {
  array[index] = value * 10;  // 원본 배열 직접 수정
});

console.log(arr); 
// [10, 20, 30]  ← 원본 배열이 실제로 변경됨
```

### map()

- 새로운 배열을 생성(리턴)

```jsx
const arr = [1, 2, 3];

const b = arr.map(x => x * 2);
console.log(b); // [2, 4, 6]
```

- map에서는 원본 배열이 자동 변경되지 않음

```jsx
const arr = [1, 2, 3];
const newArr = arr.map(x => x * 10);

console.log(arr);    // [1, 2, 3]  ← 원본 유지
console.log(newArr); // [10, 20, 30]
```

## 결론

- 성능 차이는 거의 동일하나, map은 반드시 새로운 배열을 만들기 때문에 상황에 따라 비효율적일 수 있음
- forEach() 가 필요할 때
    - 결과 배열이 필요 없고 순회하면서 부수 효과만 필요한 경우
- map() 이 필요할 때
    - 기존 배열을 변환한 새로운 배열을 만들어야 하는 경우