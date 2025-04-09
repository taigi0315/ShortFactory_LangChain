from pydantic import BaseModel
import yaml
import os
from utils.logger import setup_logger

logger = setup_logger("sheet_config")

class SheetConfig(BaseModel):
    """Google Sheets 설정을 관리하는 클래스"""
    
    def __init__(self, **data):
        # config.yaml 파일 로드
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            sheets_config = config.get('google_sheets', {})
            
            # 환경 변수에서 값 가져오기
            credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', sheets_config.get('credentials_file'))
            sheet_id = os.getenv('SPREADSHEET_ID', sheets_config.get('spreadsheet_id'))
            sheet_name = os.getenv('SHEET_NAME', sheets_config.get('worksheet_name'))
            
            data.update({
                'credentials_path': credentials_path,
                'sheet_id': sheet_id,
                'sheet_name': sheet_name
            })
            
        super().__init__(**data)
        
    credentials_path: str
    sheet_id: str
    sheet_name: str
    
    def __post_init__(self):
        """설정값 검증"""
        try:
            # credentials.json 파일 존재 확인
            with open(self.credentials_path, 'r') as f:
                pass
            logger.info(f"✅ credentials.json 파일 확인 완료: {self.credentials_path}")
        except FileNotFoundError:
            logger.error(f"❌ credentials.json 파일을 찾을 수 없습니다: {self.credentials_path}")
            raise 