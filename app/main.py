from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes.soil_routes import soil_router
from app.routes.user_routes import user_router
import uvicorn
import dotenv
import os  
dotenv.load_dotenv()

app = FastAPI(
    title="Digital Soil Analysis API",
    description="AI-driven soil nutrient prediction and crop recommendation for Malawi.",
    version="1.0.0"
) 
origins = [
    "http://10.90.166.46:3000", # current frontend IP
    "http://localhost:3000",    # Standard local react/next dev
    "http://127.0.0.1:3000",
    "https://digital-soil-analysis-i1dhey0ob-joseph-kapalamulas-projects.vercel.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Digital Soil Analysis System is Online"}

app.include_router(soil_router, prefix="/api/v1", tags=["soil"])
app.include_router(user_router, prefix="/api/v1", tags=["user"])

 
if __name__ =="__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
   
    