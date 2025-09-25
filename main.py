from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
import time
from google.cloud import vision

app = FastAPI()

# 10 MB converted to bytes. Will be used to set file size limit
MAX_BYTES = 10 * 1024**2

# middleware to make sure the file is less than 10 MB large
@app.middleware("http")
async def limit_body_size(request: Request, call_next):

    cl = request.headers.get("content-length")

    if cl is not None and cl.isdigit() and int(cl) > MAX_BYTES:
        return JSONResponse(status_code=413, content= {"detail": "File larger than limit of 10 MB."})
    return await call_next(request)

@app.post("/extract-text")
async def extractText(file: UploadFile = File(...)):

    # get the start time
    start_time = time.perf_counter()

    # read in the image

    # first check to make sure it is the right format
    if file.content_type not in ("image/jpeg", "image/jpg"):
        raise HTTPException(status_code = 400, detail = "File format must be JPEG/JPG.")

    # convert image to binary
    img_binary = await file.read()

    # check to make sure file isn't empty (unlikely but just in case)
    if not img_binary:
        raise HTTPException(status_code=400, detail="File is empty. Please upload a file with content.")

    # create the Vision API client
    # and return a 500 error if it fails
    try:
        client = vision.ImageAnnotatorClient()
    except Exception as e:
        raise HTTPException(status_code=500, detail = f"Failed to create Vision API client. {e}")
    
    # create the vision image object
    image = vision.Image(content=img_binary)


    # call the OCR method (text detection)
    # return a 502 error if this fails due to the upstream server
    try:
        response = client.text_detection(image=image)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Call to Vision API failed. {e}")
    

    # the vision API can also return internal error messages
    if response.error.message:
        raise HTTPException(status_code=502, detail=f"Vision API error. {response.error.message}")
    
    # empty placeholder variable for string. will return empty string if no text is detected
    full_text = ""
    if response.full_text_annotation and response.full_text_annotation.text:
        full_text = response.full_text_annotation.text

    # calculate total processing time
    end_time = time.perf_counter()

    # convert the processing time from seconds to milliseconds
    processing_time = (end_time - start_time) * 1000

    result = {
        "success": True,
        "time": processing_time,
        "text": full_text
    }

    return result