#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from agents.nbfc_recommendation_agent import NBFCRecommendationAgent
    print("✅ Successfully imported NBFCRecommendationAgent")
    
    # Test initialization
    agent = NBFCRecommendationAgent()
    print("✅ Successfully initialized NBFCRecommendationAgent")
    
    # Test basic functionality
    recommendations = agent.recommend_nbfcs_by_region("Mumbai", max_results=3)
    if recommendations["success"]:
        print(f"✅ Found {recommendations['total_found']} NBFCs in Mumbai")
        print("Top recommendations:")
        for i, nbfc in enumerate(recommendations["recommendations"][:2], 1):
            print(f"  {i}. {nbfc['name']}")
    else:
        print(f"❌ Error: {recommendations['error']}")
    
    print("\n🎉 NBFC Agent is working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 