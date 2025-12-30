import os
import sys
import requests
from praval import agent
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv(override=True)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    OPENAI_API_KEY = OPENAI_API_KEY.strip()
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Configure Gemini 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:

    GEMINI_API_KEY = GEMINI_API_KEY.strip()


def summarize_with_openai(text: str) -> str:
    """Primary summarization using OpenAI"""
    if not openai_client:
        raise Exception("OpenAI API key not configured")
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following HackerNews post in exactly 2 simple sentences:\n\n{text}"
            }
        ],
        temperature=0.5,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()


def summarize_with_gemini(text: str) -> str:
    """Fallback summarization using Gemini REST API"""
    if not GEMINI_API_KEY:
        raise Exception("Gemini API key not configured")
    
    # Try multiple Gemini model names and API versions
    model_configs = [
        ("v1beta", "gemini-1.5-flash-latest"),
        ("v1beta", "gemini-1.5-flash"),
        ("v1beta", "gemini-1.0-pro-latest"),
        ("v1beta", "gemini-1.0-pro"),
        ("v1", "gemini-1.5-flash-latest"),
        ("v1", "gemini-1.5-flash"),
    ]
    
    prompt = f"Summarize the following HackerNews post in exactly 2 simple sentences:\n\n{text}"
    
    last_error = None
    for api_version, model_name in model_configs:
        try:
            url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                summary = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                return summary
            else:
                raise Exception(f"No content in response for {model_name}")
                
        except Exception as e:
            last_error = f"{api_version}/{model_name}: {e}"
            continue  
    
    # If all models failed, raise the last error
    raise Exception(f"All Gemini models failed. Last error: {last_error}")


@agent("hn_summarizer", responds_to=["summary_request"])
def hn_summary_agent(spore):
    """
    Praval agent that summarizes HackerNews posts.
    Uses OpenAI first, Gemini as fallback.
    """

    text = spore.knowledge.get("text", "")

    if not text:
        return {"summary": "No content available to summarize."}

    # Try OpenAI first
    try:
        summary = summarize_with_openai(text)
        print(f"   ✓ Summary generated using OpenAI", flush=True)
        print(f"   Summary: {summary}\n", flush=True)
        sys.stdout.flush()
        return {"summary": summary}

    except Exception as openai_error:
        print(f"   OpenAI failed: {openai_error}")
        print("   Trying Gemini fallback...")

        # Fallback to Gemini
        try:
            summary = summarize_with_gemini(text)
            print(f"   ✓ Summary generated using Gemini (fallback)", flush=True)
            print(f"   Summary: {summary}\n", flush=True)
            sys.stdout.flush()
            return {"summary": summary}

        except Exception as gemini_error:
            error_msg = f"Summary generation failed: Both OpenAI and Gemini APIs are unavailable."
            print(f"   Gemini failed: {gemini_error}")
            print(f"   {error_msg}\n")
            return {"summary": error_msg}
