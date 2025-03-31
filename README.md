# 📽️ Shorts Gossip Generator (LangChain Edition)

YouTube Shorts를 위한 자동화된 드라마틱한 대화 생성기입니다. GPT, 감정 TTS, 자막, 비디오 편집을 결합하여 바이럴이 될 수 있는 쇼츠를 생성합니다.

## 🚀 기능

- GPT를 사용한 감정이 담긴 드라마틱한 대화 생성
- ElevenLabs를 활용한 감정이 담긴 음성 합성
- 자동 자막 생성 및 타이밍 조정
- 배경 비디오와 오디오, 자막을 결합한 최종 YouTube Shorts 생성

## 🛠️ 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/yourusername/shorts-gossip-langchain.git
cd shorts-gossip-langchain
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 생성하고 다음 변수들을 설정하세요:
```
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

## 💻 사용 방법

```bash
python main.py
```

## 🧪 테스트

```bash
python -m pytest tests/
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 