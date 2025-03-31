from pathlib import Path
import os
from typing import List
from tools.elevenlabs_api import ElevenLabsAPI
from utils.logger import setup_logger

# 로거 설정
logger = setup_logger("audio_chain")

class AudioChain:
    def __init__(self):
        logger.info("AudioChain 초기화 중...")
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.error("ELEVENLABS_API_KEY가 설정되지 않았습니다")
            raise ValueError("ELEVENLABS_API_KEY가 필요합니다")
        
        self.voice_map = {
            "Amber": "Rachel",
            "Jade": "Bella",
            "Liam": "Adam",
            "Noah": "Antoni"
        }
        
        self.emotion_presets = {
            "shocked": {"stability": 0.3, "style": 0.8},
            "calm": {"stability": 0.8, "style": 0.2},
            "angry": {"stability": 0.4, "style": 0.9},
            "snarky": {"stability": 0.6, "style": 0.6},
            "sad": {"stability": 0.7, "style": 0.5},
            "excited": {"stability": 0.5, "style": 0.9},
            "defensive": {"stability": 0.6, "style": 0.4},
            "frustrated": {"stability": 0.5, "style": 0.7},
            "pause": {"stability": 1.0, "style": 1.0}
        }
        
        # 출력 디렉토리 생성
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.elevenlabs = ElevenLabsAPI()
        logger.info("AudioChain 초기화 완료")
    
    def generate_dialogue_audio(self, dialogue: List[dict]) -> List[str]:
        """
        대화를 음성으로 변환합니다.
        
        Args:
            dialogue (List[dict]): 대화 라인들의 리스트
            
        Returns:
            List[str]: 생성된 오디오 파일 경로들의 리스트
        """
        logger.info(f"음성 생성 시작 - {len(dialogue)}개의 대화 라인")
        
        audio_files = []
        
        for i, line in enumerate(dialogue):
            logger.info(f"음성 생성 중... ({i+1}/{len(dialogue)})")
            logger.debug(f"대화 라인: {line}")
            
            # 음성 ID 매핑
            voice_id = self.voice_map.get(line["character"], "Rachel")
            
            # 감정 설정 가져오기
            emotion = line["emotion"]
            emotion_settings = self.emotion_presets.get(emotion, {"stability": 0.5, "style": 0.5})
            
            # 음성 생성
            audio_data = self.elevenlabs.generate_speech(
                text=line["text"],
                voice_id=voice_id,
                emotion=emotion,
                speed=1.0
            )
            
            # 파일 저장
            output_file = self.output_dir / f"line_{i+1}.mp3"
            with open(output_file, "wb") as f:
                f.write(audio_data)
            
            audio_files.append(str(output_file))
            logger.debug(f"음성 파일 저장 완료: {output_file}")
        
        logger.info(f"음성 생성 완료 - {len(audio_files)}개의 파일")
        return audio_files 