# Architecture Documentation

## Overview
The Shorts Gossip Generator is a LangChain-powered project that creates viral, drama-filled YouTube Shorts. The project uses a pipeline architecture where each component processes the output of the previous component to create the final video.

## Core Components

### 1. GossipChain (`chains/gossip_chain.py`)
The entry point for content generation.

**Key Components:**
- `DialogueLine` (Pydantic Model)
  - `character`: Name of the speaking character
  - `emotion`: Emotional state of the character
  - `text`: The actual dialogue text

- `GossipChain` (Main Class)
  - Uses GPT-4 to generate dramatic dialogue
  - Processes the output into structured DialogueLine objects
  - Handles prompt template management

**Flow:**
1. Loads prompt template from `prompts/gossip_prompt.txt`
2. Formats prompt with topic and format instructions
3. Calls GPT-4 for dialogue generation
4. Parses response into DialogueLine objects

### 2. AudioChain (`chains/audio_chain.py`)
Handles text-to-speech conversion using ElevenLabs API.

**Key Components:**
- Voice mapping for characters
- Emotion presets for TTS parameters
- Audio file management

**Flow:**
1. Receives DialogueLine objects
2. Maps characters to ElevenLabs voices
3. Applies emotion presets to TTS parameters
4. Generates and saves audio files
5. Returns list of audio file paths

### 3. VideoChain (`chains/video_chain.py`)
Manages video creation and composition.

**Key Components:**
- FFmpeg integration
- Audio file combination
- Subtitle overlay
- Video composition

**Flow:**
1. Combines multiple audio files
2. Adds subtitles to video
3. Merges audio with background video
4. Outputs final video file

### 4. Utility Tools

#### ElevenLabsAPI (`tools/elevenlabs.py`)
- Handles ElevenLabs API communication
- Manages API key and authentication
- Provides voice generation interface

#### FFmpegHandler (`tools/ffmpeg.py`)
- Manages FFmpeg operations
- Handles audio file combination
- Manages subtitle overlay

#### AudioUtils (`tools/audio_utils.py`)
- Provides audio file analysis
- Handles audio duration calculation
- Manages audio file operations

## Pipeline Flow

1. **Content Generation**
   ```
   User Input → GossipChain → List[DialogueLine]
   ```

2. **Audio Generation**
   ```
   List[DialogueLine] → AudioChain → List[AudioFile]
   ```

3. **Subtitle Generation**
   ```
   List[DialogueLine] + List[AudioFile] → Subtitle Generation → SRT File
   ```

4. **Video Creation**
   ```
   List[AudioFile] + SRT File + Background Video → VideoChain → Final Video
   ```

## File Structure
```
shorts-gossip-langchain/
├── chains/
│   ├── gossip_chain.py    # Dialogue generation
│   ├── audio_chain.py     # TTS processing
│   └── video_chain.py     # Video composition
├── tools/
│   ├── elevenlabs.py      # ElevenLabs API wrapper
│   ├── ffmpeg.py          # FFmpeg operations
│   └── audio_utils.py     # Audio utilities
├── prompts/
│   └── gossip_prompt.txt  # GPT prompt template
├── main.py                # Pipeline orchestration
└── requirements.txt       # Dependencies
```

## Dependencies
- LangChain: For GPT integration
- OpenAI: For text generation
- ElevenLabs: For TTS
- FFmpeg: For video processing
- Python-dotenv: For environment management
- Pydantic: For data validation

## Environment Variables
- `OPENAI_API_KEY`: For GPT access
- `ELEVENLABS_API_KEY`: For TTS access
- `DEBUG`: For debug mode
- `OUTPUT_DIR`: For output file location 