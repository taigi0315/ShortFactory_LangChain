import os
import requests
from typing import Optional
from utils.logger import setup_logger

# 로거 설정
logger = setup_logger("elevenlabs_api")

class ElevenLabsAPI:
    def __init__(self):
        logger.info("ElevenLabsAPI 초기화 중...")
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.error("ELEVENLABS_API_KEY가 설정되지 않았습니다")
            raise ValueError("ELEVENLABS_API_KEY가 필요합니다")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        logger.info("ElevenLabsAPI 초기화 완료")
    
    def generate_speech(
        self,
        text: str,
        voice_id: str,
        emotion: Optional[str] = None,
        speed: float = 1.0
    ) -> bytes:
        """
        텍스트를 음성으로 변환합니다.
        
        Args:
            text (str): 변환할 텍스트
            voice_id (str): 사용할 음성 ID
            emotion (Optional[str]): 감정 설정
            speed (float): 음성 속도
            
        Returns:
            bytes: 생성된 음성 데이터
        """
        logger.info(f"음성 생성 시작 - 텍스트: {text[:50]}...")
        logger.debug(f"음성 설정: voice_id={voice_id}, emotion={emotion}, speed={speed}")
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        if emotion:
            data["voice_settings"]["style"] = self._get_emotion_value(emotion)
        
        if speed != 1.0:
            data["voice_settings"]["speaking_rate"] = speed
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            logger.debug("음성 생성 완료")
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"음성 생성 실패: {str(e)}")
            raise
    
    def _get_emotion_value(self, emotion: str) -> float:
        """
        감정 문자열을 ElevenLabs API의 스타일 값으로 변환합니다.
        
        Args:
            emotion (str): 감정 문자열
            
        Returns:
            float: 스타일 값
        """
        emotion_map = {
            "happy": 0.5,
            "sad": -0.5,
            "angry": 0.8,
            "excited": 0.7,
            "calm": -0.3,
            "neutral": 0.0
        }
        
        value = emotion_map.get(emotion.lower(), 0.0)
        logger.debug(f"감정 변환: {emotion} -> {value}")
        return value 