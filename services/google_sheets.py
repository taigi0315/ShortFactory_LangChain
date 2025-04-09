import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
from typing import List, Dict, Any, Optional
from models.sheet_config import SheetConfig
from utils.logger import setup_logger

logger = setup_logger("google_sheets")

class GoogleSheetsClient:
    """Google Sheets API 클라이언트를 관리하는 클래스"""
    
    def __init__(self, config: SheetConfig):
        self.config = config
        self.client = self._create_client()
        
    def _create_client(self) -> gspread.Client:
        """Google Sheets API 클라이언트를 생성합니다."""
        try:
            SCOPES = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = None
            # token.json 파일이 있으면 기존 자격증명을 로드
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            # 자격증명이 없거나 만료된 경우 새로 생성
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                # 새 자격증명을 token.json에 저장
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            client = gspread.authorize(creds)
            logger.info("✅ Google Sheets API 클라이언트가 생성되었습니다.")
            return client
        except Exception as e:
            logger.error(f"❌ Google Sheets API 클라이언트 생성 실패: {str(e)}")
            raise
    
    def get_worksheet(self) -> gspread.Worksheet:
        """지정된 워크시트를 가져옵니다."""
        try:
            spreadsheet = self.client.open_by_key(self.config.sheet_id)
            worksheet = spreadsheet.worksheet(self.config.sheet_name)
            logger.info(f"✅ 워크시트 '{self.config.sheet_name}'를 가져왔습니다.")
            return worksheet
        except Exception as e:
            logger.error(f"❌ 워크시트 가져오기 실패: {str(e)}")
            raise
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        """워크시트의 모든 레코드를 가져옵니다."""
        try:
            worksheet = self.get_worksheet()
            records = worksheet.get_all_records()
            logger.info(f"✅ {len(records)}개의 레코드를 가져왔습니다.")
            return records
        except Exception as e:
            logger.error(f"❌ 레코드 가져오기 실패: {str(e)}")
            raise
    
    def get_next_subject(self) -> Optional[Dict[str, Any]]:
        """
        다음 처리할 주제를 찾습니다.
        Column A(Subject)에 값이 있고 Column B(Created At)가 비어있는 첫 번째 행을 반환합니다.
        
        Returns:
            Optional[Dict[str, Any]]: 다음 주제 정보 또는 None
        """
        try:
            worksheet = self.get_worksheet()
            
            # 모든 데이터 가져오기
            all_values = worksheet.get_all_values()
            
            # 헤더 행 제외하고 순회
            for row in all_values[1:]:  # 첫 번째 행은 헤더
                subject = row[0]  # Column A
                created_at = row[1]  # Column B
                
                # Subject가 있고 Created At이 비어있는 경우
                if subject and not created_at:
                    # 헤더와 매핑하여 딕셔너리 생성
                    headers = all_values[0]
                    result = dict(zip(headers, row))
                    logger.info(f"✅ 다음 주제를 찾았습니다: {result['Subject']}")
                    return result
            
            logger.info("ℹ️ 처리할 다음 주제가 없습니다.")
            return None
            
        except Exception as e:
            logger.error(f"❌ 다음 주제 찾기 실패: {str(e)}")
            raise 