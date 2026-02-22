import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

def extract_rules_with_gemini(text):

    prompt = f"""
You are an AML compliance expert.

Extract actionable transaction monitoring rules.

Return STRICTLY valid JSON array.

IMPORTANT:
- No explanation
- No markdown
- No ```json
- Only raw JSON list
- Condition must be valid pandas df.eval() syntax

Columns:
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

Policy Text:
{text[:25000]}
"""

    try:
        response = model.generate_content(prompt)

        raw_text = response.text.strip()

        # Remove markdown if any
        raw_text = re.sub(r"```json", "", raw_text)
        raw_text = re.sub(r"```", "", raw_text)

        match = re.search(r"\[.*\]", raw_text, re.DOTALL)

        if match:
            json_text = match.group(0)

            # Validate JSON
            json.loads(json_text)

            return json_text

        return "[]"

    except Exception as e:
        print("Gemini Error:", e)
        return "[]"