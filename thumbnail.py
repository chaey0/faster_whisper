import random
from moviepy.editor import VideoFileClip
from PIL import Image

def generate_thumbnail(video_path, thumbnail_path):
    # 비디오 파일에서 clip 생성
    clip = VideoFileClip(video_path)
    
    # 비디오의 전체 길이(초 단위)를 가져옴
    # video_duration = clip.duration
    
    # 랜덤한 시간 생성
    # time = random.uniform(0, video_duration)
    time=0
    
    # 특정 시간(time)에서 이미지 추출
    frame = clip.get_frame(time)
    
    # Pillow 이미지로 변환
    img = Image.fromarray(frame)
    
    # 이미지 저장
    img.save(thumbnail_path)

# 예시: 썸네일 생성
# video_path = 'C:/workspace/Capstone/2.mp4'
# thumbnail_path = 'C:/workspace/Capstone/thumbnail.jpg'

# generate_thumbnail(video_path, thumbnail_path)
