from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ddddocr
import base64
import io

app = FastAPI(title="ddddocr API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 ddddocr
ocr = ddddocr.DdddOcr(show_ad=False)
det = ddddocr.DdddOcr(det=True, show_ad=False)
slide = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)

class OcrRequest(BaseModel):
    image: str  # base64 encoded image

class SlideRequest(BaseModel):
    target: str  # 背景图 base64
    template: str  # 滑块图 base64

class SlideCompareRequest(BaseModel):
    target: str  # 背景图 base64
    template: str  # 滑块图 base64

@app.get("/")
def root():
    return {"status": "ok", "message": "ddddocr API is running"}

@app.post("/ocr")
def ocr_image(req: OcrRequest):
    """普通验证码识别"""
    try:
        img_bytes = base64.b64decode(req.image)
        result = ocr.classification(img_bytes)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/slide/match")
def slide_match(req: SlideRequest):
    """滑块验证码 - 缺口匹配"""
    try:
        target_bytes = base64.b64decode(req.target)
        template_bytes = base64.b64decode(req.template)
        result = slide.slide_match(template_bytes, target_bytes, simple_target=True)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/slide/compare")
def slide_compare(req: SlideCompareRequest):
    """滑块验证码 - 坑位比对"""
    try:
        target_bytes = base64.b64decode(req.target)
        template_bytes = base64.b64decode(req.template)
        result = slide.slide_comparison(template_bytes, target_bytes)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect")
def detect_image(req: OcrRequest):
    """目标检测"""
    try:
        img_bytes = base64.b64decode(req.image)
        result = det.detection(img_bytes)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
