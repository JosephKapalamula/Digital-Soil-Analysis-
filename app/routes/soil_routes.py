from fastapi import APIRouter,HTTPException
from ..schemas.soil_schema import SoilRequest
from ..cntrollers.soil_controller import run_full_analysis

soil_router = APIRouter()

@soil_router.post("/analyze-soil")
async def soil_analysis(req: SoilRequest):
    try:
        # 1. Call the controller logic we built
        features = run_full_analysis(req.latitude, req.longitude)
        
        # 2. Return the multispectral data
        return {
            "status": "success",
            "location": {
                "lat": req.latitude,
                "lon": req.longitude
            },
            "data": features
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))