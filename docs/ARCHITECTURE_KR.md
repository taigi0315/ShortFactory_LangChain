# 아키텍처 문서

## 개요
Shorts Gossip Generator는 LangChain을 활용하여 바이럴이 될 수 있는 드라마틱한 YouTube Shorts를 생성하는 프로젝트입니다. 파이프라인 아키텍처를 사용하여 각 컴포넌트가 이전 컴포넌트의 출력을 처리하여 최종 비디오를 생성합니다.

## 핵심 컴포넌트

### 1. GossipChain (`chains/gossip_chain.py`)
콘텐츠 생성을 위한 진입점입니다.

**주요 구성요소:**
- `DialogueLine` (Pydantic 모델)
  - `character`: 대화를 하는 캐릭터 이름
  - `emotion`: 캐릭터의 감정 상태
  - `text`: 실제 대화 텍스트

- `GossipChain` (메인 클래스)
  - GPT-4를 사용하여 드라마틱한 대화 생성
  - 출력을 구조화된 DialogueLine 객체로 처리
  - 프롬프트 템플릿 관리

**작동 흐름:**
1. `prompts/gossip_prompt.txt`에서 프롬프트 템플릿 로드
2. 주제와 형식 지침으로 프롬프트 포맷팅
3. GPT-4 호출하여 대화 생성
4. 응답을 DialogueLine 객체로 파싱

### 2. AudioChain (`chains/audio_chain.py`)
ElevenLabs API를 사용한 텍스트-음성 변환을 처리합니다.

**주요 구성요소:**
- 캐릭터별 음성 매핑
- TTS 파라미터를 위한 감정 프리셋
- 오디오 파일 관리

**작동 흐름:**
1. DialogueLine 객체 수신
2. 캐릭터를 ElevenLabs 음성으로 매핑
3. TTS 파라미터에 감정 프리셋 적용
4. 오디오 파일 생성 및 저장
5. 오디오 파일 경로 리스트 반환

### 3. VideoChain (`chains/video_chain.py`)
비디오 생성과 합성을 관리합니다.

**주요 구성요소:**
- FFmpeg 통합
- 오디오 파일 결합
- 자막 오버레이
- 비디오 합성

**작동 흐름:**
1. 여러 오디오 파일 결합
2. 비디오에 자막 추가
3. 오디오와 배경 비디오 병합
4. 최종 비디오 파일 출력

### 4. 유틸리티 도구

#### ElevenLabsAPI (`tools/elevenlabs.py`)
- ElevenLabs API 통신 처리
- API 키 및 인증 관리
- 음성 생성 인터페이스 제공

#### FFmpegHandler (`tools/ffmpeg.py`)
- FFmpeg 작업 관리
- 오디오 파일 결합 처리
- 자막 오버레이 관리

#### AudioUtils (`tools/audio_utils.py`)
- 오디오 파일 분석 제공
- 오디오 길이 계산 처리
- 오디오 파일 작업 관리

## 파이프라인 흐름

1. **콘텐츠 생성**
   ```
   사용자 입력 → GossipChain → List[DialogueLine]
   ```

2. **음성 생성**
   ```
   List[DialogueLine] → AudioChain → List[AudioFile]
   ```

3. **자막 생성**
   ```
   List[DialogueLine] + List[AudioFile] → 자막 생성 → SRT 파일
   ```

4. **비디오 생성**
   ```
   List[AudioFile] + SRT 파일 + 배경 비디오 → VideoChain → 최종 비디오
   ```

## 파일 구조
```
shorts-gossip-langchain/
├── chains/
│   ├── gossip_chain.py    # 대화 생성
│   ├── audio_chain.py     # TTS 처리
│   └── video_chain.py     # 비디오 합성
├── tools/
│   ├── elevenlabs.py      # ElevenLabs API 래퍼
│   ├── ffmpeg.py          # FFmpeg 작업
│   └── audio_utils.py     # 오디오 유틸리티
├── prompts/
│   └── gossip_prompt.txt  # GPT 프롬프트 템플릿
├── main.py                # 파이프라인 조정
└── requirements.txt       # 의존성
```

## 의존성
- LangChain: GPT 통합용
- OpenAI: 텍스트 생성용
- ElevenLabs: TTS용
- FFmpeg: 비디오 처리용
- Python-dotenv: 환경 관리용
- Pydantic: 데이터 검증용

## 환경 변수
- `OPENAI_API_KEY`: GPT 접근용
- `ELEVENLABS_API_KEY`: TTS 접근용
- `DEBUG`: 디버그 모드용
- `OUTPUT_DIR`: 출력 파일 위치 