from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from utils.config_manager import config_manager
from utils.logger import logger_setup

logger = logger_setup.get_logger(__name__)

class ContentState(str, Enum):
    """콘텐츠 상태를 정의하는 열거형"""
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    DELETED = "DELETED"

class StateTransitionError(Exception):
    """상태 전환 오류"""
    pass

class StateManager:
    """콘텐츠 상태 관리 클래스"""
    
    def __init__(self):
        """StateManager 초기화"""
        self._config = config_manager.get('status', {})
        self._history_enabled = self._config.get('history_enabled', True)
        self._max_retries = self._config.get('max_retries', 3)
        self._state_history: Dict[str, List[Dict]] = {}
    
    def initialize_content(self, content_id: str) -> None:
        """
        새로운 콘텐츠의 상태를 초기화
        
        Args:
            content_id: 콘텐츠 식별자
        """
        if content_id in self._state_history:
            logger.warning(f"콘텐츠 {content_id}는 이미 초기화되어 있습니다.")
            return
        
        self._state_history[content_id] = []
        self._add_state_record(content_id, ContentState.NEW)
        logger.info(f"콘텐츠 {content_id} 상태가 {ContentState.NEW}로 초기화되었습니다.")
    
    def get_current_state(self, content_id: str) -> Optional[ContentState]:
        """
        현재 콘텐츠의 상태를 반환
        
        Args:
            content_id: 콘텐츠 식별자
        
        Returns:
            현재 상태 또는 None (콘텐츠가 없는 경우)
        """
        if not self._state_history.get(content_id):
            return None
        return ContentState(self._state_history[content_id][-1]['state'])
    
    def get_state_history(self, content_id: str) -> List[Dict]:
        """
        콘텐츠의 상태 이력을 반환
        
        Args:
            content_id: 콘텐츠 식별자
        
        Returns:
            상태 이력 목록
        """
        return self._state_history.get(content_id, [])
    
    def transition_state(self, content_id: str, new_state: ContentState, 
                        error_message: Optional[str] = None) -> None:
        """
        콘텐츠의 상태를 전환
        
        Args:
            content_id: 콘텐츠 식별자
            new_state: 새로운 상태
            error_message: 에러 메시지 (에러 상태로 전환시)
        
        Raises:
            StateTransitionError: 잘못된 상태 전환 시도시
        """
        current_state = self.get_current_state(content_id)
        if not current_state:
            raise StateTransitionError(f"콘텐츠 {content_id}가 초기화되지 않았습니다.")
        
        # 상태 전환 유효성 검사
        if not self._is_valid_transition(current_state, new_state):
            raise StateTransitionError(
                f"잘못된 상태 전환: {current_state} -> {new_state}"
            )
        
        # 에러 상태 전환시 재시도 횟수 확인
        if new_state == ContentState.ERROR:
            error_count = sum(
                1 for record in self._state_history[content_id] 
                if record['state'] == ContentState.ERROR
            )
            if error_count >= self._max_retries:
                logger.error(f"콘텐츠 {content_id}가 최대 재시도 횟수를 초과했습니다.")
                new_state = ContentState.DELETED
        
        self._add_state_record(content_id, new_state, error_message)
        logger.info(f"콘텐츠 {content_id} 상태가 {new_state}로 변경되었습니다.")
    
    def _add_state_record(self, content_id: str, state: ContentState, 
                         error_message: Optional[str] = None) -> None:
        """
        상태 기록 추가
        
        Args:
            content_id: 콘텐츠 식별자
            state: 상태
            error_message: 에러 메시지
        """
        record = {
            'state': state,
            'timestamp': datetime.now().isoformat(),
            'error_message': error_message
        }
        
        if self._history_enabled:
            self._state_history[content_id].append(record)
        else:
            self._state_history[content_id] = [record]
    
    def _is_valid_transition(self, current_state: ContentState, 
                           new_state: ContentState) -> bool:
        """
        상태 전환의 유효성 검사
        
        Args:
            current_state: 현재 상태
            new_state: 새로운 상태
        
        Returns:
            상태 전환 가능 여부
        """
        # 상태 전환 규칙 정의
        valid_transitions = {
            ContentState.NEW: {
                ContentState.IN_PROGRESS, 
                ContentState.ERROR, 
                ContentState.DELETED
            },
            ContentState.IN_PROGRESS: {
                ContentState.COMPLETE, 
                ContentState.ERROR, 
                ContentState.DELETED
            },
            ContentState.ERROR: {
                ContentState.IN_PROGRESS, 
                ContentState.DELETED
            },
            ContentState.COMPLETE: {
                ContentState.DELETED
            },
            ContentState.DELETED: set()  # 삭제된 상태에서는 전환 불가
        }
        
        return new_state in valid_transitions[current_state]

# 싱글톤 인스턴스
state_manager = StateManager() 