from fastapi import APIRouter,HTTPException,Depends
from ..schemas.soil_schema import SoilRequest,SoilAnalysisRecord,DataRequest,UpdateGroundTruthRequest,DeleteGroundTruthRequest
from ..cntrollers.soil_controller import run_full_analysis,updating_ground_truth,deleting_ground_truth,extract_soil_features
from ..db.session import get_db
from fastapi import Depends
from sqlalchemy.orm import Session 


soil_router = APIRouter()
@soil_router.post("/analyze-soil")
async def soil_analysis(req: SoilRequest,db: Session = Depends(get_db)):
    try:
        # 1. Call the controller logic we built
        features = run_full_analysis(req.latitude, req.longitude, db)
        
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

@soil_router.post("/collect-ground-truth")
def collect_data(req: DataRequest,db: Session = Depends(get_db)):
    # 1. Get the satellite data for this exact spot
    existing_truth = db.query(SoilAnalysisRecord).filter(
        SoilAnalysisRecord.latitude == req.latitude,
        SoilAnalysisRecord.longitude == req.longitude,
        SoilAnalysisRecord.is_ground_truth == True
    ).first()
    if existing_truth:
        raise HTTPException(status_code=400, detail="Ground truth already exists for this location")
    satellite_data = extract_soil_features(req.latitude, req.longitude)
    # 2. Save it as a "Training Ready" record
    new_training_data = SoilAnalysisRecord(
        location=req.location,
        actual_ph=req.ph,
        actual_nitrogen=req.nitrogen,
        actual_phosphorus=req.phosphorus,
        actual_potassium=req.potassium,
        actual_recommended_crop=req.recommended_crop,
        latitude=req.latitude,
        longitude=req.longitude,
        is_ground_truth=True,
        raw_satellite_data=satellite_data,
        confidence_score=req.confidence
        )
    db.add(new_training_data)
    db.commit()
    return {"status": "Ground truth collected and linked to satellite data"}

@soil_router.put("/update-ground-truth")
def update_ground_truth(req: UpdateGroundTruthRequest, db: Session = Depends(get_db)):
    try:
        updating_ground_truth(req.latitude, req.longitude, req.actual_ph, req.actual_nitrogen, req.actual_phosphorus, req.actual_potassium, req.actual_recommended_crop, req.confidence, db)
        return {"status": "Ground truth updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@soil_router.delete("/delete-ground-truth")
def delete_ground_truth(req: DeleteGroundTruthRequest, db: Session = Depends(get_db)):
    try:
        deleting_ground_truth(req.latitude, req.longitude, db)
        return {"status": "Ground truth deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
