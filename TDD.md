# 📽️ Shorts Gossip Generator (LangChain Edition)

A LangChain-powered project to automatically generate viral, drama-filled YouTube Shorts using GPT, emotional TTS, subtitles, and video stitching.

---

## 🎯 Goal

To build an automated pipeline that:
- Generates emotionally-charged, gossip-style dialogue between two fictional characters
- Synthesizes voiceovers for each dialogue line using ElevenLabs (emotion-aware)
- Generates perfectly timed subtitles (SRT)
- Combines audio, subtitles, and visual elements into a ready-to-upload YouTube Shorts video

---

## 🧩 Project Architecture

```
User Input (optional: topic) ─▶ LangChain → GPT Dialogue
                               └──────────→ JSON {character, emotion, text}

          ↓

  [For each line]
    └→ TTS (ElevenLabs)
    └→ Duration → Subtitle

          ↓

     FFmpeg Merge
      (audio + subtitles + background video)

          ↓

      Final .mp4 Shorts
```

---

## 🧱 Modules

### 1. `gossip_chain.py`
- Uses LangChain `PromptTemplate`, `ChatOpenAI`, and `StructuredOutputParser`
- Generates dialogue in JSON format:
```json
[
  {
    "character": "Amber",
    "emotion": "shocked",
    "text": "Wait — she invited her ex to her birthday?!"
  },
  ...
]
```

### 2. `audio_chain.py`
- For each line, calls ElevenLabs API with:
  - Voice ID (based on character)
  - Stability / Style (based on emotion)
- Saves `.mp3` for each line

### 3. `subtitle_chain.py`
- Measures `.mp3` duration for each line
- Generates `.srt` subtitles timed to the audio

### 4. `video_chain.py`
- Uses FFmpeg to:
  - Combine background video + TTS audio + `.srt` subtitles
  - Output `.mp4` suitable for YouTube Shorts

---

## 👥 Character Voice Map

| Character | Role           | Voice ID (ElevenLabs) |
|-----------|----------------|------------------------|
| Amber     | main_female    | Rachel                 |
| Jade      | support_female | Bella                  |
| Liam      | main_male      | Adam                   |
| Noah      | support_male   | Antoni                 |

---

## 💬 Emotion Presets (for TTS tuning)

| Emotion     | Stability | Style |
|-------------|-----------|--------|
| shocked     | 0.3       | 0.8    |
| calm        | 0.8       | 0.2    |
| angry       | 0.4       | 0.9    |
| snarky      | 0.6       | 0.6    |
| sad         | 0.7       | 0.5    |
| excited     | 0.5       | 0.9    |
| defensive   | 0.6       | 0.4    |
| frustrated  | 0.5       | 0.7    |
| pause       | 1.0       | 1.0    |

---

## 🗃️ File Structure

```
shorts-gossip-langchain/
├── chains/
│   ├── gossip_chain.py
│   ├── audio_chain.py
│   └── video_chain.py
├── tools/
│   ├── elevenlabs.py
│   ├── ffmpeg.py
│   └── audio_utils.py
├── prompts/
│   └── gossip_prompt.txt
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
```

---

## 🚀 Future Plans

- Integrate LangServe for API endpoint
- Add UI with Streamlit
- Auto-select trending topics
- Add character memory/personality system
