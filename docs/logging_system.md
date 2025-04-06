# 로깅 시스템 (Logging System)

## 개요
ShortFactory의 로깅 시스템은 애플리케이션의 모든 활동을 추적하고 기록하기 위한 중앙화된 로깅 메커니즘을 제공합니다.

## 주요 기능

### 1. 중앙화된 로깅 설정
- 설정 파일(`config/config.yaml`)을 통한 로깅 설정 관리
- 로그 레벨, 포맷, 출력 대상 등을 유연하게 설정 가능

### 2. 다중 출력 지원
- 파일 로깅: 모든 로그를 파일에 기록
- 콘솔 로깅: DEBUG 모드에서 콘솔에도 출력
- 로그 로테이션: 파일 크기 기반 자동 로테이션 (기본 10MB)

### 3. 로그 레벨 관리
- DEBUG: 상세한 디버깅 정보
- INFO: 일반적인 정보성 메시지
- WARNING: 주의가 필요한 상황
- ERROR: 오류 상황
- CRITICAL: 심각한 문제 상황

## 사용 방법

### 1. 로거 인스턴스 생성
```python
from utils.logger import logger_setup

# 로거 생성
logger = logger_setup.get_logger(__name__)
```

### 2. 로그 기록
```python
# 다양한 레벨의 로그 기록
logger.debug("디버그 정보")
logger.info("일반 정보")
logger.warning("경고 메시지")
logger.error("에러 메시지")
logger.exception("예외 발생시 스택 트레이스와 함께 기록")
```

### 3. 설정 예시
```yaml
# config/config.yaml
logging:
  level: "INFO"  # 기본 로그 레벨
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
  file: "shortfactory.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
  console_logging: true
  file_logging: true
```

## 구현 세부사항

### LoggerSetup 클래스
- 싱글톤 패턴으로 구현
- 설정 파일과 환경 변수를 통한 설정 관리
- 로그 포맷터 및 핸들러 관리
- 로그 로테이션 자동화

### 로그 포맷
- 타임스탬프: 이벤트 발생 시간
- 로거 이름: 로그를 생성한 모듈/컴포넌트
- 로그 레벨: 메시지의 중요도
- 메시지: 실제 로그 내용

## 모범 사례
1. 적절한 로그 레벨 사용
2. 구조화된 로그 메시지 작성
3. 예외 처리시 exception() 메서드 활용
4. 민감한 정보는 로깅하지 않음

## 예제 코드
`examples/logging_example.py` 참조 