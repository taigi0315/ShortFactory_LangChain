.PHONY: install test lint format clean setup-python

# Python 버전 확인
PYTHON_VERSION := $(shell python --version)
PYTHON_PATH := $(shell which python)

# 기본 설정
VENV_NAME := venv
VENV_BIN := $(VENV_NAME)/bin
PYTHON := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip

# Python 설정
setup-python:
	@echo "Python SSL 모듈 설정 중..."
	brew install openssl@3
	LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib" \
	CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include" \
	PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig" \
	pyenv install --force 3.12.2
	pyenv global 3.12.2
	@echo "Python SSL 모듈 설정 완료"

# 설치
install: setup-python
	@echo "Python 버전: $(PYTHON_VERSION)"
	@echo "Python 경로: $(PYTHON_PATH)"
	rm -rf $(VENV_NAME)
	python -m venv $(VENV_NAME)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# 테스트 실행
test:
	$(PYTHON) -m pytest -v --cov=tools --cov-report=term-missing

# 코드 스타일 검사
lint:
	$(PYTHON) -m flake8 tools tests
	$(PYTHON) -m isort --check-only tools tests

# 코드 포맷팅
format:
	$(PYTHON) -m black tools tests
	$(PYTHON) -m isort tools tests

# 캐시 및 임시 파일 정리
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "output" -exec rm -rf {} +

# 개발 환경 초기화
init: clean install format

# 가상환경 활성화 (Windows/Mac/Linux)
activate-venv:
	@echo "Use Following command to activate venv"
	@echo "venv\Scripts\activate.bat"
	@echo "venv\Scripts\Activate.ps1"
# Google Cloud 인증 및 프로젝트 설정
gcloud-auth:
	gcloud auth login
	gcloud auth application-default set-quota-project gen-lang-client-0273830092

# 도움말
help:
	@echo "사용 가능한 명령어:"
	@echo "  make setup-python - Python SSL 모듈 설정"
	@echo "  make install    - 의존성 설치"
	@echo "  make test      - 테스트 실행"
	@echo "  make lint      - 코드 스타일 검사"
	@echo "  make format    - 코드 포맷팅"
	@echo "  make clean     - 캐시 및 임시 파일 정리"
	@echo "  make init      - 개발 환경 초기화"
	@echo "  make activate-venv - 가상환경 활성화 안내"
	@echo "  make gcloud-auth  - Google Cloud 인증 및 프로젝트 설정"
	@echo "  make help      - 도움말 표시"