from typing import List, Dict, Any, Optional
from models.sheet_config import SheetConfig
from services.google_sheets import GoogleSheetsClient
from utils.logger import setup_logger

logger = setup_logger("sheet_service")

def get_google_sheets_data() -> List[Dict[str, Any]]:
    """
    Google Sheets에서 데이터를 가져옵니다.
    
    Returns:
        List[Dict[str, Any]]: 시트의 모든 레코드
        
    Raises:
        ValueError: 필수 환경 변수가 설정되지 않은 경우
        gspread.exceptions.APIError: Google Sheets API 오류
        Exception: 기타 예외
    """
    try:
        # 설정 로드
        config = SheetConfig.from_env()
        
        # 클라이언트 생성 및 데이터 가져오기
        client = GoogleSheetsClient(config)
        data = client.get_all_records()
        
        logger.info(f"✅ Google Sheets에서 {len(data)}개의 항목을 성공적으로 가져왔습니다.")
        return data
        
    except ValueError as e:
        logger.error(f"❌ 설정 오류: {str(e)}")
        raise
    except gspread.exceptions.APIError as e:
        logger.error(f"❌ Google Sheets API 오류: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ 예기치 않은 오류: {str(e)}")
        raise

def get_next_subject() -> Optional[Dict[str, Any]]:
    """
    다음 처리할 주제를 찾습니다.
    
    Returns:
        Optional[Dict[str, Any]]: 다음 주제 정보 또는 None
    """
    try:
        config = SheetConfig()
        client = GoogleSheetsClient(config)
        return client.get_next_subject()
    except Exception as e:
        logger.error(f"❌ 다음 주제 가져오기 실패: {str(e)}")
        raise

def get_all_records() -> List[Dict[str, Any]]:
    """
    모든 레코드를 가져옵니다.
    
    Returns:
        List[Dict[str, Any]]: 모든 레코드 목록
    """
    try:
        config = SheetConfig()
        client = GoogleSheetsClient(config)
        return client.get_all_records()
    except Exception as e:
        logger.error(f"❌ 레코드 가져오기 실패: {str(e)}")
        raise 