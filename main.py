from chains.gossip_chain import GossipChain
from chains.audio_chain import AudioChain
from chains.video_chain import VideoChain
from tools.youtube_uploader import YouTubeUploader
from tools.tiktok_uploader import TikTokUploader
from tools.instagram_uploader import InstagramUploader
import os
from dotenv import load_dotenv
import argparse
from pathlib import Path
from utils.logger import setup_logger, setup_langchain_debug

# 로거 설정
logger = setup_logger("shorts_generator")
setup_langchain_debug(True)

def main():
    # 환경 변수 로드
    load_dotenv()
    
    # 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(description="YouTube Shorts Gossip Generator")
    parser.add_argument("--topic", type=str, help="대화의 주제")
    parser.add_argument("--background", type=str, required=True, help="배경 비디오 파일 경로")
    parser.add_argument("--upload", action="store_true", help="소셜 미디어에 업로드")
    parser.add_argument("--platforms", nargs="+", choices=["youtube", "tiktok", "instagram"], 
                       default=["youtube"], help="업로드할 플랫폼 선택")
    args = parser.parse_args()
    
    logger.info("🚀 Shorts Generator 시작")
    logger.info(f"🎯 주제: {args.topic or '기본 주제'}")
    logger.info(f"🎬 배경 비디오: {args.background}")
    
    # 체인 초기화
    logger.info("🧠 체인 초기화 중...")
    gossip_chain = GossipChain()
    audio_chain = AudioChain()
    video_chain = VideoChain()
    
    # 업로더 초기화
    uploaders = {}
    if args.upload:
        if "youtube" in args.platforms:
            uploaders["youtube"] = YouTubeUploader()
        if "tiktok" in args.platforms:
            uploaders["tiktok"] = TikTokUploader()
        if "instagram" in args.platforms:
            uploaders["instagram"] = InstagramUploader()
    
    try:
        # 1. 대화 생성
        logger.info("💬 대화 생성 중...")
        dialogue = gossip_chain.generate_dialogue(args.topic)
        logger.info(f"✅ {len(dialogue)}개의 대화 라인 생성 완료")
        
        # 2. 음성 생성
        logger.info("🔊 음성 생성 중...")
        audio_files = audio_chain.generate_dialogue_audio(dialogue)
        logger.info(f"✅ {len(audio_files)}개의 음성 파일 생성 완료")
        
        # 3. 자막 파일 생성
        logger.info("📝 자막 생성 중...")
        subtitle_file = create_subtitles(dialogue, audio_files)
        logger.info("✅ 자막 파일 생성 완료")
        
        # 4. 비디오 생성
        logger.info("🎥 비디오 생성 중...")
        output_file = video_chain.create_video(
            audio_files=audio_files,
            subtitle_file=subtitle_file,
            background_video=args.background,
            output_filename="final_shorts.mp4"
        )
        
        logger.info(f"✨ 완료! 생성된 비디오: {output_file}")
        
        # 5. 소셜 미디어 업로드
        if args.upload and uploaders:
            logger.info("📤 소셜 미디어 업로드 시작...")
            
            # 대화 내용을 기반으로 캡션 생성
            caption = "\n".join([line["text"] for line in dialogue])
            hashtags = ["#shorts", "#gossip", "#drama"]
            
            for platform, uploader in uploaders.items():
                try:
                    if platform == "youtube":
                        uploader.upload_video(
                            video_path=output_file,
                            title=args.topic or "Gossip Shorts",
                            description=caption,
                            tags=hashtags
                        )
                    elif platform == "tiktok":
                        uploader.upload_video(
                            video_path=output_file,
                            caption=caption,
                            hashtags=hashtags
                        )
                    elif platform == "instagram":
                        uploader.upload_video(
                            video_path=output_file,
                            caption=caption,
                            hashtags=hashtags
                        )
                    logger.info(f"✅ {platform} 업로드 완료")
                except Exception as e:
                    logger.error(f"❌ {platform} 업로드 실패: {str(e)}")
        
    except Exception as e:
        logger.error(f"❌ 오류 발생: {str(e)}", exc_info=True)
        raise

def create_subtitles(dialogue, audio_files):
    """
    대화와 오디오 파일을 기반으로 자막 파일을 생성합니다.
    """
    from tools.audio_utils import AudioUtils
    
    subtitle_file = Path("output/subtitles.srt")
    current_time = 0
    
    with open(subtitle_file, "w", encoding="utf-8") as f:
        for i, (line, audio_file) in enumerate(zip(dialogue, audio_files), 1):
            duration = AudioUtils.get_audio_duration(audio_file)
            
            # 자막 시작/종료 시간 계산
            start_time = format_time(current_time)
            current_time += duration
            end_time = format_time(current_time)
            
            # 자막 작성
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{line.text}\n\n")
    
    return str(subtitle_file)

def format_time(seconds):
    """
    초 단위의 시간을 SRT 형식(HH:MM:SS,mmm)으로 변환합니다.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

if __name__ == "__main__":
    main() 