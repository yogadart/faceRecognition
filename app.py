"""
    docstring
"""
# pylint: disable=import-error

import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from deepface import DeepFace
from functions import resize_image_dimension, file_to_image

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# penggunaan GPU
# os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
# os.environ['CUDA_VISIBLE_DEVICES'] = '0'

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS = [
    "VGG-Face", 
    "Facenet", 
    "Facenet512", 
    "OpenFace", 
    "DeepFace", 
    "DeepID", 
    "ArcFace", 
    "Dlib", 
    "SFace",
]

@app.get('/api/facematch/v1')
async def index():
    """
        docstring
    """

    return 0

@app.post("/api/facematch/v1/verify")
async def create_upload_file(file1: UploadFile = File(...),file2: UploadFile = File(...)):
    """
        Response Success Example:
        {
            "status": 200,
            "result": {
                "verified": false,
                "distance": 0.49744723671250135,
                "threshold": 0.4,
                "model": "VGG-Face",
                "detector_backend": "opencv",
                "similarity_metric": "cosine",
                "facial_areas": {
                    "img1": {
                        "x": 141,
                        "y": 385,
                        "w": 524,
                        "h": 524
                    },
                    "img2": {
                        "x": 483,
                        "y": 85,
                        "w": 271,
                        "h": 271
                    }
                },
                "time": 12.77
            }
        }    
    """
    # pylint: disable=raise-missing-from,invalid-name

    if file1.filename == '' or file2.filename == '':
        return JSONResponse(status_code=400,content={
            "status":400,
            "message":"file1 and file2 are required"
        })
    try:
        # Save the uploaded file to a temporary directory on disk
        file_path1 = file_to_image(file1)
        file_path2 = file_to_image(file2)

        _ = resize_image_dimension(file_path1)
        _ = resize_image_dimension(file_path2)

        # Process the uploaded file with DeepFace
        result = DeepFace.verify(
            file_path1,
            file_path2,
            enforce_detection=False,
            model_name=MODELS[2]
        )

        result['verified'] = bool(result['verified'].item())

        # Return a JSON response indicating success
        return JSONResponse(
            content={
                "status":200,
                "result": result
            }
        )

    except Exception as e:
        # If an error occurs, raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Always close and remove the temporary file when finished
        file1.file.close()
        file2.file.close()
        os.remove(file_path1)
        os.remove(file_path2)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=9001)
