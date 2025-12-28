import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def summarize_feedback(cleaned_texts: list) -> str:
    """
    Draga saman endurgjöf viðskiptavina úr mörgum gagnagrunnum
    
    Vistast i output (sem summary report)

    Parameters: cleaned_texts

    Skilar: Skýrsla í markdown sem strengur
    """
    
    if not cleaned_texts:
        return "No data available"
    
    # Limit á input size
    sample_texts = cleaned_texts[:30]

    formatted_feedback = "\n".join(
        f"- {text}" for text in sample_texts if text.strip()
    )
    
    prompt = f"""
You are a data analyst working with customer feedback.

Analyze the following feedback collected from multiple sources:

{formatted_feedback}

Return a Markdown report with the following sections:

## Overall Sentiment
## Common Themes
## Frequent Issues
## Actionable Recommendations

Keep the tone professional and business-focused.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.2,
            }
        )
        
        return str(response.text)
    
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"Error generating summary: {str(e)}"


if __name__ == "__main__":
    print("Testing AI Summary\n")
    
    test_feedback = [
        "the app crashes when i log in",
        "love the new dashboard design",
        "customer service was slow but helpful",
        "performance is terrible during peak hours",
        "onboarding process was smooth"
    ]
    
    summary = summarize_feedback(test_feedback)
    print(summary)