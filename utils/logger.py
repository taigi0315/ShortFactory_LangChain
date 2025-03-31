import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from langchain.globals import set_debug

def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """
    로거를 설정하고 반환합니다.
    
    Args:
        name (str): 로거 이름
        log_dir (str): 로그 파일이 저장될 디렉토리
        
    Returns:
        logging.Logger: 설정된 로거
    """
    # 로그 디렉토리 생성
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 이미 핸들러가 있다면 추가하지 않음
    if logger.handlers:
        return logger
    
    # 포맷터 생성
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (로그 로테이션)
    file_handler = RotatingFileHandler(
        log_path / f"{name}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def setup_langchain_debug(debug: bool = True):
    """
    LangChain 디버그 모드를 설정합니다.
    
    Args:
        debug (bool): 디버그 모드 활성화 여부
    """
    set_debug(debug) 