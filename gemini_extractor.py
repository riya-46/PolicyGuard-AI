import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

# -------------------------
# Configure Gemini API
# -------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found.")

# -------------------------
# Main Extraction Function
# -------------------------
def extract_rules_with_gemini(text):

    model = genai.GenerativeModel("gemini-1.5-flash")

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

    try:
        response = model.generate_content(prompt)

        raw_text = response.text.strip()

        # -------------------------
        # CLEAN RESPONSE
        # -------------------------

        # Remove markdown wrappers
        raw_text = re.sub(r"```json", "", raw_text)
        raw_text = re.sub(r"```", "", raw_text)

        # Extract JSON array safely
        match = re.search(r"\[.*\]", raw_text, re.DOTALL)

        if match:
            json_text = match.group(0)

            # Validate JSON before returning
            try:
                json.loads(json_text)
                return json_text
            except json.JSONDecodeError:
                print("Invalid JSON returned from Gemini.")
                return "[]"
        else:
            print("No JSON array found in Gemini response.")
            return "[]"

    except Exception as e:
        print("Gemini API Error:", str(e))
        return "[]"