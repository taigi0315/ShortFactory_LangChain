from utils.logger import setup_logger
from services.sheet_service import get_google_sheets_data, get_next_subject
from services.content_creator import ContentCreator

# 로거 설정
logger = setup_logger("shorts_generator")

def main():
    try:
        logger.info("🚀 Shorts Generator 시작")
        
        # 다음 주제 찾기
        next_subject = get_next_subject()
        
        if next_subject:
            logger.info(f"📋 다음 주제: {next_subject['Subject']}")
            
            # 콘텐츠 생성기 초기화
            content_creator = ContentCreator()
            
            # 콘텐츠 생성
            content = content_creator.create_content(next_subject['Subject'])
            
            logger.info("✅ 콘텐츠 생성 완료")
            logger.info(f"📝 생성된 콘텐츠: {content}")
            
        else:
            raise Exception("❌ 처리할 다음 주제가 없습니다.")
        
    except Exception as e:
        logger.error(f"❌ 오류 발생: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 