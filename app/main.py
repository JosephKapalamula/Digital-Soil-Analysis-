from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes.soil_routes import soil_router
import dotenv
import os 
dotenv.load_dotenv()

app = FastAPI(
    title="Digital Soil Analysis API",
    description="AI-driven soil nutrient prediction and crop recommendation for Malawi.",
    version="1.0.0"
)
  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Digital Soil Analysis System is Online"}

@app.include_router(soil_router, prefix="/api/v1", tags=["soil"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
