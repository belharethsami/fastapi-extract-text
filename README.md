# Setup

1. Clone the repo locally `git clone https://github.com/belharethsami/fastapi-extract-text.git`

2. Navigate to the repo using `cd fastapi-extract-text`

3. Deploy to GCP using `gcloud run deploy --source .`


## API documentation
**Base URL:** https://fastapi-ocr-155731627853.us-east1.run.app

**Method:** `POST`

**Path:** `extract-text`

**Auth:** Public


## Request format
**Request content type:** `multipart/form-data`

**Field name:** `file`

**File type:** JPEG/JPG only

**Max size:** 10 MB


## Response format and possible error codes

**Format for successful response (200):**

```
{
    "success": true,
    "time": 55
    "text": "The quick brown fox jumped over the lazy dog."
}
```

`success`: boolean

`time`: processing time in millisenconds (float)

`text`: full OCR text (string)


### Possible error codes:

**400 Bad Request**

- File format isn't JPEG/JPG

- File is empty

**413 Request Entity Too Large**

- If file uploaded is larger than 10 MB

**422 Unprocessable Entity**

- If `file` field wasn't sent as a part of `multipart/form-data`

**500 Internal Server Error**

- Failed to create Vision API client (credential issues, etc.)

**502 Bad Gateway**

- Call to Vision API failed


## Example curl command for testing

`curl -X POST -F "file=@/path/to/image.jpg" https://fastapi-ocr-155731627853.us-east1.run.app/extract-text`


## Implementation explanation

**OCR service used:** GCP Vision API

**Handling file uploads and validation:** An HTTP middleware checks to make sure the file size is less than 10 MB if present.

If the file format is not JPEG/JPG, we return a 400 error. If the binary is empty, we return a 400 error.

**Deployment strategy:** The FastAPI server is hosted on Cloud Run. It can be deployed by cloning the repo locally, and building on GCP using:
`gcloud run deploy --source .`

GCP automatically manages Application Default Credentials for authentication to the Vision API.
