from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import dotenv
import os
import sys

# Load environment variables
dotenv.load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.routes.soil_routes import soil_router
    from app.routes.user_routes import user_router
    print("✅ Successfully imported route modules")
except ImportError as e:
    print(f"❌ Failed to import route modules: {e}")
    soil_router = None
    user_router = None

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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "All systems operational"}

# Only include routers if they were successfully imported
if soil_router:
    app.include_router(soil_router, prefix="/api/v1", tags=["soil"])
    print("✅ Soil routes included")
else:
    print("⚠️  Soil routes not included due to import error")

if user_router:
    app.include_router(user_router, prefix="/api/v1", tags=["user"])
    print("✅ User routes included")
else:
    print("⚠️  User routes not included due to import error")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)