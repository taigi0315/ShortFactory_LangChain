from utils.logger import logger_setup
from utils.state_manager import ContentState, StateTransitionError, state_manager

logger = logger_setup.get_logger(__name__)

def main():
    # 콘텐츠 ID 생성
    content_id = "test_content_123"
    
    try:
        # 콘텐츠 상태 초기화
        logger.info("콘텐츠 상태 초기화")
        state_manager.initialize_content(content_id)
        
        # 현재 상태 확인
        current_state = state_manager.get_current_state(content_id)
        logger.info(f"현재 상태: {current_state}")
        
        # IN_PROGRESS로 전환
        logger.info("처리 중 상태로 전환")
        state_manager.transition_state(content_id, ContentState.IN_PROGRESS)
        
        # 에러 상태로 전환 (재시도 테스트)
        logger.info("에러 상태로 전환")
        for i in range(4):  # 최대 재시도 횟수(3) 초과
            state_manager.transition_state(
                content_id, 
                ContentState.ERROR,
                f"테스트 에러 #{i+1}"
            )
            if i < 3:  # 마지막 반복을 제외하고 IN_PROGRESS로 재시도
                state_manager.transition_state(content_id, ContentState.IN_PROGRESS)
        
        # 상태 이력 출력
        logger.info("상태 이력:")
        for record in state_manager.get_state_history(content_id):
            logger.info(
                f"상태: {record['state']}, "
                f"시간: {record['timestamp']}, "
                f"에러: {record.get('error_message', 'N/A')}"
            )
        
        # 잘못된 상태 전환 시도
        logger.info("잘못된 상태 전환 시도 (DELETED -> IN_PROGRESS)")
        state_manager.transition_state(content_id, ContentState.IN_PROGRESS)
        
    except StateTransitionError as e:
        logger.error(f"상태 전환 오류: {str(e)}")
    except Exception as e:
        logger.exception(f"예상치 못한 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 