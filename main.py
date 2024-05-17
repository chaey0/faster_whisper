import os, sys
sys.path.append("./faster-whisper")

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from thumbnail import generate_thumbnail
from faster_whisper.transcribe import WhisperModel
from googletrans import Translator
import json
from typing import Optional
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import unquote



app = FastAPI()
translator = Translator()

# video 폴더 경로
VIDEO_FOLDER = "/Users/minu/Desktop/upload/video"
#VIDEO_FOLDER = "C:/workspace/Capstone/video"

# thumbnail 폴더 경로
#THUMBNAIL_FOLDER = "C:/workspace/Capstone/thumbnail"
THUMBNAIL_FOLDER = "/Users/minu/Desktop/upload/thumbnail"

def extract_text_from_file(file_path:str)->dict:
    try:
        model_size = "small"
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        segments, info = model.transcribe(file_path, beam_size=5)
        return segments
    except ValueError as ve:
        raise HTTPException(status_code=400, detail="Failed to transcribe audio: {}".format(str(ve)))

#자막 생성 API
@app.get("/api/json/{video_id}")
async def create_subtitle(video_id: str):
    # 코드 실행 시작 시간 기록
    start_time = time.time()
    
    # 요청된 video_id에 해당하는 영상 파일 경로를 확인
    video_path = os.path.join(VIDEO_FOLDER, f"{video_id}.mp4")
    
    # 해당하는 영상 파일이 존재하는지 확인
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="해당하는 영상을 찾을 수 없습니다.")
    
    if video_path:
        
        # 썸네일 생성
        thumbnail_path = os.path.join(THUMBNAIL_FOLDER, f"{video_id}.jpg")
        generate_thumbnail(video_path, thumbnail_path)
        
        # 오디오 추출 성공 시 자막 생성
        segments = extract_text_from_file(video_path)
        subtitles = []
        for segment in segments:
            translated_text = translator.translate(segment.text, src="ko", dest="en").text
            subtitle = {
                #"id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "korText": segment.text,
                "korWordText": segment.text.split(),
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
        # os.remove(audio_file_path)
        
        # 코드 실행 종료 시간 기록
        end_time = time.time()
        # 코드 실행 시간 계산
        execution_time = end_time - start_time
        
        # 추출된 오디오 파일 경로와 자막 파일 경로 반환
        return JSONResponse(final_json)
    else:
        raise HTTPException(status_code=500, detail="Failed to generate subtitles")
    
    
@app.get("/translate")
async def translate(word: str = Query(None)):  # 선택적 매개변수로 설정
    if not word:
        raise HTTPException(status_code=400, detail="No word provided")

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    try:
        print(f"Translating the word: {word}")
        url = f'https://en.dict.naver.com/#/search?range=word&query={word}'
        driver.get(url)
        time.sleep(5)  # 페이지 로드 완료를 위해 대기

        # 번역 결과 추출
        real_word_elements = driver.find_elements(By.CSS_SELECTOR, "div.component_keyword > div.row strong.highlight")
        eng_meaning_elements = driver.find_elements(By.CSS_SELECTOR, "div.component_keyword > div.row p.mean")

        if not eng_meaning_elements:
            raise HTTPException(status_code=404, detail="Translation not found")

        meaning_list = []
        for real_word, eng_meaning in zip(real_word_elements, eng_meaning_elements):
            meaning_list.append({
                "realWord": real_word.text,
                "meaning": eng_meaning.text
            })

        data = {
            "word": unquote(word),
            "engMeanings": meaning_list
        }
        return data
    finally:
        driver.quit()