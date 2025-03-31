from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser
from pydantic import BaseModel
from typing import List
import os
from pathlib import Path
from utils.logger import setup_logger

# 로거 설정
logger = setup_logger("gossip_chain")

class DialogueLine(BaseModel):
    character: str
    emotion: str
    text: str

class GossipChain:
    def __init__(self):
        logger.info("GossipChain 초기화 중...")
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7
        )
        self.parser = StructuredOutputParser.from_pydantic_object(DialogueLine)
        
        # 프롬프트 템플릿 로드
        prompt_path = Path(__file__).parent.parent / "prompts" / "gossip_prompt.txt"
        logger.debug(f"프롬프트 템플릿 로드: {prompt_path}")
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["topic"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        logger.info("GossipChain 초기화 완료")
    
    def generate_dialogue(self, topic: str = None) -> List[DialogueLine]:
        """
        주어진 주제에 대한 드라마틱한 대화를 생성합니다.
        
        Args:
            topic (str, optional): 대화의 주제. 기본값은 None입니다.
            
        Returns:
            List[DialogueLine]: 생성된 대화 라인들의 리스트
        """
        if topic is None:
            topic = "일상적인 드라마"
            logger.warning("주제가 지정되지 않아 기본 주제 사용")
            
        logger.info(f"대화 생성 시작 - 주제: {topic}")
        
        # 프롬프트 생성
        formatted_prompt = self.prompt.format(topic=topic)
        logger.debug("프롬프트 생성 완료")
        
        # LLM 호출
        logger.debug("GPT-4 호출 중...")
        response = self.llm.invoke(formatted_prompt)
        logger.debug("GPT-4 응답 수신")
        
        # 응답 파싱
        logger.debug("응답 파싱 중...")
        dialogue = self.parser.parse(response.content)
        logger.info(f"대화 생성 완료 - {len(dialogue)}개의 대화 라인")
        
        return dialogue 