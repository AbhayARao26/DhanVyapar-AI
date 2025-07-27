"""
NBFC Recommendation Agent
Provides NBFC recommendations based on user's region and preferences
Supports English, Hindi, and Kannada with enhanced region matching
"""

import os
import json
import pandas as pd
import re
from typing import Dict, Any, Optional, List, Tuple
from difflib import SequenceMatcher
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import get_language_prompt, generate_cache_key
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NBFCRecommendationAgent:
    def __init__(self, csv_path: str = "data/RBI - List of NBFCs.csv"):
        """
        Initialize NBFC Recommendation Agent
        
        Args:
            csv_path (str): Path to the NBFC CSV file
        """
        self.csv_path = csv_path
        self.nbfc_data = None
        self.region_mappings = {}
        self.cache = {}
        
        # Common region variations and abbreviations
        self.region_variations = {
            "mumbai": ["bombay", "mumbai city", "mumbai suburban", "thane", "navi mumbai"],
            "delhi": ["new delhi", "nct", "ncr", "gurgaon", "gurugram", "noida", "faridabad"],
            "bangalore": ["bengaluru", "bangalore city", "bangalore urban"],
            "chennai": ["madras", "chennai city"],
            "kolkata": ["calcutta", "kolkata city"],
            "hyderabad": ["secunderabad", "hyderabad city"],
            "ahmedabad": ["ahmedabad city"],
            "pune": ["pune city"],
            "jaipur": ["jaipur city"],
            "lucknow": ["lucknow city"],
            "patna": ["patna city"],
            "bhubaneswar": ["bhubaneshwar", "bhubaneswar city"],
            "chandigarh": ["chandigarh city"],
            "thiruvananthapuram": ["trivandrum", "thiruvananthapuram city"],
            "andhra pradesh": ["ap", "andhra"],
            "karnataka": ["ka", "karnataka state"],
            "tamil nadu": ["tn", "tamilnadu", "tamil nadu state"],
            "maharashtra": ["mh", "maharashtra state"],
            "gujarat": ["gj", "gujarat state"],
            "west bengal": ["wb", "west bengal state"],
            "kerala": ["kl", "kerala state"],
            "punjab": ["pb", "punjab state"],
            "haryana": ["hr", "haryana state"],
            "rajasthan": ["rj", "rajasthan state"],
            "uttar pradesh": ["up", "uttar pradesh state"],
            "bihar": ["br", "bihar state"],
            "odisha": ["or", "odisha state", "orissa"],
            "telangana": ["tg", "telangana state"],
            "chhattisgarh": ["cg", "chhattisgarh state"],
            "madhya pradesh": ["mp", "madhya pradesh state"],
            "jharkhand": ["jh", "jharkhand state"],
            "assam": ["as", "assam state"],
            "manipur": ["mn", "manipur state"],
            "meghalaya": ["ml", "meghalaya state"],
            "nagaland": ["nl", "nagaland state"],
            "tripura": ["tr", "tripura state"],
            "arunachal pradesh": ["ar", "arunachal pradesh state"],
            "mizoram": ["mz", "mizoram state"],
            "sikkim": ["sk", "sikkim state"],
            "goa": ["ga", "goa state"],
            "himachal pradesh": ["hp", "himachal pradesh state"],
            "uttarakhand": ["uk", "uttarakhand state", "uttaranchal"],
            "jammu and kashmir": ["jk", "jammu and kashmir state"],
            "ladakh": ["la", "ladakh state"]
        }
        
        # NBFC classification descriptions
        self.classification_descriptions = {
            "ICC": "Investment and Credit Company - Provides loans and investments",
            "CIC": "Core Investment Company - Primarily invests in group companies",
            "MFI": "Micro Finance Institution - Focuses on small loans to low-income groups",
            "IFC": "Infrastructure Finance Company - Specializes in infrastructure financing",
            "IDF": "Infrastructure Debt Fund - Provides debt financing for infrastructure",
            "HFC": "Housing Finance Company - Specializes in housing loans",
            "NBFC-Factor": "Factoring Company - Provides factoring services",
            "NBFC-AA": "Asset Reconstruction Company - Acquires and manages distressed assets",
            "NBFC-P2P": "Peer to Peer Lending Platform - Facilitates lending between individuals"
        }
        
        # Load and preprocess NBFC data
        self._load_nbfc_data()
        self._build_region_mappings()
    
    def _load_nbfc_data(self):
        """Load and preprocess NBFC data from CSV"""
        try:
            self.nbfc_data = pd.read_csv(self.csv_path)
            
            # Clean and standardize data
            self.nbfc_data['Regional Office'] = self.nbfc_data['Regional Office'].str.strip()
            self.nbfc_data['NBFC Name'] = self.nbfc_data['NBFC Name'].str.strip()
            self.nbfc_data['Classification'] = self.nbfc_data['Classification'].str.strip()
            
            # Remove rows with missing regional office
            self.nbfc_data = self.nbfc_data.dropna(subset=['Regional Office'])
            
            print(f"Loaded {len(self.nbfc_data)} NBFC records")
            
        except Exception as e:
            print(f"Error loading NBFC data: {e}")
            self.nbfc_data = pd.DataFrame()
    
    def _build_region_mappings(self):
        """Build mappings for region variations and abbreviations"""
        if self.nbfc_data.empty:
            return
            
        # Get unique regions from data
        unique_regions = self.nbfc_data['Regional Office'].unique()
        
        # Build reverse mappings
        for region in unique_regions:
            region_lower = region.lower().strip()
            self.region_mappings[region_lower] = region
            
            # Add common abbreviations
            if region_lower in self.region_variations:
                for variation in self.region_variations[region_lower]:
                    self.region_mappings[variation] = region
    
    def _normalize_region(self, user_region: str) -> str:
        """
        Normalize user input region to match database regions
        
        Args:
            user_region (str): User input region
            
        Returns:
            str: Normalized region name
        """
        if not user_region:
            return ""
            
        user_region_lower = user_region.lower().strip()
        
        # Direct match
        if user_region_lower in self.region_mappings:
            return self.region_mappings[user_region_lower]
        
        # Fuzzy matching for similar regions
        best_match = None
        best_score = 0
        
        for region in self.region_mappings.keys():
            score = SequenceMatcher(None, user_region_lower, region).ratio()
            if score > best_score and score > 0.6:  # Threshold for similarity
                best_score = score
                best_match = region
        
        if best_match:
            return self.region_mappings[best_match]
        
        return user_region
    
    def recommend_nbfcs_by_region(self, user_region: str, 
                                 classification_filter: Optional[str] = None,
                                 max_results: int = 10) -> Dict[str, Any]:
        """
        Recommend NBFCs based on user's region
        
        Args:
            user_region (str): User's region/location
            classification_filter (str, optional): Filter by NBFC classification
            max_results (int): Maximum number of results to return
            
        Returns:
            Dict: Recommendation results with NBFC details
        """
        if self.nbfc_data.empty:
            return {
                "success": False,
                "error": "NBFC data not available",
                "recommendations": [],
                "total_found": 0
            }
        
        # Normalize user region
        normalized_region = self._normalize_region(user_region)
        
        if not normalized_region:
            return {
                "success": False,
                "error": f"Could not identify region: {user_region}",
                "recommendations": [],
                "total_found": 0,
                "suggested_regions": self._get_suggested_regions(user_region)
            }
        
        # Filter by region
        filtered_data = self.nbfc_data[
            self.nbfc_data['Regional Office'].str.contains(
                normalized_region, case=False, na=False
            )
        ]
        
        # Apply classification filter if specified
        if classification_filter:
            filtered_data = filtered_data[
                filtered_data['Classification'].str.contains(
                    classification_filter, case=False, na=False
                )
            ]
        
        # Sort by relevance (you can customize this)
        filtered_data = filtered_data.sort_values('NBFC Name')
        
        # Limit results
        if len(filtered_data) > max_results:
            filtered_data = filtered_data.head(max_results)
        
        # Prepare recommendations
        recommendations = []
        for _, row in filtered_data.iterrows():
            recommendation = {
                "name": row['NBFC Name'],
                "regional_office": row['Regional Office'],
                "classification": row['Classification'],
                "classification_description": self.classification_descriptions.get(
                    row['Classification'], "Specialized financial services"
                ),
                "address": row.get('Address', ''),
                "email": row.get('Email ID', ''),
                "corporate_id": row.get('Corporate Identification Number', ''),
                "layer": row.get('Layer', ''),
                "accepts_deposits": row.get('Whether have CoR for holding/ Accepting Public Deposits', 'No')
            }
            recommendations.append(recommendation)
        
        return {
            "success": True,
            "user_region": user_region,
            "normalized_region": normalized_region,
            "recommendations": recommendations,
            "total_found": len(filtered_data),
            "classification_filter": classification_filter
        }
    
    def _get_suggested_regions(self, user_input: str) -> List[str]:
        """Get suggested regions based on user input"""
        if not user_input:
            return []
        
        user_input_lower = user_input.lower()
        suggestions = []
        
        # Check for partial matches
        for region in self.region_mappings.keys():
            if user_input_lower in region or region in user_input_lower:
                suggestions.append(self.region_mappings[region])
        
        # Remove duplicates and limit
        suggestions = list(set(suggestions))[:5]
        return suggestions
    
    def get_nbfc_details(self, nbfc_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific NBFC
        
        Args:
            nbfc_name (str): Name of the NBFC
            
        Returns:
            Dict: Detailed NBFC information
        """
        if self.nbfc_data.empty:
            return {"success": False, "error": "NBFC data not available"}
        
        # Search for NBFC
        matches = self.nbfc_data[
            self.nbfc_data['NBFC Name'].str.contains(
                nbfc_name, case=False, na=False
            )
        ]
        
        if matches.empty:
            return {
                "success": False, 
                "error": f"NBFC '{nbfc_name}' not found",
                "suggestions": self._get_nbfc_suggestions(nbfc_name)
            }
        
        # Get the first match
        nbfc = matches.iloc[0]
        
        return {
            "success": True,
            "details": {
                "name": nbfc['NBFC Name'],
                "regional_office": nbfc['Regional Office'],
                "classification": nbfc['Classification'],
                "classification_description": self.classification_descriptions.get(
                    nbfc['Classification'], "Specialized financial services"
                ),
                "address": nbfc.get('Address', ''),
                "email": nbfc.get('Email ID', ''),
                "corporate_id": nbfc.get('Corporate Identification Number', ''),
                "layer": nbfc.get('Layer', ''),
                "accepts_deposits": nbfc.get('Whether have CoR for holding/ Accepting Public Deposits', 'No')
            }
        }
    
    def _get_nbfc_suggestions(self, nbfc_name: str) -> List[str]:
        """Get NBFC name suggestions based on partial input"""
        if not nbfc_name or self.nbfc_data.empty:
            return []
        
        suggestions = []
        nbfc_name_lower = nbfc_name.lower()
        
        # Find partial matches
        for name in self.nbfc_data['NBFC Name']:
            if nbfc_name_lower in name.lower():
                suggestions.append(name)
        
        return suggestions[:5]
    
    def get_regional_statistics(self, region: str = None) -> Dict[str, Any]:
        """
        Get statistics about NBFCs in a region or overall
        
        Args:
            region (str, optional): Specific region to analyze
            
        Returns:
            Dict: Statistical information
        """
        if self.nbfc_data.empty:
            return {"success": False, "error": "NBFC data not available"}
        
        if region:
            normalized_region = self._normalize_region(region)
            if not normalized_region:
                return {"success": False, "error": f"Region '{region}' not found"}
            
            data = self.nbfc_data[
                self.nbfc_data['Regional Office'].str.contains(
                    normalized_region, case=False, na=False
                )
            ]
        else:
            data = self.nbfc_data
        
        # Calculate statistics
        total_nbfcs = len(data)
        classifications = data['Classification'].value_counts().to_dict()
        layers = data['Layer'].value_counts().to_dict()
        deposit_accepting = len(data[data['Whether have CoR for holding/ Accepting Public Deposits'] == 'Yes'])
        
        return {
            "success": True,
            "region": region or "All India",
            "statistics": {
                "total_nbfcs": total_nbfcs,
                "by_classification": classifications,
                "by_layer": layers,
                "deposit_accepting": deposit_accepting,
                "non_deposit_accepting": total_nbfcs - deposit_accepting
            }
        }
    
    def search_nbfcs(self, query: str, search_type: str = "name", max_results: int = 10) -> Dict[str, Any]:
        """
        Search NBFCs by various criteria
        
        Args:
            query (str): Search query
            search_type (str): Type of search (name, classification, region)
            max_results (int): Maximum results to return
            
        Returns:
            Dict: Search results
        """
        if self.nbfc_data.empty:
            return {"success": False, "error": "NBFC data not available"}
        
        if not query:
            return {"success": False, "error": "Search query is required"}
        
        # Determine search column
        if search_type == "name":
            search_column = 'NBFC Name'
        elif search_type == "classification":
            search_column = 'Classification'
        elif search_type == "region":
            search_column = 'Regional Office'
        else:
            return {"success": False, "error": "Invalid search type"}
        
        # Perform search
        matches = self.nbfc_data[
            self.nbfc_data[search_column].str.contains(
                query, case=False, na=False
            )
        ]
        
        # Limit results
        if len(matches) > max_results:
            matches = matches.head(max_results)
        
        # Prepare results
        results = []
        for _, row in matches.iterrows():
            result = {
                "name": row['NBFC Name'],
                "regional_office": row['Regional Office'],
                "classification": row['Classification'],
                "address": row.get('Address', ''),
                "email": row.get('Email ID', '')
            }
            results.append(result)
        
        return {
            "success": True,
            "query": query,
            "search_type": search_type,
            "results": results,
            "total_found": len(matches)
        }
    
    def generate_recommendation_summary(self, recommendations: Dict[str, Any], 
                                      language: str = "english") -> str:
        """
        Generate a human-readable summary of NBFC recommendations
        
        Args:
            recommendations (Dict): Recommendation results
            language (str): Language for the summary
            
        Returns:
            str: Formatted summary
        """
        if not recommendations.get("success"):
            error_msg = recommendations.get("error", "Unknown error")
            if language == "hindi":
                return f"❌ त्रुटि: {error_msg}"
            elif language == "kannada":
                return f"❌ ದೋಷ: {error_msg}"
            else:
                return f"❌ Error: {error_msg}"
        
        nbfcs = recommendations.get("recommendations", [])
        total = recommendations.get("total_found", 0)
        region = recommendations.get("normalized_region", "")
        
        if total == 0:
            if language == "hindi":
                return f"🔍 {region} क्षेत्र में कोई NBFC नहीं मिला। कृपया अन्य क्षेत्र का प्रयास करें।"
            elif language == "kannada":
                return f"🔍 {region} ಪ್ರದೇಶದಲ್ಲಿ ಯಾವುದೇ NBFC ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಬೇರೆ ಪ್ರದೇಶವನ್ನು ಪ್ರಯತ್ನಿಸಿ."
            else:
                return f"🔍 No NBFCs found in {region} region. Please try another region."
        
        # Generate summary
        if language == "hindi":
            summary = f"✅ {region} क्षेत्र में {total} NBFC मिले:\n\n"
            for i, nbfc in enumerate(nbfcs[:5], 1):
                summary += f"{i}. {nbfc['name']}\n"
                summary += f"   प्रकार: {nbfc['classification_description']}\n"
                if nbfc.get('email'):
                    summary += f"   ईमेल: {nbfc['email']}\n"
                summary += "\n"
        elif language == "kannada":
            summary = f"✅ {region} ಪ್ರದೇಶದಲ್ಲಿ {total} NBFC ಕಂಡುಬಂದಿದೆ:\n\n"
            for i, nbfc in enumerate(nbfcs[:5], 1):
                summary += f"{i}. {nbfc['name']}\n"
                summary += f"   ವಿಧ: {nbfc['classification_description']}\n"
                if nbfc.get('email'):
                    summary += f"   ಇಮೇಲ್: {nbfc['email']}\n"
                summary += "\n"
        else:
            summary = f"✅ Found {total} NBFCs in {region} region:\n\n"
            for i, nbfc in enumerate(nbfcs[:5], 1):
                summary += f"{i}. {nbfc['name']}\n"
                summary += f"   Type: {nbfc['classification_description']}\n"
                if nbfc.get('email'):
                    summary += f"   Email: {nbfc['email']}\n"
                summary += "\n"
        
        if total > 5:
            if language == "hindi":
                summary += f"... और {total - 5} अधिक NBFC"
            elif language == "kannada":
                summary += f"... ಮತ್ತು {total - 5} ಹೆಚ್ಚಿನ NBFC"
            else:
                summary += f"... and {total - 5} more NBFCs"
        
        return summary 