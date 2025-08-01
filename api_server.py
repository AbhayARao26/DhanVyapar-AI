from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import sys
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.user_onboarding_agent import UserOnboardingAgent
from agents.credit_scoring_agent import CreditScoringAgent
from agents.loan_risk_advisor_agent import LoanRiskAdvisorAgent
from agents.educational_content_agent import EducationalContentAgent
from agents.document_processing_agent import DocumentProcessingAgent
from agents.voice_assistant_agent import VoiceAssistantAgent
from agents.translation_agent import TranslationAgent
from agents.nbfc_recommendation_agent import NBFCRecommendationAgent

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for user data
user_database = {}
current_user_id = None

# Initialize agents
onboarding_agent = UserOnboardingAgent()
credit_agent = CreditScoringAgent()
loan_advisor = LoanRiskAdvisorAgent()
education_agent = EducationalContentAgent()
document_agent = DocumentProcessingAgent()
voice_agent = VoiceAssistantAgent()
translation_agent = TranslationAgent()
nbfc_agent = NBFCRecommendationAgent()

USER_DATA_FILE = "user_data.json"

def load_user_data():
    global user_database
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                user_database = json.load(f)
    except Exception as e:
        print(f"Error loading user data: {e}")
        user_database = {}

def save_user_data():
    try:
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_database, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving user data: {e}")

# Load user data on startup
load_user_data()

# --- Pydantic Models ---
class UserCreateRequest(BaseModel):
    name: str
    phone: str
    village: Optional[str] = ""

class UserSelectRequest(BaseModel):
    user_id: str

class LanguageUpdateRequest(BaseModel):
    user_id: str
    new_language: str

class ProfileUpdateRequest(BaseModel):
    user_id: str
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    dependents: Optional[int] = None
    aadhaar: Optional[str] = None
    voter_id: Optional[str] = None
    age: Optional[int] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    house_type: Optional[str] = None
    electricity: Optional[str] = None
    occupation: Optional[str] = None
    secondary_income: Optional[str] = None
    income: Optional[int] = None
    expenses: Optional[int] = None
    seasonal_variation: Optional[str] = None
    savings_monthly: Optional[int] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    existing_loans: Optional[str] = None
    repayment_history: Optional[str] = None
    past_loans: Optional[str] = None
    group_membership: Optional[str] = None
    owns_land: Optional[str] = None
    land_area: Optional[str] = None
    land_type: Optional[str] = None
    patta_number: Optional[str] = None
    property_location: Optional[str] = None
    smartphone: Optional[str] = None
    app_usage: Optional[str] = None
    communication_pref: Optional[str] = None
    internet: Optional[str] = None
    user_notes: Optional[str] = None
    agent_observations: Optional[str] = None

class EducationRequest(BaseModel):
    user_id: str
    topic: str

class NBFCRequest(BaseModel):
    user_id: str
    region: str
    classification_filter: Optional[str] = ""
    language: Optional[str] = "English"

class ChatRequest(BaseModel):
    user_id: str
    message: str
    language: str

# --- API Endpoints ---
@app.get("/users")
def get_users():
    return list(user_database.keys())

@app.post("/users/create")
def create_user(req: UserCreateRequest):
    name, phone, village = req.name, req.phone, req.village
    if not name or not phone:
        raise HTTPException(status_code=400, detail="Name and phone number are required")
    user_id = f"{name}_{phone}"
    # Initialize user data
    user_database[user_id] = {
        "full_name": name,
        "phone_number": phone,
        "village_name": village or "",
        "preferred_language": "english",
        "age": None,
        "gender": "",
        "aadhaar_number": "",
        "marital_status": "",
        "voter_id": "",
        "district": "",
        "state": "",
        "pincode": "",
        "house_type": "",
        "electricity_connection": "",
        "number_of_dependents": None,
        "primary_occupation": "",
        "secondary_income_sources": "",
        "monthly_income": None,
        "monthly_expenses": None,
        "seasonal_variation": "",
        "bank_account_status": "",
        "bank_name": "",
        "existing_loans": "",
        "repayment_history": "",
        "savings_per_month": None,
        "group_membership": "",
        "past_loan_amounts": "",
        "owns_land": "",
        "land_area": "",
        "land_type": "",
        "patta_or_katha_number": "",
        "property_location": "",
        "owns_smartphone": "",
        "knows_how_to_use_apps": "",
        "preferred_mode_of_communication": "",
        "internet_availability": "",
        "user_notes": "",
        "agent_observations": ""
    }
    save_user_data()
    return {"message": f"User {name} created successfully!", "user_id": user_id}

@app.post("/users/select")
def select_user(req: UserSelectRequest):
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    return {"dashboard": get_user_dashboard(user_id)}

def get_user_dashboard(user_id: str) -> str:
    if user_id not in user_database:
        return "❌ User not found"
    user_data = user_database[user_id]
    dashboard = f"""
# 👤 User Dashboard: {user_data.get('full_name', 'Unknown')}
## 📋 Basic Information
- **Name**: {user_data.get('full_name', 'Not provided')}
- **Phone**: {user_data.get('phone_number', 'Not provided')}
- **Age**: {user_data.get('age', 'Not provided')}
- **Gender**: {user_data.get('gender', 'Not provided')}
- **Village**: {user_data.get('village_name', 'Not provided')}
- **District**: {user_data.get('district', 'Not provided')}
- **Preferred Language**: {user_data.get('preferred_language', 'english').title()}
## 💼 Occupation & Income
- **Primary Occupation**: {user_data.get('primary_occupation', 'Not provided')}
- **Monthly Income**: ₹{user_data.get('monthly_income', 'Not provided')}
- **Monthly Expenses**: ₹{user_data.get('monthly_expenses', 'Not provided')}
- **Seasonal Variation**: {user_data.get('seasonal_variation', 'Not provided')}
- **Savings per Month**: ₹{user_data.get('savings_per_month', 'Not provided')}
## 🏦 Financial Information
- **Bank Account**: {user_data.get('bank_account_status', 'Not provided')}
- **Repayment History**: {user_data.get('repayment_history', 'Not provided')}
- **Group Membership**: {user_data.get('group_membership', 'Not provided')}
## 🏡 Property & Assets
- **Owns Land**: {user_data.get('owns_land', 'Not provided')}
- **Land Area**: {user_data.get('land_area', 'Not provided')}
- **Land Type**: {user_data.get('land_type', 'Not provided')}
## 📊 Profile Completeness
{get_profile_completeness(user_data)}
## 🎯 Available Actions
Use the tabs below to:
- Complete profile information
- Get credit score assessment
- Apply for loan recommendations
- Access financial education content
"""
    return dashboard

def get_profile_completeness(user_data: Dict[str, Any]) -> str:
    completeness = 0
    if user_data.get('full_name'): completeness += 10
    if user_data.get('phone_number'): completeness += 10
    if user_data.get('village_name'): completeness += 10
    if user_data.get('gender'): completeness += 10
    if user_data.get('age'): completeness += 10
    if user_data.get('primary_occupation'): completeness += 10
    if user_data.get('monthly_income'): completeness += 10
    if user_data.get('monthly_expenses'): completeness += 10
    if user_data.get('savings_per_month'): completeness += 10
    if user_data.get('bank_account_status'): completeness += 10
    if user_data.get('repayment_history'): completeness += 10
    if user_data.get('group_membership'): completeness += 10
    if user_data.get('owns_land'): completeness += 10
    if user_data.get('land_area'): completeness += 10
    if user_data.get('land_type'): completeness += 10
    if user_data.get('aadhaar_number'): completeness += 10
    if user_data.get('voter_id'): completeness += 10
    if user_data.get('district'): completeness += 10
    if user_data.get('state'): completeness += 10
    if user_data.get('pincode'): completeness += 10
    if user_data.get('house_type'): completeness += 10
    if user_data.get('electricity_connection'): completeness += 10
    if user_data.get('number_of_dependents'): completeness += 10
    if user_data.get('secondary_income_sources'): completeness += 10
    if user_data.get('bank_name'): completeness += 10
    if user_data.get('past_loan_amounts'): completeness += 10
    if user_data.get('patta_or_katha_number'): completeness += 10
    if user_data.get('property_location'): completeness += 10
    if user_data.get('owns_smartphone'): completeness += 10
    if user_data.get('knows_how_to_use_apps'): completeness += 10
    if user_data.get('preferred_mode_of_communication'): completeness += 10
    if user_data.get('internet_availability'): completeness += 10
    if user_data.get('user_notes'): completeness += 10
    if user_data.get('agent_observations'): completeness += 10

    return f"Profile Completeness: {completeness}%"

@app.post("/users/update_profile")
def update_profile(req: ProfileUpdateRequest):
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_database[user_id]
    for key, value in req.dict().items():
        if value is not None:
            user_data[key] = value

    save_user_data()
    return {"message": "Profile updated successfully!", "user_id": user_id}

@app.post("/users/update_language")
def update_language(req: LanguageUpdateRequest):
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_database[user_id]
    user_data["preferred_language"] = req.new_language
    save_user_data()
    return {"message": "Language updated successfully!", "user_id": user_id}

@app.post("/users/credit_score")
def get_credit_score(req: UserSelectRequest):
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_database[user_id]
    credit_score = credit_agent.get_credit_score(user_data)
    return {"user_id": user_id, "credit_score": credit_score}

@app.post("/users/loan_recommendation")
def get_loan_recommendation(req: UserSelectRequest):
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_database[user_id]
    loan_recommendation = loan_advisor.get_loan_recommendation(user_data)
    return {"user_id": user_id, "loan_recommendation": loan_recommendation}

@app.post("/users/educational_content")
def get_educational_content(req: EducationRequest):
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_database[user_id]
    content = education_agent.get_educational_content(user_data, req.topic)
    return {"user_id": user_id, "content": content}

@app.post("/users/nbfc_recommendation")
def get_nbfc_recommendation(req: NBFCRequest):
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_database[user_id]
    nbfc_recommendations = nbfc_agent.get_nbfc_recommendations(user_data, req.region, req.classification_filter, req.language)
    return {"user_id": user_id, "nbfc_recommendations": nbfc_recommendations}

@app.post("/users/chat")
def chat_with_assistant(req: ChatRequest):
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_database[user_id]
    message = req.message
    language = req.language

    # Determine if the message is in English or Hindi
    if language.lower() == "hindi":
        message_in_english = translation_agent.translate_to_english(message)
        response_in_english = voice_agent.chat(message_in_english)
        response_in_hindi = translation_agent.translate_to_hindi(response_in_english)
        return {"user_id": user_id, "message": message, "language": language, "response": response_in_hindi}
    else:
        response_in_english = voice_agent.chat(message)
        response_in_hindi = translation_agent.translate_to_hindi(response_in_english)
        return {"user_id": user_id, "message": message, "language": language, "response": response_in_hindi}

@app.post("/users/document_processing")
def process_document(req: UserSelectRequest):
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_database[user_id]
    # Assuming document_agent.process_document takes a Pydantic model for the request
    # For now, we'll just return a placeholder response
    return {"user_id": user_id, "message": "Document processing endpoint is under development."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 