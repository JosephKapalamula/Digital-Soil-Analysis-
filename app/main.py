from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import dotenv
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Digital Soil Analysis API",
    description="AI-driven soil nutrient prediction and crop recommendation for Malawi.",
    version="1.0.0"
) 

# Configure CORS for all origins in production
origins = [
    "http://10.90.166.46:3000", # current frontend IP
    "http://localhost:3000",    # Standard local react/next dev
    "http://127.0.0.1:3000",
    "https://digital-soil-analysis-i1dhey0ob-joseph-kapalamulas-projects.vercel.app"
]

# Allow all origins in production for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Digital Soil Analysis System is Online"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "message": "All systems operational"}

@app.get("/test")
async def test_endpoint():
    logger.info("Test endpoint accessed")
    return {"message": "Test endpoint working", "timestamp": str(os.environ.get("TIMESTAMP", "unknown"))}

@app.get("/api/v1/test")
async def api_test():
    logger.info("API v1 test endpoint accessed")
    return {"message": "API v1 test endpoint working"}

# Try to import and include routes
try:
    from app.routes.soil_routes import soil_router
    app.include_router(soil_router, prefix="/api/v1", tags=["soil"])
    logger.info("✅ Soil routes included successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import soil routes: {e}")

try:
    from app.routes.user_routes import user_router
    app.include_router(user_router, prefix="/api/v1", tags=["user"])
    logger.info("✅ User routes included successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import user routes: {e}")

# Print all available routes
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            logger.info(f"Route: {route.methods} {route.path}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)