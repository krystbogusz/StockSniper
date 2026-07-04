import json
from google import genai
from app.core.config import settings
from app.core.logger import monitor_logger

if settings.llm_api_key and settings.llm_api_key != "your_gemini_api_key_here":
    client = genai.Client(api_key=settings.llm_api_key)
else:
    client = None


def check_availability(text_content: str, sizes: list[str]) -> tuple[list[str], str]:
    if not client:
        monitor_logger.error("LLM Model not configured.")
        return [], "Unknown Product"

    prompt = f"""
Analyze the following text from an e-commerce website and determine if the MAIN product is available in any of the provided sizes for purchase.
CRITICAL INSTRUCTION: The text may contain information about multiple products (e.g. 'Recommended', 'Others also bought', 'isRelatedTo', or nested JSON-LD data for cross-selling). You MUST ignore these secondary products and focus EXCLUSIVELY on the primary product featured on the page. 
Return ONLY a valid JSON string without markdown blocks, indicating the available sizes from the list AND the name of the main product.
If the main product is out of stock in the requested sizes, return an empty list for sizes, but STILL return the product name.
Expected response example: {{"available_sizes": ["42", "43"], "product_name": "FC Barcelona Home Shirt 26/27"}}

Requested sizes: {sizes}

Website text:
{text_content[:500000]}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = (
                response_text.replace("```json", "").replace("```", "").strip()
            )
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()

        data = json.loads(response_text)
        return data.get("available_sizes", []), data.get(
            "product_name", "Unknown Product"
        )
    except Exception as e:
        monitor_logger.error(f"LLM Error in check_availability: {e}")
        raise e


def check_url_safety(url: str) -> tuple[bool, str]:
    if not client:
        return True, "LLM not configured, skipping safety check."

    prompt = f"""
Evaluate if the following URL is a safe e-commerce or product link.
Ensure that it is not a link to malware, phishing, or other dangerous content.
Return ONLY a valid JSON string with 'is_safe' (boolean) and 'reason' (string explaining your decision).
Example: {{"is_safe": false, "reason": "The domain appears to be a known phishing site."}}

URL to evaluate: {url}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = (
                response_text.replace("```json", "").replace("```", "").strip()
            )
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()

        data = json.loads(response_text)
        is_safe = data.get("is_safe", False)
        reason = data.get("reason", "No reason provided by LLM.")
        return is_safe, reason
    except Exception as e:
        from app.core.logger import api_logger

        api_logger.error(f"LLM Error in check_url_safety: {e}")
        return False, f"Failed to verify URL safety due to an internal AI error: {e}"
