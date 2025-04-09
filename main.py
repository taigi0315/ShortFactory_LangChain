from utils.logger import setup_logger
from services.sheet_service import get_google_sheets_data, get_next_subject

# 로거 설정
logger = setup_logger("shorts_generator")

def main():
    try:
        logger.info("🚀 Shorts Generator 시작")
        
        # 다음 주제 찾기
        next_subject = get_next_subject()
        
        if next_subject:
            logger.info("📋 다음 주제 정보:")
            logger.info(f"주제: {next_subject['Subject']}")
            logger.info(f"제목: {next_subject['Title']}")
            logger.info(f"설명: {next_subject['Description']}")
            logger.info(f"해시태그: {next_subject['Hashtags']}")
        else:
            logger.info("❌ 처리할 다음 주제가 없습니다.")
            
    except Exception as e:
        logger.error(f"❌ 오류 발생: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 