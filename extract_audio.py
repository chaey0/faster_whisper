# extract_audio.py
import os
import pytube

def extract_audio(youtube_link):
    try:
        # YouTube 객체 생성
        youtube = pytube.YouTube(youtube_link)
        
        # 오디오 스트림 필터링 및 다운로드
        audio_stream = youtube.streams.filter(only_audio=True).first()
        
        # 파일 이름에 사용할 비디오 제목을 가져와서 공백을 언더스코어로 대체 (추가)
        #video_title = youtube.title.replace(" ", "_")
        
        #audio_stream.download(filename=output_file)
        
        # 다운로드한 오디오 파일 경로 반환
        return audio_stream.download()
        return output_file
        
    except Exception as e:
        print("Error:", e)
        return None
