import os
import json
from google import genai
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Confidence threshold fyrir manual review
CONFIDENCE_THRESHOLD = 0.7

def analyze_incident(incident_text: str, source: str = "unknown") -> Dict[str, Any]:
    """
    Greinir incident/feedback og skilar skipulögðum ákvörðunargögnum
    
    Þetta er kjarninn i þessu verkenfi:
    - Flokkar alvarleika/ severity (critical/high/medium/low)
    - Greinir flokk/category (performance/ux/service/technical/billing)
    - Mælir með aðgerð/action (escalate/monitor/autofix/dismiss)
    - Skilar confidence score
    
    Inntaksgögn:
     incident_text: incident/feedback texti
     source: data source (api/csv/webhook)
    
    Skilar: Dictionary
    """
    
    if not incident_text or not incident_text.strip():
        return {
            "severity": "low",
            "category": "unknown",
            "recommended_action": "dismiss",
            "confidence": 0.0,
            "reasoning": "Empty or invalid input",
            "source": source,
            "needs_manual_review": False
        }
    
    prompt = f"""You are an AI system that analyzes customer incidents and operational issues.

Analyze this incident and return ONLY a valid JSON object (no markdown, no explanation):

INCIDENT: {incident_text}
SOURCE: {source}

Return this exact structure:
{{
  "severity": "critical|high|medium|low",
  "category": "performance|ux|service|technical|billing|other",
  "recommended_action": "escalate|monitor|autofix|dismiss",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation in 1-2 sentences"
}}

SEVERITY DEFINITIONS:
- critical: System down, data loss, security breach, affects all users
- high: Major feature broken, affects many users, revenue impact
- medium: Minor bug, affects some users, workaround exists
- low: Cosmetic issue, single user, minor inconvenience

ACTIONS:
- escalate: Needs immediate engineering attention
- monitor: Track but not urgent
- autofix: Can be resolved automatically
- dismiss: Not actionable or spam

Return ONLY the JSON, nothing else."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        
        # Lesa json response
        decision = json.loads(response.text)
        
        # Metadata
        decision["source"] = source
        decision["raw_text"] = incident_text[:200]
        
        # Validate structure
        required_keys = ["severity", "category", "recommended_action", "confidence", "reasoning"]
        for key in required_keys:
            if key not in decision:
                raise ValueError(f"Missing required key: {key}")
        
        # Validate severity
        valid_severities = ["critical", "high", "medium", "low"]
        if decision["severity"] not in valid_severities:
            decision["severity"] = "medium"
        
        # Validate confidence
        if not isinstance(decision["confidence"], (int, float)) or not (0 <= decision["confidence"] <= 1):
            decision["confidence"] = 0.5

        # Bæta við needs_manual_review ef confidence < threshold
        # Ef confidence er lág, downgrade til medium og flag fyrir manual review
        if decision["confidence"] < CONFIDENCE_THRESHOLD:
            decision["needs_manual_review"] = True
            if decision["severity"] in ["critical", "high"]:
                decision["severity"] = "medium"
        else:
            decision["needs_manual_review"] = False

        return decision
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {response.text[:200]}")
        
        # Fallback
        return {
            "severity": "medium",
            "category": "other",
            "recommended_action": "monitor",
            "confidence": 0.3,
            "reasoning": "Failed to parse AI response, defaulting to safe values",
            "source": source,
            "error": str(e),
            "needs_manual_review": True  # Alltaf flagga fyrir review ef parsing error
        }
    
    except Exception as e:
        print(f"Error in AI decision: {e}")
        
        # Fallback
        return {
            "severity": "medium",
            "category": "other",
            "recommended_action": "monitor",
            "confidence": 0.0,
            "reasoning": f"Error during analysis: {str(e)}",
            "source": source,
            "error": str(e),
            "needs_manual_review": True  # Alltaf flagga fyrir review ef error
        }


def batch_analyze_incidents(incidents: list) -> list:
    """
    Greinir mörg atvik í einni lotu (batch)

    Færibreytur:
    incidents: Listi af orðabókum (dict) þar sem hver orðabók inniheldur lykla:
    'text': Hráan texta atviks eða endurgjafar
    'source': Uppruni gagna
    Skilar:
    Listi af orðabókum, þar sem hver orðabók inniheldur skipulögða ákvörðun fyrir tiltekið atvik.
    """
    decisions = []
    
    for idx, incident in enumerate(incidents):
        text = incident.get("text", "")
        source = incident.get("source", "unknown")
        
        print(f"Analyzing incident {idx + 1}/{len(incidents)}...")
        decision = analyze_incident(text, source)
        decisions.append(decision)
    
    return decisions


def get_critical_incidents(decisions: list) -> list:
    """
    Sía atvik með alvarleika

    Parameters: decisions: List of decision dictionaries

    Skilar:Lista sem innihalda aðeins atvik með alvarleika critical og high
    """
    SEVERITY_PRIORITY = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3
    }

    critical = [
        d for d in decisions
        if d.get("severity") in ["critical", "high"]
    ]

    return sorted(
        critical,
        key=lambda x: (
            SEVERITY_PRIORITY.get(x.get("severity", "low"), 3),
            -x.get("confidence", 0)
        )
    )


if __name__ == "__main__":
    #Test fra chat
    test_cases = [
        {
            "text": "The app crashes every time I try to log in. This has been happening for 3 hours.",
            "source": "api"
        },
        {
            "text": "The onboarding process was very smooth and easy",
            "source": "csv"
        },
        {
            "text": "Performance is terrible during peak hours, pages take 30+ seconds to load",
            "source": "api"
        },
        {
            "text": "Customer service was helpful but slow",
            "source": "csv"
        }
    ]
    
    print("Testing AI Decision Engine\n")
    
    for test in test_cases:
        print(f"Input: {test['text'][:60]}...")
        decision = analyze_incident(test["text"], test["source"])
        print(f"Decision: {json.dumps(decision, indent=2)}\n")
    
    print("\nTesting batch analysis...")
    decisions = batch_analyze_incidents(test_cases)
    
    print(f"\nCritical/High incidents: {len(get_critical_incidents(decisions))}")
    for incident in get_critical_incidents(decisions):
        print(f"  - [{incident['severity'].upper()}] {incident['reasoning']}")