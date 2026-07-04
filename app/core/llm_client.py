import json
import google.generativeai as genai
from app.core.config import settings

if settings.llm_api_key and settings.llm_api_key != "your_gemini_api_key_here":
    genai.configure(api_key=settings.llm_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

def check_availability(text_content: str, sizes: list[str]) -> list[str]:
    if not model:
        print("LLM Model not configured.", flush=True)
        return []

    prompt = f"""
Analyze the following text from an e-commerce website and determine if the product is available in any of the provided sizes for purchase.
Return ONLY a valid JSON string without markdown blocks, indicating the available sizes from the list.
If none are available, return an empty list.
Expected response example: {{"available_sizes": ["42", "43"]}}

Requested sizes: {sizes}

Website text:
{text_content[:25000]}
"""
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
            
        data = json.loads(response_text)
        return data.get("available_sizes", [])
    except Exception as e:
        print(f"LLM Error in check_availability: {e}", flush=True)
        return []

def check_url_safety(url: str) -> tuple[bool, str]:
    if not model:
        return True, "LLM not configured, skipping safety check."

    prompt = f"""
Evaluate if the following URL is a safe e-commerce or product link.
Ensure that it is not a link to malware, phishing, or other dangerous content.
Return ONLY a valid JSON string with 'is_safe' (boolean) and 'reason' (string explaining your decision).
Example: {{"is_safe": false, "reason": "The domain appears to be a known phishing site."}}

URL to evaluate: {url}
"""
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
            
        data = json.loads(response_text)
        is_safe = data.get("is_safe", False)
        reason = data.get("reason", "No reason provided by LLM.")
        return is_safe, reason
    except Exception as e:
        print(f"LLM Error in check_url_safety: {e}", flush=True)
        return False, f"Failed to verify URL safety due to an internal AI error: {e}"
