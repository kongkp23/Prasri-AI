import os
import re
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Global client for reuse
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Use sync function for stability as requested by new SDK patterns
def _get_menu_recommendations_sync(ingredients, matching_menus):
    prompt = f"""
    คุณคือ "ป้าศรีเด็กหอ" ผู้เชี่ยวชาญการทำอาหารในหอพัก
    วัตถุดิบที่มี: {', '.join(ingredients)}
    เมนูที่น่าจะทำได้จากฐานข้อมูล: {matching_menus}

    ช่วยแนะนำเมนูอาหาร 3 อย่างที่เหมาะสมที่สุด
    โดยใช้หลักการ:
    1. ใช้ของที่มีให้คุ้มค่าที่สุด
    2. ทำง่ายในหอพัก (อาจมีแค่หม้อหุงข้าว หรือเตาไฟฟ้า)
    3. ถ้าขาดวัตถุดิบอะไร ให้บอกมาชัดเจน

    Return ONLY valid JSON in this format:
    [
      {{
        "menu_name": "ชื่อเมนู",
        "missing_ingredients": ["สิ่งที่ต้องซื้อเพิ่ม"],
        "difficulty": "ง่าย/ปานกลาง/ยาก",
        "reason": "เหตุผลที่แนะนำ",
        "steps": [
          "ขั้นตอนที่ 1: ...",
          "ขั้นตอนที่ 2: ...",
          "ขั้นตอนที่ 3: ..."
        ]
      }}
    ]
    """
    
    try:
        # We've tested that gemini-2.5-flash is the available model for this key/library combo
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        
        if not response or not response.text:
            return "[]"
            
        text = response.text.strip()
        
        # Clean extra text using regex to extract only the JSON array
        json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
            
        return text
    except Exception as e:
        print(f"AI Gemini Error: {e}")
        raise e

async def get_menu_recommendations(ingredients, matching_menus):
    """
    Expert "Pa Sri Dek Hor" recommend menus.
    Using the new google-genai SDK.
    """
    # Run sync call in a thread to keep the server responsive
    return await asyncio.to_thread(_get_menu_recommendations_sync, ingredients, matching_menus)
