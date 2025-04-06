# ShortFactory 개발 계획

## 1. 현재 구현된 기능 (Fetch Process)
- Reddit에서 이야기 가져오기
- Google Sheet 업데이트
- 카테고리별 데이터 관리
- 중복 체크
- 상태 관리 (기본)

## 2. 개발 단계

### Phase 1: 기본 구조 설정
- [ ] 설정 파일 구조 생성
  - `config/` 디렉토리 생성
  - `config.yaml` 기본 설정 파일 작성
  - 환경 변수와 설정 파일 통합 관리
- [ ] 로깅 시스템 구현
  - 로그 레벨 설정
  - 로그 포맷 정의
  - 로그 파일 관리
- [ ] 상태 관리 시스템 개선
  - 상태 정의 (New, In Progress, Complete, Error)
  - 상태 변경 이력 추적
  - 에러 처리 및 복구 메커니즘

### Phase 2: Create Process 구현
- [ ] Google Sheet 읽기 기능 구현
  - 'New' 상태 게시물 필터링
  - 데이터 검증
- [ ] LangChain 통합
  - 프롬프트 템플릿 설계
  - Chain 구성 (요약 -> 대화형 변환 -> 감정 추가)
  - 결과 검증 및 품질 관리
- [ ] 결과물 저장 시스템
  - 새로운 워크시트 생성
  - 메타데이터 관리
  - 버전 관리

### Phase 3: 프로세스 자동화
- [ ] Fetch Process 자동화
  - 스케줄링 시스템 구현
  - 에러 복구 메커니즘
  - 상태 모니터링
- [ ] Create Process 자동화
  - 작업 큐 시스템 구현
  - 병렬 처리 지원
  - 리소스 관리

### Phase 4: 품질 관리 및 최적화
- [ ] 테스트 시스템 구축
  - 단위 테스트
  - 통합 테스트
  - 성능 테스트
- [ ] 모니터링 시스템
  - 성능 메트릭 수집
  - 알림 시스템
  - 대시보드 구현
- [ ] 최적화
  - 성능 개선
  - 리소스 사용 최적화
  - 비용 최적화

## 3. 기술 스택
- Python 3.12+
- LangChain
- OpenAI GPT-4
- Google Sheets API
- Reddit API (PRAW)
- PyYAML
- Logging
- pytest

## 4. 디렉토리 구조
```
ShortFactory/
├── config/
│   ├── config.yaml
│   └── templates/
├── tools/
│   ├── reddit_fetcher.py
│   ├── sheet_manager.py
│   └── content_creator.py
├── utils/
│   ├── logger.py
│   ├── state_manager.py
│   └── validators.py
├── chains/
│   ├── summarizer.py
│   ├── dialogue_converter.py
│   └── emotion_adder.py
├── scripts/
│   ├── fetch_stories.py
│   └── create_shorts.py
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    ├── development_plan.md
    └── api_documentation.md
```

## 5. 다음 단계 (브랜치 생성 계획)
1. `feature/config-system`: 설정 파일 시스템 구현
2. `feature/logging-system`: 로깅 시스템 구현
3. `feature/state-management`: 상태 관리 시스템 개선
4. `feature/content-creator`: Create Process 핵심 기능 구현
5. `feature/automation`: 자동화 시스템 구현
6. `feature/monitoring`: 모니터링 시스템 구현

## 6. 예상 타임라인
- Phase 1: 1-2주
- Phase 2: 2-3주
- Phase 3: 1-2주
- Phase 4: 1-2주

총 예상 개발 기간: 5-9주 