from utils.logger import logger_setup

def main():
    # 기본 로거 생성
    logger = logger_setup.get_logger("example")
    
    # 다양한 로그 레벨 테스트
    logger.debug("디버그 메시지")
    logger.info("정보 메시지")
    logger.warning("경고 메시지")
    logger.error("에러 메시지")
    
    # 다른 이름의 로거 생성
    sub_logger = logger_setup.get_logger("example.sub", level="DEBUG")
    sub_logger.debug("서브 로거의 디버그 메시지")
    
    try:
        # 예외 발생 시나리오
        raise ValueError("테스트 에러 발생")
    except Exception as e:
        logger.exception("예외가 발생했습니다: %s", str(e))

if __name__ == "__main__":
    main() 