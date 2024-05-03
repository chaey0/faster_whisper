# test.py
import os, sys
sys.path.append("./faster-whisper")

from faster_whisper.transcribe import WhisperModel
from googletrans import Translator
#from google_trans_new import google_translator  
  
import json
from extract_audio import extract_audio

translator = Translator()
#translator = google_translator()

def extract_text_from_file(file_path:str)->dict:
    model_size="base"
    model=WhisperModel(model_size, device="cpu", compute_type="int8")

    
    #segments, info = model.transcribe(file_path, beam_size=5)

    
    try:
        segments, info = model.transcribe(file_path,beam_size=5)
        print("FUCK Detected language '%s' with probability %f" % (info.language, info.language_probability))
    except ValueError as e:
        print("Error:", e)
        
        sys.exit(1)  # 프로그램 종료
    
    return segments

def main():
    # 링크를 직접 입력
    youtube_link = "https://www.youtube.com/watch?v=Tq1OoWpcO_4"
    #youtube_link = "https://www.youtube.com/shorts/lmAg4FXYm34?feature=share"
    # 동영상 ID 가져오기
    video_id = youtube_link.split("=")[-1]
    file_path = f"{video_id}.mp3"
    
    # 동영상 추출
    file_path=extract_audio(youtube_link)
    
    segments = extract_text_from_file(file_path)
    
    data = []
    for segment in segments:
        translated_text = translator.translate(segment.text, src="ko", dest="en").text
        segment_data = {
            "id": segment.id,
            "start": segment.start,
            "end": segment.end,
            "ko-text": segment.text,
            "eng-text": translated_text
        }
        data.append(segment_data)
    
    with open("translated_transcript.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    # 작업 완료 후 임시 파일 삭제
    os.remove(file_path)

if __name__ == "__main__":
    main()
