import pytest
import os
from chains.video_chain import VideoChain

def test_video_chain_initialization():
    chain = VideoChain()
    assert chain is not None
    assert os.path.exists(chain.output_dir)

def test_output_directory_creation():
    # 임시 디렉토리 생성
    temp_dir = "temp_output"
    chain = VideoChain()
    chain.output_dir = temp_dir
    
    # 디렉토리가 생성되었는지 확인
    assert os.path.exists(temp_dir)
    
    # 정리
    os.rmdir(temp_dir) 