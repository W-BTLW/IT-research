# 🌊 Next.js 하이드레이션(Hydration) 오류 및 방어 가이드

## 1. 하이드레이션(Hydration)이란?
서버 사이드 렌더링(SSR) 결과물인 **정적 HTML** 위에 자바스크립트를 실행하여, 리액트 컴포넌트의 이벤트 리스너와 상태(State)를 결합하는 과정을 말합니다.



## 2. 오류 발생 원인 (Mismatch)
서버에서 만든 HTML과 클라이언트 브라우저가 첫 렌더링 시점에 그린 HTML이 일치하지 않을 때 발생합니다.

* **브라우저 API 참조**: 서버에는 없는 `window`, `localStorage`, `document` 등을 컴포넌트 본문 내에서 직접 호출할 때.
* **휘발성 데이터 사용**: 서버와 클라이언트의 시간대가 다르거나 `Math.random()` 값이 일치하지 않을 때.
* **비정상적인 HTML 구조**: `<p>` 안에 `<div>`를 넣는 등 웹 표준에 어긋난 태그 중첩 시 브라우저가 자동으로 구조를 교정하면서 불일치가 발생.

---

## 3. 하이드레이션 오류 방어 전략 (Solutions)

### ✅ 방법 1: `useEffect`를 이용한 마운트 체크
가장 표준적인 방법으로, 컴포넌트가 브라우저에 안착(Mount)한 이후에만 클라이언트 전용 로직이 실행되도록 제어합니다.

```javascript
import { useState, useEffect } from 'react';

export default function SafeComponent() {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null; // 마운트 전에는 빈 화면 혹은 스켈레톤 노출

  return <div>브라우저에서만 보이는 정보: {window.location.href}</div>;
}
```

### ✅ 방법 2: Next.js Dynamic Import (No SSR)
특정 컴포넌트가 브라우저 전용 라이브러리를 많이 사용하거나 서버 렌더링이 아예 불가능할 때 사용합니다.
```javascript
import dynamic from 'next/dynamic';

// 해당 컴포넌트를 SSR 단계에서 제외
const NoSSRComponent = dynamic(() => import('./ClientOnlyView'), {
  ssr: false,
});

export default function Page() {
  return <NoSSRComponent />;
}
```

### ✅ 방법 3: suppressHydrationWarning 속성 활용
날짜, 시간 등 서버와 클라이언트의 값이 미세하게 다를 수밖에 없는 경우, 해당 태그에 한해 경고를 끄고 클라이언트 값으로 덮어씌웁니다.
```javascript
export default function Clock() {
  return (
    <div suppressHydrationWarning>
      {/* 초 단위 불일치 경고를 무시함 */}
      현재 시간: {new Date().toLocaleTimeString()}
    </div>
  );
}
```

## 💡 결론: 가급적 방법 1(useEffect)을 권장하며, 서드파티 라이브러리 충돌이 심할 경우 방법 2(dynamic)를, 단순히 텍스트 차이만 발생하는 경우에는 방법 3을 선택하는 것이 좋습니다.
