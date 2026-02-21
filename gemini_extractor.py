from google import genai
import os
import re
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_rules_with_gemini(text):

    prompt = f"""
You are an AML compliance expert.

Extract actionable transaction monitoring rules.

Return STRICTLY valid JSON.

IMPORTANT:
- Do NOT add explanations.
- Do NOT add markdown.
- Do NOT wrap JSON in ```json.
- Only return pure JSON array.
- Use dataset columns EXACTLY as written below:

Available Columns:
Timestamp
From Bank
Account
To Bank
Account.1
Amount Received
Receiving Currency
Amount Paid
Payment Currency
Payment Format
Is Laundering

The "condition" must be valid pandas df.eval() expression.


Return ONLY JSON.

Policy Text:
{text[:30000]}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw_text = response.text.strip()

    # -------------------------
    # CLEAN RESPONSE
    # -------------------------

    # Remove markdown if present
    raw_text = re.sub(r"```json", "", raw_text)
    raw_text = re.sub(r"```", "", raw_text)

    # Extract only JSON array
    match = re.search(r"\[.*\]", raw_text, re.DOTALL)

    if match:
        return match.group(0)
    else:
        return "[]"