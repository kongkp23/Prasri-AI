from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional
import json
from .supabase_client import get_supabase
from .gemini_client import get_menu_recommendations

router = APIRouter()

# ========================
# Request Models
# ========================

class RecommendRequest(BaseModel):
    ingredients: str
    equipment: Optional[str] = None

class SelectMenuRequest(BaseModel):
    recommendation_id: str
    menu_name: str

class FeedbackRequest(BaseModel):
    recommendation_id: str
    rating: int          # 0 = not appropriate, 1 = selected/like
    comment: Optional[str] = None

    @validator('rating')
    def validate_rating(cls, v):
        if v < 1:
            raise ValueError(f"rating must be >= 1 (Supabase constraint), got {v}")
        return v

# ========================
# Database Access Functions
# ========================

async def get_all_menus():
    """Fetch all menus from the database"""
    supabase = get_supabase()
    try:
        response = supabase.table("menus").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching menus: {e}")
        return []

async def save_recommendation(rec_data: dict):
    """
    Save a recommendation to the recommendations table.
    Schema: id, menu_name, user_ingredients, missing_ingredients, difficulty, estimated_cost, created_at
    """
    supabase = get_supabase()
    try:
        response = supabase.table("recommendations").insert(rec_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0].get("id")
        return None
    except Exception as e:
        print(f"Error saving recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save recommendation: {str(e)}")

async def save_feedback(feedback_data: dict):
    """
    Save feedback to the feedback table.
    Schema: id, recommendation_id, rating, comment, created_at
    """
    supabase = get_supabase()
    try:
        response = supabase.table("feedback").insert(feedback_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error saving feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")

# ========================
# API Routes
# ========================

@router.get("/menus")
async def get_menus():
    """Get all available menus from database"""
    menus = await get_all_menus()
    return {"menus": menus}


@router.post("/recommend")
async def recommend_menu(req: RecommendRequest):
    """Get menu recommendations based on ingredients and save each to DB"""
    ingredients_list = [i.strip() for i in req.ingredients.split(",") if i.strip()]

    # Step 1: Query Supabase menus
    db_menus = await get_all_menus()
    if not db_menus:
        raise HTTPException(status_code=500, detail="No menus found in database")

    # Step 2: Get AI recommendations from Gemini
    try:
        recommendations_json = await get_menu_recommendations(ingredients_list, db_menus)
        recommendations = json.loads(recommendations_json)
    except Exception as e:
        print(f"Gemini error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Recommendation failed: {str(e)}")

    # Step 3: Save each recommendation row to DB (matching actual schema)
    result = []
    for rec in recommendations[:3]:
        rec_data = {
            "menu_name": rec.get("menu_name", ""),
            "user_ingredients": ingredients_list,
            "missing_ingredients": rec.get("missing_ingredients", []),
            "difficulty": rec.get("difficulty", ""),
            "estimated_cost": int(rec.get("estimated_cost", 0)),
        }
        saved_id = await save_recommendation(rec_data)
        # Attach the DB-generated id to each card so frontend can send feedback
        result.append({
            **rec,
            "recommendation_id": saved_id,  # per-card id
        })

    return {
        "recommendations": result
    }


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    """
    Submit feedback for a recommendation.
    Saves rating + optional comment to the feedback table.
    rating: 1 = selected/like, -1 = not appropriate
    """
    if req.recommendation_id is None:
        raise HTTPException(status_code=400, detail="recommendation_id is required")

    feedback_data = {
        "recommendation_id": req.recommendation_id,
        "rating": req.rating,
        "comment": req.comment or "",
    }

    result = await save_feedback(feedback_data)
    return {"status": "success", "feedback_id": result.get("id") if result else None}


@router.patch("/select-menu")
async def select_menu(req: SelectMenuRequest):
    """
    Convenience endpoint: record that a user selected a menu.
    Inserts a positive-rating feedback row for that recommendation.
    """
    if not req.recommendation_id:
        raise HTTPException(status_code=400, detail="recommendation_id is required")

    feedback_data = {
        "recommendation_id": req.recommendation_id,
        "rating": 1,
        "comment": f"เลือกเมนู: {req.menu_name}",
    }
    result = await save_feedback(feedback_data)
    return {"status": "success", "feedback_id": result.get("id") if result else None}
