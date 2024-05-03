import os, sys
sys.path.append("./faster-whisper")

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from extract_audio import extract_audio
from faster_whisper.transcribe import WhisperModel
from googletrans import Translator
import json
from typing import Optional
import time

app = FastAPI()
translator = Translator()

def extract_text_from_file(file_path:str)->dict:
    try:
        model_size = "small"
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        segments, info = model.transcribe(file_path, beam_size=5)
        return segments
    except ValueError as ve:
        raise HTTPException(status_code=400, detail="Failed to transcribe audio: {}".format(str(ve)))

#자막 생성 API
@app.get("/subtitle")
async def create_subtitle(video_id: str, youtube_link: str):
    # 코드 실행 시작 시간 기록
    start_time = time.time()
    
    # 유튜브 링크에서 오디오 추출
    audio_file_path = extract_audio(youtube_link)
    
    if audio_file_path:
        # 오디오 추출 성공 시 자막 생성
        segments = extract_text_from_file(audio_file_path)
        subtitles = []
        for segment in segments:
            translated_text = translator.translate(segment.text, src="ko", dest="en").text
            subtitle = {
                #"id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "korText": segment.text,
                "engText": translated_text
            }
            subtitles.append(subtitle)
        
        final_json={
            "video_id": video_id,
            "subtitleList": subtitles
        }
        # JSON 파일로 저장
        json_file_path = "subtitles.json"
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(final_json, f, ensure_ascii=False, indent=4)
        
        # 작업 완료 후 임시 파일 삭제
        os.remove(audio_file_path)
        
        # 코드 실행 종료 시간 기록
        end_time = time.time()
        # 코드 실행 시간 계산
        execution_time = end_time - start_time
        
        # 추출된 오디오 파일 경로와 자막 파일 경로 반환
        return JSONResponse(final_json)
    else:
        raise HTTPException(status_code=500, detail="Failed to generate subtitles")
