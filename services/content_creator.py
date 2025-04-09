import os
import yaml
from typing import Dict, Any, List
import google.generativeai as genai
from utils.logger import setup_logger

logger = setup_logger("content_creator")

class ContentCreator:
    def __init__(self):
        """ContentCreator 클래스를 초기화합니다."""
        # Google API 키 설정
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
        
        # Gemini 모델 초기화
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def _get_image_style_list(self) -> List[str]:
        """YAML 파일에서 이미지 스타일 목록을 가져옵니다."""
        try:
            with open("config/prompts/content_create.yaml", "r") as f:
                config = yaml.safe_load(f)
                image_style_guide = config.get("image_style_guide", {})
                return list(image_style_guide.keys())
        except Exception as e:
            logger.error(f"이미지 스타일 목록 로드 실패: {str(e)}")
            raise
    
    def create_content(self, video_subject: str) -> Dict[str, Any]:
        """
        주어진 주제에 대한 콘텐츠를 생성합니다.
        
        Args:
            video_subject (str): 비디오 주제
            
        Returns:
            Dict[str, Any]: 생성된 콘텐츠 정보
        """
        try:
            logger.info(f"콘텐츠 생성 시작: {video_subject}")
            
            # 이미지 스타일 목록 가져오기
            image_style_list = self._get_image_style_list()
            
            # 프롬프트 템플릿 로드
            with open("config/prompts/content_create.yaml", "r") as f:
                config = yaml.safe_load(f)
                content_prompt = config.get("content_prompt", "")
            
            # 프롬프트에 변수 대입
            prompt = content_prompt.format(
                video_subject=video_subject,
                image_style_list=image_style_list
            )
            
            # 콘텐츠 생성
            response = self.model.generate_content(prompt)
            
            logger.info("콘텐츠 생성 완료")
            return response.text
            
        except Exception as e:
            logger.error(f"콘텐츠 생성 실패: {str(e)}")
            raise 