import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from utils.config_manager import config_manager

class LoggerSetup:
    """로깅 시스템 설정을 관리하는 클래스"""
    
    def __init__(self):
        """LoggerSetup 초기화"""
        self.log_config = config_manager.get('logging', {})
        self.log_dir = Path('logs')
        self.log_file = self.log_dir / (self.log_config.get('file', 'shortfactory.log'))
        self._setup_log_directory()
    
    def _setup_log_directory(self) -> None:
        """로그 디렉토리 생성"""
        self.log_dir.mkdir(exist_ok=True)
    
    def _get_formatter(self) -> logging.Formatter:
        """로그 포맷터 생성"""
        log_format = self.log_config.get(
            'format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.Formatter(log_format)
    
    def _setup_file_handler(self) -> logging.Handler:
        """파일 핸들러 설정"""
        # 로그 로테이션 설정 (최대 10MB, 최대 5개 백업)
        handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10_000_000,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        handler.setFormatter(self._get_formatter())
        return handler
    
    def _setup_console_handler(self) -> logging.Handler:
        """콘솔 핸들러 설정"""
        handler = logging.StreamHandler()
        handler.setFormatter(self._get_formatter())
        return handler
    
    def get_logger(self, name: str, level: Optional[str] = None) -> logging.Logger:
        """
        로거 인스턴스 생성 및 반환
        
        Args:
            name (str): 로거 이름
            level (Optional[str]): 로그 레벨 (미지정시 설정파일의 level 사용)
        
        Returns:
            logging.Logger: 설정된 로거 인스턴스
        """
        logger = logging.getLogger(name)
        
        # 로그 레벨 설정
        log_level = (level or self.log_config.get('level', 'INFO')).upper()
        logger.setLevel(getattr(logging, log_level))
        
        # 핸들러가 이미 설정되어 있지 않은 경우에만 추가
        if not logger.handlers:
            # 파일 핸들러 추가
            logger.addHandler(self._setup_file_handler())
            
            # 콘솔 핸들러 추가 (DEBUG 모드일 때만)
            if os.getenv('DEBUG', 'false').lower() == 'true':
                logger.addHandler(self._setup_console_handler())
        
        return logger

# 싱글톤 인스턴스
logger_setup = LoggerSetup() 