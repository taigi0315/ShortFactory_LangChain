# 📽️ ShortFactory (LangChain Edition)

A professional YouTube Shorts generation framework built with LangChain. This tool combines AI story generation, text-to-speech narration, image generation, and video assembly to create engaging YouTube Shorts automatically.

## 🚀 Features

- AI-powered story generation using Google's Gemini Pro
- Multiple scene generation with coherent narrative flow
- High-quality text-to-speech narration with ElevenLabs (or Google Cloud TTS)
- Image generation with multiple providers (OpenAI DALL-E, Google Vertex AI Imagen)
- Automatic video assembly with seamless transitions
- Modular and extensible architecture for easy customization

## 📂 Project Structure

```
ShortFactory_LangChain/
├── docs/                     # Documentation
├── src/                      # Source code
│   ├── shortfactory/         # Main package
│   │   ├── assemblers/       # Video assembly components
│   │   ├── config/           # Configuration settings
│   │   ├── core/             # Core orchestration logic
│   │   ├── generators/       # Content generation modules
│   │   ├── models/           # Data models
│   │   └── utils/            # Utility functions
│   └── main.py               # Application entry point
├── tests/                    # Test suite
├── .env.example              # Example environment variables
├── main.py                   # Simplified entry point
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## 🛠️ Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/ShortFactory_LangChain.git
cd ShortFactory_LangChain
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
Copy `.env.example` to `.env` and configure your API keys:
```
GOOGLE_API_KEY=your_google_api_key
ELEVEN_LABS_API_KEY=your_elevenlabs_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 💻 Usage

### Basic Usage

```bash
python main.py --subject "A curious cat exploring a magical library" --scenes 5
```

### Advanced Options

```bash
python main.py \
  --subject "An astronaut discovering an alien civilization" \
  --scenes 6 \
  --tts-provider elevenlabs \
  --image-provider google_vertex_ai_image \
  --gcp-project-id your-gcp-project-id \
  --output-prefix space_adventure
```

## 🧩 Components

### Story Generator
Uses Google's Gemini Pro to create a structured story with scenes, characters, and visual descriptions.

### Narration Generator
Converts text to speech using ElevenLabs or Google Cloud TTS for high-quality narration.

### Visual Generator
Generates images for each scene using OpenAI DALL-E or Google Vertex AI Imagen.

### Video Assembler
Combines images and audio narration to create the final video with transitions.

## 🧪 Testing

Run all tests with coverage reporting:

```bash
python run_tests.py
```

Run specific test modules with verbose output:

```bash
python run_tests.py tests/test_story_generator.py -v
```

The test suite includes:

- Unit tests for all generators (story, narration, visual)
- Unit tests for the video assembler
- Integration tests for the ShortVideoFactory
- Configuration and environment variable tests

Each test is designed to run independently, using mocks for external dependencies and temporary directories for file operations.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request




# Run Command
- gcloud auth application-default set-quota-project gen-lang-client-0273830092
