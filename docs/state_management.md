# 상태 관리 시스템 (State Management System)

## 개요
ShortFactory의 상태 관리 시스템은 콘텐츠의 생명주기를 추적하고 관리하기 위한 강력한 상태 기계(State Machine)를 제공합니다.

## 주요 기능

### 1. 콘텐츠 상태 관리
각 콘텐츠는 다음 상태 중 하나를 가집니다:
- `NEW`: 새로 생성된 콘텐츠
- `IN_PROGRESS`: 현재 처리 중인 콘텐츠
- `COMPLETE`: 처리가 완료된 콘텐츠
- `ERROR`: 처리 중 오류가 발생한 콘텐츠
- `DELETED`: 삭제된 콘텐츠

### 2. 상태 전환 규칙
유효한 상태 전환만 허용됩니다:
```
NEW → IN_PROGRESS, ERROR, DELETED
IN_PROGRESS → COMPLETE, ERROR, DELETED
ERROR → IN_PROGRESS, DELETED
COMPLETE → DELETED
DELETED → (전환 불가)
```

### 3. 상태 이력 관리
- 모든 상태 변경을 시간순으로 기록
- 각 상태 변경에 대한 메타데이터 저장
- 에러 메시지 및 상태 변경 사유 기록

### 4. 오류 처리 및 재시도
- 최대 재시도 횟수 설정 가능
- 재시도 횟수 초과시 자동으로 DELETED 상태로 전환
- 각 오류 발생 시 상세 정보 기록

## 사용 방법

### 1. 상태 관리자 사용
```python
from utils.state_manager import state_manager, ContentState

# 콘텐츠 초기화
state_manager.initialize_content("content_123")

# 상태 전환
state_manager.transition_state("content_123", ContentState.IN_PROGRESS)

# 현재 상태 확인
current_state = state_manager.get_current_state("content_123")

# 상태 이력 조회
history = state_manager.get_state_history("content_123")
```

### 2. 설정 예시
```yaml
# config/config.yaml
status:
  states:
    - NEW
    - IN_PROGRESS
    - COMPLETE
    - ERROR
    - DELETED
  history_enabled: true
  max_retries: 3
```

## 구현 세부사항

### StateManager 클래스
- 싱글톤 패턴으로 구현
- 스레드 안전한 상태 관리
- 설정 기반의 동작 방식
- 로깅 시스템과 통합

### 상태 기록 구조
```python
{
    'state': ContentState,
    'timestamp': ISO8601 시간,
    'error_message': Optional[str]
}
```

### 예외 처리
- `StateTransitionError`: 잘못된 상태 전환 시도시 발생
- 최대 재시도 횟수 초과 처리
- 초기화되지 않은 콘텐츠 접근 처리

## 모범 사례
1. 상태 전환 전 유효성 검증
2. 에러 상태 전환시 상세 메시지 포함
3. 상태 이력 주기적 모니터링
4. 장기 ERROR 상태 콘텐츠 관리

## 예제 코드
`examples/state_management_example.py` 참조

## 상태 다이어그램
```
[NEW] ──────┐
   │        │
   ↓        ↓
[IN_PROGRESS] ←─── [ERROR]
   │               │
   ↓               │
[COMPLETE]         │
   │               │
   ↓               ↓
  [DELETED] ←──────┘
``` 