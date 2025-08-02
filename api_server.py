from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import os
import sys
import json
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import borrower platform agents
try:
    from borrower_platform.agents.user_onboarding_agent import UserOnboardingAgent
    from borrower_platform.agents.credit_scoring_agent import CreditScoringAgent
    from borrower_platform.agents.loan_risk_advisor_agent import LoanRiskAdvisorAgent
    from borrower_platform.agents.educational_content_agent import EducationalContentAgent
    from borrower_platform.agents.document_processing_agent import DocumentProcessingAgent
    from borrower_platform.agents.voice_assistant_agent import VoiceAssistantAgent
    from borrower_platform.agents.translation_agent import TranslationAgent
    from borrower_platform.agents.lender_recommendation_agent import LenderRecommendationAgent
    from borrower_platform.agents.property_verification_agent import PropertyVerificationAgent
    from borrower_platform.agents.credit_metrics_explainer import CreditMetricsExplainer
except ImportError as e:
    logger.error(f"Failed to import borrower platform agents: {e}")
    # Create placeholder classes for missing agents
    class PlaceholderAgent:
        def __init__(self):
            pass
        def __call__(self, *args, **kwargs):
            return {"error": "Agent not available"}
    
    UserOnboardingAgent = PlaceholderAgent
    CreditScoringAgent = PlaceholderAgent
    LoanRiskAdvisorAgent = PlaceholderAgent
    EducationalContentAgent = PlaceholderAgent
    DocumentProcessingAgent = PlaceholderAgent
    VoiceAssistantAgent = PlaceholderAgent
    TranslationAgent = PlaceholderAgent
    LenderRecommendationAgent = PlaceholderAgent
    PropertyVerificationAgent = PlaceholderAgent
    CreditMetricsExplainer = PlaceholderAgent

# Import MFI platform agents
try:
    from microfinance_platform.lender_agents.creditsense_analyst import CreditSenseAnalyst
    from microfinance_platform.lender_agents.fundflow_forecaster import FundFlowForecaster
    from microfinance_platform.lender_agents.policypulse_advisor import PolicyPulseAdvisor
    from microfinance_platform.lender_agents.opsgenie_agent import OpsGenieAgent
except ImportError as e:
    logger.error(f"Failed to import MFI platform agents: {e}")
    # Create placeholder classes for missing agents
    class PlaceholderMFIAgent:
        def __init__(self):
            pass
        def __call__(self, *args, **kwargs):
            return {"error": "MFI Agent not available"}
    
    CreditSenseAnalyst = PlaceholderMFIAgent
    FundFlowForecaster = PlaceholderMFIAgent
    PolicyPulseAdvisor = PlaceholderMFIAgent
    OpsGenieAgent = PlaceholderMFIAgent

app = FastAPI(
    title="DhanVyapar AI - Microfinance Platform API",
    description="Comprehensive API for rural microfinance operations with AI agents",
    version="1.0.0"
)

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
mfi_database = {}
current_user_id = None

# Initialize agents with error handling
def initialize_agents():
    """Initialize all agents with proper error handling"""
    agents = {}
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        logger.warning("GROQ_API_KEY not found. Some agents may not work properly.")
    
    # Initialize borrower platform agents
    try:
        agents['onboarding'] = UserOnboardingAgent(groq_api_key)
        logger.info("UserOnboardingAgent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize UserOnboardingAgent: {e}")
        agents['onboarding'] = None
    
    try:
        agents['credit'] = CreditScoringAgent(groq_api_key)
        logger.info("CreditScoringAgent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize CreditScoringAgent: {e}")
        agents['credit'] = None
    
    try:
        agents['loan_advisor'] = LoanRiskAdvisorAgent(groq_api_key)
        logger.info("LoanRiskAdvisorAgent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LoanRiskAdvisorAgent: {e}")
        agents['loan_advisor'] = None
    
    try:
        agents['education'] = EducationalContentAgent(groq_api_key)
        logger.info("EducationalContentAgent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize EducationalContentAgent: {e}")
        agents['education'] = None
    
    try:
        agents['document'] = DocumentProcessingAgent(groq_api_key)
        logger.info("DocumentProcessingAgent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize DocumentProcessingAgent: {e}")
        agents['document'] = None
    
    try:
        agents['voice'] = VoiceAssistantAgent(groq_api_key)
        logger.info("VoiceAssistantAgent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize VoiceAssistantAgent: {e}")
        agents['voice'] = None
    
    try:
        agents['translation'] = TranslationAgent(groq_api_key)
        logger.info("TranslationAgent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize TranslationAgent: {e}")
        agents['translation'] = None
    
    try:
        agents['lender'] = LenderRecommendationAgent(groq_api_key)
        logger.info("LenderRecommendationAgent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LenderRecommendationAgent: {e}")
        agents['lender'] = None
    
    try:
        agents['property'] = PropertyVerificationAgent(groq_api_key)
        logger.info("PropertyVerificationAgent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize PropertyVerificationAgent: {e}")
        agents['property'] = None
    
    try:
        agents['credit_metrics'] = CreditMetricsExplainer(groq_api_key)
        logger.info("CreditMetricsExplainer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize CreditMetricsExplainer: {e}")
        agents['credit_metrics'] = None
    
    # Initialize MFI platform agents
    try:
        agents['credit_sense'] = CreditSenseAnalyst(groq_api_key)
        logger.info("CreditSenseAnalyst initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize CreditSenseAnalyst: {e}")
        agents['credit_sense'] = None
    
    try:
        agents['fund_flow'] = FundFlowForecaster(groq_api_key)
        logger.info("FundFlowForecaster initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize FundFlowForecaster: {e}")
        agents['fund_flow'] = None
    
    try:
        agents['policy_pulse'] = PolicyPulseAdvisor(groq_api_key)
        logger.info("PolicyPulseAdvisor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize PolicyPulseAdvisor: {e}")
        agents['policy_pulse'] = None
    
    try:
        agents['ops_genie'] = OpsGenieAgent(groq_api_key)
        logger.info("OpsGenieAgent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OpsGenieAgent: {e}")
        agents['ops_genie'] = None
    
    return agents

# Initialize agents
agents = initialize_agents()

USER_DATA_FILE = "user_data.json"
MFI_DATA_FILE = "mfi_data.json"

def load_user_data():
    """Load user data from file"""
    global user_database
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                user_database = json.load(f)
                logger.info(f"Loaded {len(user_database)} users from database")
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
        user_database = {}

def save_user_data():
    """Save user data to file"""
    try:
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_database, f, indent=2, ensure_ascii=False)
        logger.info("User data saved successfully")
    except Exception as e:
        logger.error(f"Error saving user data: {e}")

def load_mfi_data():
    """Load MFI data from file"""
    global mfi_database
    try:
        if os.path.exists(MFI_DATA_FILE):
            with open(MFI_DATA_FILE, "r", encoding="utf-8") as f:
                mfi_database = json.load(f)
                logger.info(f"Loaded {len(mfi_database)} MFIs from database")
    except Exception as e:
        logger.error(f"Error loading MFI data: {e}")
        mfi_database = {}

def save_mfi_data():
    """Save MFI data to file"""
    try:
        with open(MFI_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(mfi_database, f, indent=2, ensure_ascii=False)
        logger.info("MFI data saved successfully")
    except Exception as e:
        logger.error(f"Error saving MFI data: {e}")

# Load data on startup
load_user_data()
load_mfi_data()

# --- Pydantic Models ---

class UserCreateRequest(BaseModel):
    name: str = Field(..., description="Full name of the user")
    phone: str = Field(..., description="Phone number")
    village: Optional[str] = Field("", description="Village name")

class UserSelectRequest(BaseModel):
    user_id: str = Field(..., description="User ID")

class LanguageUpdateRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    new_language: str = Field(..., description="New preferred language")

class ProfileUpdateRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
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
    user_id: str = Field(..., description="User ID")
    topic: str = Field(..., description="Educational topic")

class LoanRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    loan_amount: float = Field(..., description="Requested loan amount")
    loan_type: str = Field(..., description="Type of loan")
    purpose: str = Field(..., description="Loan purpose")
    tenure_months: Optional[int] = Field(12, description="Loan tenure in months")

class LenderRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    region: str = Field(..., description="Region for lender search")
    classification_filter: Optional[str] = Field("", description="Lender classification filter")
    language: Optional[str] = Field("English", description="Preferred language")

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    message: str = Field(..., description="User message")
    language: str = Field(..., description="Language of the message")

class DocumentProcessRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    document_type: str = Field(..., description="Type of document")
    document_data: str = Field(..., description="Document data or text")

class PropertyVerificationRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    property_address: str = Field(..., description="Property address")
    property_type: str = Field(..., description="Type of property")
    verification_type: str = Field(..., description="Type of verification needed")

class MFICreateRequest(BaseModel):
    name: str = Field(..., description="MFI name")
    type: str = Field(..., description="MFI type")
    region: str = Field(..., description="Operating region")
    contact_info: Dict[str, Any] = Field(..., description="Contact information")

class MFIAnalysisRequest(BaseModel):
    mfi_id: str = Field(..., description="MFI ID")
    analysis_type: str = Field(..., description="Type of analysis")
    parameters: Optional[Dict[str, Any]] = Field({}, description="Analysis parameters")

# --- API Endpoints ---

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "DhanVyapar AI - Microfinance Platform API",
        "version": "1.0.0",
        "status": "running",
        "available_endpoints": [
            "/users/* - User management endpoints",
            "/mfi/* - MFI management endpoints",
            "/agents/* - Agent interaction endpoints",
            "/docs - API documentation"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_available": {name: agent is not None for name, agent in agents.items()}
    }

# --- User Management Endpoints ---

@app.get("/users")
def get_users():
    """Get all users"""
    return {
        "users": list(user_database.keys()),
        "total_users": len(user_database)
    }

@app.post("/users/create")
def create_user(req: UserCreateRequest):
    """Create a new user"""
    name, phone, village = req.name, req.phone, req.village
    if not name or not phone:
        raise HTTPException(status_code=400, detail="Name and phone number are required")
    
    user_id = f"{name}_{phone}"
    
    if user_id in user_database:
        raise HTTPException(status_code=409, detail="User already exists")
    
    # Initialize user data with comprehensive schema
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
        "agent_observations": "",
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    
    save_user_data()
    return {
        "message": f"User {name} created successfully!",
        "user_id": user_id,
        "dashboard": get_user_dashboard(user_id)
    }

@app.post("/users/select")
def select_user(req: UserSelectRequest):
    """Select a user and get their dashboard"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "dashboard": get_user_dashboard(user_id),
        "profile_completeness": get_profile_completeness(user_database[user_id])
    }

@app.get("/users/{user_id}")
def get_user(user_id: str):
    """Get user details"""
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "user_data": user_database[user_id],
        "profile_completeness": get_profile_completeness(user_database[user_id])
    }

@app.post("/users/update_profile")
def update_profile(req: ProfileUpdateRequest):
    """Update user profile"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_database[user_id]
    update_data = req.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        if key != "user_id" and value is not None:
            user_data[key] = value
    
    user_data["last_updated"] = datetime.now().isoformat()
    save_user_data()
    
    return {
        "message": "Profile updated successfully!",
        "user_id": user_id,
        "profile_completeness": get_profile_completeness(user_data)
    }

@app.post("/users/update_language")
def update_language(req: LanguageUpdateRequest):
    """Update user's preferred language"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_database[user_id]
    user_data["preferred_language"] = req.new_language
    user_data["last_updated"] = datetime.now().isoformat()
    save_user_data()
    
    return {
        "message": "Language updated successfully!",
        "user_id": user_id,
        "preferred_language": req.new_language
    }

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    """Delete a user"""
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    del user_database[user_id]
    save_user_data()
    
    return {"message": f"User {user_id} deleted successfully"}

# --- Agent Interaction Endpoints ---

@app.post("/agents/onboarding/conversation")
def conversational_onboarding(req: ChatRequest):
    """Start or continue conversational onboarding"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not agents['onboarding']:
        raise HTTPException(status_code=503, detail="Onboarding agent not available")
    
    try:
        user_data = user_database[user_id]
        result = agents['onboarding'].conversational_data_collection(
            req.message, 
            language=req.language
        )
        
        # Update user data if new information was collected
        if result.get('updated_data'):
            user_data.update(result['updated_data'])
            user_data["last_updated"] = datetime.now().isoformat()
            save_user_data()
        
        return {
            "user_id": user_id,
            "response": result.get('response', ''),
            "next_question": result.get('next_question', ''),
            "is_complete": result.get('is_complete', False),
            "collected_data": result.get('collected_data', {})
        }
    except Exception as e:
        logger.error(f"Error in conversational onboarding: {e}")
        raise HTTPException(status_code=500, detail=f"Onboarding error: {str(e)}")

@app.post("/agents/credit_score")
def get_credit_score(req: UserSelectRequest):
    """Get user's credit score"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not agents['credit']:
        raise HTTPException(status_code=503, detail="Credit scoring agent not available")
    
    try:
        user_data = user_database[user_id]
        credit_result = agents['credit'].calculate_credit_score(user_data)
        
        return {
            "user_id": user_id,
            "credit_score": credit_result.get('credit_score'),
            "risk_level": credit_result.get('risk_level'),
            "recommendation": credit_result.get('recommendation'),
            "key_factors": credit_result.get('key_risk_factors', []),
            "completeness_check": credit_result.get('completeness_check', {})
        }
    except Exception as e:
        logger.error(f"Error in credit scoring: {e}")
        raise HTTPException(status_code=500, detail=f"Credit scoring error: {str(e)}")

@app.post("/agents/loan_recommendation")
def get_loan_recommendation(req: LoanRequest):
    """Get loan recommendation for user"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not agents['loan_advisor']:
        raise HTTPException(status_code=503, detail="Loan advisor agent not available")
    
    try:
        user_data = user_database[user_id]
        loan_request = {
            "amount": req.loan_amount,
            "type": req.loan_type,
            "purpose": req.purpose,
            "tenure_months": req.tenure_months
        }
        
        recommendation = agents['loan_advisor'].provide_detailed_loan_recommendation(
            user_data, 
            loan_request
        )
        
        return {
            "user_id": user_id,
            "loan_recommendation": recommendation,
            "loan_request": loan_request
        }
    except Exception as e:
        logger.error(f"Error in loan recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Loan recommendation error: {str(e)}")

@app.post("/agents/lender_recommendation")
def get_lender_recommendation(req: LenderRequest):
    """Get lender recommendations for user"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not agents['lender']:
        raise HTTPException(status_code=503, detail="Lender recommendation agent not available")
    
    try:
        user_data = user_database[user_id]
        loan_request = {
            "region": req.region,
            "classification_filter": req.classification_filter,
            "language": req.language
        }
        
        recommendations = agents['lender'].recommend_lenders(user_data, loan_request)
        
        return {
            "user_id": user_id,
            "lender_recommendations": recommendations,
            "search_parameters": loan_request
        }
    except Exception as e:
        logger.error(f"Error in lender recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Lender recommendation error: {str(e)}")

@app.post("/agents/educational_content")
def get_educational_content(req: EducationRequest):
    """Get educational content for user"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not agents['education']:
        raise HTTPException(status_code=503, detail="Educational content agent not available")
    
    try:
        user_data = user_database[user_id]
        content = agents['education'].get_educational_content(user_data, req.topic)
        
        return {
            "user_id": user_id,
            "topic": req.topic,
            "content": content
        }
    except Exception as e:
        logger.error(f"Error in educational content: {e}")
        raise HTTPException(status_code=500, detail=f"Educational content error: {str(e)}")

@app.post("/agents/chat")
def chat_with_assistant(req: ChatRequest):
    """Chat with voice assistant"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not agents['voice'] or not agents['translation']:
        raise HTTPException(status_code=503, detail="Voice or translation agent not available")
    
    try:
        user_data = user_database[user_id]
        message = req.message
        language = req.language

        # Handle multilingual chat
        if language.lower() == "hindi":
            message_in_english = agents['translation'].translate_to_english(message)
            response_in_english = agents['voice'].chat(message_in_english)
            response_in_hindi = agents['translation'].translate_to_hindi(response_in_english)
            final_response = response_in_hindi
        else:
            response_in_english = agents['voice'].chat(message)
            response_in_hindi = agents['translation'].translate_to_hindi(response_in_english)
            final_response = response_in_hindi

        return {
            "user_id": user_id,
            "message": message,
            "language": language,
            "response": final_response
        }
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/agents/document_processing")
def process_document(req: DocumentProcessRequest):
    """Process user documents"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not agents['document']:
        raise HTTPException(status_code=503, detail="Document processing agent not available")
    
    try:
        user_data = user_database[user_id]
        result = agents['document'].process_document(
            req.document_type,
            req.document_data,
            user_data
        )
        
        return {
            "user_id": user_id,
            "document_type": req.document_type,
            "processing_result": result
        }
    except Exception as e:
        logger.error(f"Error in document processing: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing error: {str(e)}")

@app.post("/agents/property_verification")
def verify_property(req: PropertyVerificationRequest):
    """Verify property details"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not agents['property']:
        raise HTTPException(status_code=503, detail="Property verification agent not available")
    
    try:
        user_data = user_database[user_id]
        result = agents['property'].verify_property(
            req.property_address,
            req.property_type,
            req.verification_type,
            user_data
        )
        
        return {
            "user_id": user_id,
            "property_address": req.property_address,
            "verification_result": result
        }
    except Exception as e:
        logger.error(f"Error in property verification: {e}")
        raise HTTPException(status_code=500, detail=f"Property verification error: {str(e)}")

@app.post("/agents/credit_metrics_explanation")
def explain_credit_metrics(req: UserSelectRequest):
    """Explain credit metrics to user"""
    user_id = req.user_id
    if user_id not in user_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not agents['credit_metrics']:
        raise HTTPException(status_code=503, detail="Credit metrics explainer not available")
    
    try:
        user_data = user_database[user_id]
        explanation = agents['credit_metrics'].explain_credit_metrics(user_data)
        
        return {
            "user_id": user_id,
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Error in credit metrics explanation: {e}")
        raise HTTPException(status_code=500, detail=f"Credit metrics explanation error: {str(e)}")

# --- MFI Platform Endpoints ---

@app.get("/mfi")
def get_mfis():
    """Get all MFIs"""
    return {
        "mfis": list(mfi_database.keys()),
        "total_mfis": len(mfi_database)
    }

@app.post("/mfi/create")
def create_mfi(req: MFICreateRequest):
    """Create a new MFI"""
    mfi_id = f"{req.name}_{req.type}"
    
    if mfi_id in mfi_database:
        raise HTTPException(status_code=409, detail="MFI already exists")
    
    mfi_database[mfi_id] = {
        "name": req.name,
        "type": req.type,
        "region": req.region,
        "contact_info": req.contact_info,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    
    save_mfi_data()
    return {
        "message": f"MFI {req.name} created successfully!",
        "mfi_id": mfi_id
    }

@app.post("/mfi/analysis")
def analyze_mfi(req: MFIAnalysisRequest):
    """Perform MFI analysis"""
    mfi_id = req.mfi_id
    if mfi_id not in mfi_database:
        raise HTTPException(status_code=404, detail="MFI not found")
    
    mfi_data = mfi_database[mfi_id]
    analysis_type = req.analysis_type
    
    try:
        if analysis_type == "credit_analysis" and agents['credit_sense']:
            result = agents['credit_sense'].analyze_portfolio(mfi_data, req.parameters)
        elif analysis_type == "fund_flow" and agents['fund_flow']:
            result = agents['fund_flow'].forecast_fund_flow(mfi_data, req.parameters)
        elif analysis_type == "policy_advice" and agents['policy_pulse']:
            result = agents['policy_pulse'].provide_policy_advice(mfi_data, req.parameters)
        elif analysis_type == "operations" and agents['ops_genie']:
            result = agents['ops_genie'].optimize_operations(mfi_data, req.parameters)
        else:
            raise HTTPException(status_code=400, detail=f"Analysis type '{analysis_type}' not supported or agent not available")
        
        return {
            "mfi_id": mfi_id,
            "analysis_type": analysis_type,
            "result": result
        }
    except Exception as e:
        logger.error(f"Error in MFI analysis: {e}")
        raise HTTPException(status_code=500, detail=f"MFI analysis error: {str(e)}")

# --- Utility Functions ---

def get_user_dashboard(user_id: str) -> str:
    """Generate user dashboard"""
    if user_id not in user_database:
        return "❌ User not found"
    
    user_data = user_database[user_id]
    completeness = get_profile_completeness(user_data)
    
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
{completeness}

## 🎯 Available Actions
Use the API endpoints to:
- Complete profile information
- Get credit score assessment
- Apply for loan recommendations
- Access financial education content
- Chat with voice assistant
- Process documents
- Verify properties
"""
    return dashboard

def get_profile_completeness(user_data: Dict[str, Any]) -> str:
    """Calculate profile completeness percentage"""
    fields = [
        'full_name', 'phone_number', 'village_name', 'gender', 'age',
        'primary_occupation', 'monthly_income', 'monthly_expenses',
        'savings_per_month', 'bank_account_status', 'repayment_history',
        'group_membership', 'owns_land', 'land_area', 'land_type',
        'aadhaar_number', 'voter_id', 'district', 'state', 'pincode',
        'house_type', 'electricity_connection', 'number_of_dependents',
        'secondary_income_sources', 'bank_name', 'past_loan_amounts',
        'patta_or_katha_number', 'property_location', 'owns_smartphone',
        'knows_how_to_use_apps', 'preferred_mode_of_communication',
        'internet_availability', 'user_notes', 'agent_observations'
    ]
    
    completed_fields = sum(1 for field in fields if user_data.get(field))
    total_fields = len(fields)
    completeness = (completed_fields / total_fields) * 100
    
    return f"Profile Completeness: {completeness:.1f}% ({completed_fields}/{total_fields} fields)"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 