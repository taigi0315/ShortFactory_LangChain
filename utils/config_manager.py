import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

class ConfigManager:
    """설정 파일과 환경 변수를 관리하는 클래스"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        ConfigManager 초기화
        
        Args:
            config_path (str): 설정 파일 경로
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_env()
        self._load_config()
    
    def _load_env(self) -> None:
        """환경 변수 로드"""
        load_dotenv()
    
    def _load_config(self) -> None:
        """YAML 설정 파일 로드 및 환경 변수 치환"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
    
    def _replace_env_vars(self, config: Dict[str, Any], section: str = "") -> None:
        """
        설정값 중 환경 변수 참조를 실제 값으로 치환
        
        Args:
            config: 설정 딕셔너리
            section: 현재 처리 중인 설정 섹션
        """
        for key, value in config.items():
            current_section = f"{section}.{key}" if section else key
            
            if isinstance(value, dict):
                self._replace_env_vars(value, current_section)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env_value = os.getenv(env_var)
                
                # 로깅 섹션이 아닌 경우에만 환경 변수 필수 체크
                if env_value is None and not current_section.startswith("logging"):
                    raise ValueError(f"환경 변수를 찾을 수 없습니다: {env_var}")
                
                if env_value is not None:
                    config[key] = env_value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        설정값 조회
        
        Args:
            key (str): 설정 키 (점으로 구분된 경로)
            default: 기본값
        
        Returns:
            설정값 또는 기본값
        """
        try:
            value = self._config
            for k in key.split('.'):
                value = value[k]
            
            # 딕셔너리인 경우 환경 변수 치환
            if isinstance(value, dict):
                self._replace_env_vars(value, key)
            
            return value
        except (KeyError, TypeError):
            return default
    
    def get_all(self) -> Dict[str, Any]:
        """전체 설정 반환"""
        return self._config.copy()

# 싱글톤 인스턴스
config_manager = ConfigManager() 