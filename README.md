# 🍳 ป้าศรีเด็กหอ — AI ช่วยคิดเมนู

> ระบบแนะนำเมนูอาหารสำหรับนักศึกษาหอพัก โดยใช้ **Google Gemini AI** วิเคราะห์วัตถุดิบที่มีอยู่ในห้องและแนะนำเมนูที่ทำได้จริง พร้อมขั้นตอนการปรุง

---

## 📋 ภาพรวมระบบ

**ป้าศรีเด็กหอ** คือ Web Application ที่ช่วยให้นักศึกษาหอพักสามารถ:

- 🥕 **กรอกวัตถุดิบ** ที่มีอยู่ในห้อง (เช่น ไข่ไก่, มาม่า, ปลากระป๋อง)
- 🍳 **เลือกอุปกรณ์** ที่มี (หม้อหุงข้าว / ไมโครเวฟ / เตาไฟฟ้า)
- 🤖 **รับคำแนะนำเมนู** จาก AI สูงสุด 3 เมนู พร้อมวัตถุดิบที่ต้องซื้อเพิ่ม, ระดับความยาก, ราคาประมาณ และขั้นตอนการปรุง
- 👍👎 **ให้ Feedback** กับแต่ละเมนูที่แนะนำ

---

## 🏗️ โครงสร้างโปรเจกต์

```
project/
├── app/                        # Backend (FastAPI)
│   ├── main.py                 # จุดเริ่มต้น FastAPI + CORS + Static files
│   ├── routes.py               # API Endpoints ทั้งหมด
│   ├── gemini_client.py        # ติดต่อ Google Gemini AI
│   └── supabase_client.py      # ติดต่อฐานข้อมูล Supabase
├── static/                     # Frontend (HTML/CSS/JS)
│   ├── index.html              # หน้าเว็บหลัก
│   ├── style.css               # สไตล์ UI
│   ├── script.js               # JavaScript Logic
│   └── assets/
│       └── logo.png            # โลโก้แอป
├── tmp/                        # ไฟล์ทดสอบ (ไม่ใช่ Production)
├── .env                        # Environment Variables (ไม่ควร commit ขึ้น Git)
├── requirements.txt            # Python dependencies
└── README.md                   # ไฟล์นี้
```

---

## 🛠️ เทคโนโลยีที่ใช้

| ส่วน          | เทคโนโลยี                                                                      |
| ------------- | ------------------------------------------------------------------------------ |
| **Backend**   | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| **AI Engine** | [Google Gemini 2.5 Flash](https://ai.google.dev/) (`google-genai`)             |
| **Database**  | [Supabase](https://supabase.com/) (PostgreSQL)                                 |
| **Frontend**  | HTML5, CSS3 (Glassmorphism), Vanilla JavaScript                                |
| **Font**      | Outfit + Sarabun (Google Fonts)                                                |

---

## ⚙️ การติดตั้งและรันระบบ (ตั้งแต่ต้น)

### 1. ความต้องการเบื้องต้น

- **Python 3.10+** — [ดาวน์โหลดที่นี่](https://www.python.org/downloads/)
- **บัญชี Supabase** — [สมัครฟรีที่นี่](https://supabase.com/)
- **Google Gemini API Key** — [รับ Key ที่นี่](https://aistudio.google.com/app/apikey)

---

### 2. Clone หรือเตรียมโปรเจกต์

```bash
# ถ้า clone จาก Git
git clone <repository-url>
cd project

# หรือเปิด folder โปรเจกต์ที่มีอยู่แล้ว
cd c:\Users\sirik\Downloads\project\project
```

---

### 3. สร้าง Virtual Environment และติดตั้ง Dependencies

```bash
# สร้าง Virtual Environment
python -m venv venv

# Activate venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate venv (Windows CMD)
.\venv\Scripts\activate.bat

# ติดตั้ง packages
pip install -r requirements.txt
```

> **หมายเหตุ:** ถ้า PowerShell บอก "cannot be loaded because running scripts is disabled" ให้รัน:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

### 4. ตั้งค่า Environment Variables

สร้างไฟล์ `.env` ใน root ของโปรเจกต์:

```env
SUPABASE_URL=https://xxxxxxxxxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GEMINI_API_KEY=AIzaSy...
```

> ⚠️ **อย่า commit ไฟล์ `.env` ขึ้น GitHub** เด็ดขาด! ให้เพิ่มลงใน `.gitignore`

#### วิธีหาค่าต่าง ๆ:

- **SUPABASE_URL** และ **SUPABASE_SERVICE_ROLE_KEY** — ไปที่ Supabase Dashboard → Project Settings → API
- **GEMINI_API_KEY** — ไปที่ [Google AI Studio](https://aistudio.google.com/app/apikey) → Create API Key

---

### 5. ตั้งค่าฐานข้อมูล Supabase

เปิด **SQL Editor** ใน Supabase Dashboard แล้วรัน SQL ต่อไปนี้:

```sql
-- ตาราง menus: เก็บรายชื่อเมนูทั้งหมดในระบบ
CREATE TABLE menus (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  category TEXT,
  ingredients TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ตาราง recommendations: เก็บผลลัพธ์ที่ AI แนะนำแต่ละครั้ง
CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  menu_name TEXT NOT NULL,
  user_ingredients TEXT[],
  missing_ingredients TEXT[],
  difficulty TEXT,
  estimated_cost INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ตาราง feedback: เก็บ feedback ของผู้ใช้ต่อแต่ละคำแนะนำ
CREATE TABLE feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  recommendation_id UUID REFERENCES recommendations(id),
  rating INTEGER CHECK (rating >= 1),
  comment TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### ตัวอย่างข้อมูลเมนูเริ่มต้น (Optional)

```sql
INSERT INTO menus (name, category, ingredients) VALUES
  ('ไข่ดาว', 'อาหารเช้า', ARRAY['ไข่ไก่', 'น้ำมัน', 'เกลือ']),
  ('มาม่าต้ม', 'อาหารหลัก', ARRAY['มาม่า', 'ไข่ไก่', 'น้ำ']),
  ('ข้าวไข่เจียว', 'อาหารหลัก', ARRAY['ไข่ไก่', 'น้ำมัน', 'ข้าวสวย', 'ซีอิ๊ว']),
  ('ปลากระป๋องผัดพริก', 'อาหารหลัก', ARRAY['ปลากระป๋อง', 'พริก', 'กระเทียม', 'น้ำมัน']),
  ('โจ๊กไข่', 'อาหารเช้า', ARRAY['ข้าวสวย', 'ไข่ไก่', 'น้ำ', 'เกลือ']);
```

---

### 6. รัน Server

```bash
# รันด้วย uvicorn (พร้อม auto-reload สำหรับ development)
uvicorn app.main:app --reload

# หรือระบุ port (default: 8000)
uvicorn app.main:app --reload --port 8000
```

เมื่อรันสำเร็จจะขึ้น:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process ...
INFO:     Started server process ...
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### 7. เปิดใช้งาน

เปิด Browser แล้วไปที่:

```
http://localhost:8000
```

---

## 🔌 API Endpoints

Base URL: `http://localhost:8000/api`

| Method  | Endpoint           | คำอธิบาย                                  |
| ------- | ------------------ | ----------------------------------------- |
| `GET`   | `/api/menus`       | ดึงรายการเมนูทั้งหมดจากฐานข้อมูล          |
| `POST`  | `/api/recommend`   | ส่งวัตถุดิบเพื่อรับคำแนะนำเมนูจาก AI      |
| `POST`  | `/api/feedback`    | ส่ง feedback (rating) สำหรับเมนูที่แนะนำ  |
| `PATCH` | `/api/select-menu` | บันทึกว่าผู้ใช้เลือกเมนูนั้น (rating = 1) |

### ตัวอย่าง Request / Response

#### POST `/api/recommend`

```json
// Request Body
{
  "ingredients": "ไข่ไก่, มาม่า, ปลากระป๋อง",
  "equipment": "rice_cooker"
}

// Response
{
  "recommendations": [
    {
      "menu_name": "มาม่าต้มไข่",
      "missing_ingredients": [],
      "difficulty": "ง่าย",
      "estimated_cost": 15,
      "reason": "ใช้ของที่มีครบ ทำได้ในหม้อหุงข้าว",
      "steps": ["ต้มน้ำในหม้อหุงข้าว", "ใส่มาม่าและเครื่องปรุง", "ตอกไข่ลงไป"],
      "recommendation_id": "uuid-xxx"
    }
  ]
}
```

#### POST `/api/feedback`

```json
// Request Body
{
  "recommendation_id": "uuid-xxx",
  "rating": 1,
  "comment": "อร่อยมาก!"
}
```

---

## 🎨 วิธีใช้งานผ่าน UI

1. **กรอกวัตถุดิบ** ที่มีในห้อง คั่นด้วยคอมม่า เช่น `ไข่ไก่, มาม่า, ปลากระป๋อง`
2. **เลือกอุปกรณ์** ที่มี จาก dropdown
3. กด **"ถามป้าศรีเลย"** รอสักครู่ขณะ AI ประมวลผล
4. ดู **เมนูที่แนะนำ** (สูงสุด 3 เมนู) แต่ละการ์ดจะแสดง:
   - ชื่อเมนู
   - วัตถุดิบที่ต้องซื้อเพิ่ม
   - ระดับความยาก และราคาประมาณ
   - เหตุผลที่แนะนำ
5. กด **"ดูวิธีทำ"** เพื่อเปิด Modal แสดงขั้นตอนการปรุง
6. กด **👍 เลือกเมนูนี้** หรือ **👎 ไม่เหมาะ** เพื่อให้ Feedback

---

## 🗄️ โครงสร้างฐานข้อมูล

```
menus
├── id (UUID, PK)
├── name (TEXT)
├── category (TEXT)
├── ingredients (TEXT[])
└── created_at (TIMESTAMPTZ)

recommendations
├── id (UUID, PK)
├── menu_name (TEXT)
├── user_ingredients (TEXT[])
├── missing_ingredients (TEXT[])
├── difficulty (TEXT)
├── estimated_cost (INTEGER)
└── created_at (TIMESTAMPTZ)

feedback
├── id (UUID, PK)
├── recommendation_id (UUID, FK → recommendations.id)
├── rating (INTEGER, >= 1)
├── comment (TEXT)
└── created_at (TIMESTAMPTZ)
```

---

## 🤖 วิธีการทำงานของ AI

1. Frontend ส่งวัตถุดิบและอุปกรณ์มาที่ Backend
2. Backend ดึงเมนูทั้งหมดจาก Supabase
3. ส่ง prompt ไปให้ **Google Gemini 2.5 Flash** พร้อมบทบาทเป็น "ป้าศรีเด็กหอ"
4. Gemini ตอบกลับเป็น JSON รูปแบบที่กำหนด (menu_name, missing_ingredients, difficulty, estimated_cost, reason, steps)
5. Backend บันทึกแต่ละคำแนะนำลง Supabase แล้วส่ง response กลับ Frontend

---

## 🔧 Troubleshooting

### `ModuleNotFoundError`

```bash
# ตรวจสอบว่า activate venv แล้วหรือยัง
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### `ValueError: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set`

- ตรวจสอบว่ามีไฟล์ `.env` และกรอกค่าถูกต้อง
- ค่าต้องไม่มีช่องว่างหรือ quote รอบ ๆ

### AI ไม่ตอบสนอง / Error 500

- ตรวจสอบ **GEMINI_API_KEY** ว่าถูกต้องและยังไม่หมดโควต้า
- ดู log ใน terminal ที่รัน uvicorn

### ฐานข้อมูลว่าง (No menus found)

- ตรวจสอบว่าสร้างตาราง `menus` ใน Supabase แล้ว
- เพิ่มข้อมูลเมนูด้วย SQL INSERT ตามตัวอย่างด้านบน

---

## 📁 ไฟล์ที่ควรเพิ่มใน `.gitignore`

```gitignore
# Environment variables (ข้อมูลลับ)
.env

# Virtual environment
venv/

# Python cache
__pycache__/
*.pyc

# ไฟล์ทดสอบชั่วคราว
tmp/
```

---

## 📝 License

โปรเจกต์นี้สร้างขึ้นเพื่อการศึกษา ใช้งานได้อย่างอิสระ

---

_สร้างด้วย ❤️ สำหรับนักศึกษาหอพักทุกคน — ขอให้อิ่มท้องทุกมื้อนะจ๊ะ 🍜_
