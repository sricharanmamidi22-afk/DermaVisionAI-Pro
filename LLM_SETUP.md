# DermaVision AI Agent Setup Guide

## Recent Updates

### 1. **Ledger System Connected ✅**
- New **Scan** database model added for tracking all skin analysis records
- **Ledger page** (`/ledger`) displays all user scans in a cyberpunk-styled table
- Each scan shows: UUID, timestamp, thumbnail, confidence score, diagnosis, and action links
- All scans are automatically saved when users perform skin analysis

### 2. **AI Agent Upgraded to Real LLM ✅**
The chatbot now uses **Google Gemini API** for intelligent, context-aware responses instead of mocked replies.

#### Features:
- **Contextual Analysis**: AI considers recent scan history when responding to queries
- **Clinical Terminology**: Responses use proper dermatological language (TEWL, erythema, etc.)
- **Structured Advice**: Follows [OBSERVATION] → [PATHOPHYSIOLOGY] → [INTERVENTION] format
- **Real-time Personalization**: Responses tailored to individual user's scan data
- **Fallback Support**: If API unavailable, uses local knowledge base with 10+ pre-trained responses

---

## Setup Instructions

### Step 1: Get Your Free Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account (create one if needed)
3. Click **"Create API Key"**
4. Copy the generated API key

### Step 2: Add API Key to Your Environment

#### Option A: Create `.env` file (Recommended for Local Development)
```bash
# In the root directory (d:\MY\sri\DermaVisionAI\)
# Create a file named: .env

GOOGLE_GEMINI_API_KEY=your_api_key_here_paste_it
FLASK_ENV=development
FLASK_DEBUG=True
```

#### Option B: Export as Environment Variable (Windows PowerShell)
```powershell
$env:GOOGLE_GEMINI_API_KEY = "your_api_key_here"
```

#### Option C: Production Deployment
Set environment variables in your hosting platform (Heroku, Docker, AWS, etc.)

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

New packages added:
- `google-generativeai>=0.3.0` - Google Gemini API client
- `python-dotenv>=1.0.0` - Environment variable management

### Step 4: Run the Application

```bash
python -m backend.app
```

Visit: `http://localhost:5000`

---

## How It Works

### AI Agent Flow:

```
User Query
    ↓
ChatbotService.generate_clinical_response()
    ↓
┌─────────────────────┐
│ API Key Available?  │
└─────────────────────┘
    ↙           ↘
  YES           NO
   ↓            ↓
Google Gemini  Local KB
(Real LLM)     (10+ Responses)
   ↓            ↓
   └────┬───────┘
        ↓
   Formatted Response
   [OBSERVATION]
   [PATHOPHYSIOLOGY]
   [CLINICAL_CORRELATION]
   [INTERVENTION]
   [TIMELINE]
   [PREVENTION]
   NEURAL_VERDICT
```

### Ledger System:

```
User Uploads Skin Photo
    ↓
/api/analyze endpoint
    ↓
Face Detection + Skin Analysis
    ↓
Save to Scan Table
┌──────────────────────┐
│ scan_id (UUID)       │
│ user_id (FK)         │
│ image_path           │
│ results (JSON)       │
│ confidence (%)       │
│ diagnosis (status)   │
│ timestamp            │
└──────────────────────┘
    ↓
/ledger displays all Scans
```

---

## Database Changes

### New Model: `Scan`
```python
class Scan(db.Model):
    id: int (primary key)
    scan_id: str (unique UUID)
    user_id: int (foreign key → users)
    image_path: str (filename)
    results: str (JSON string)
    confidence: float (0-100)
    diagnosis: str (analysis result)
    timestamp: datetime (creation time)
```

### Backward Compatibility:
- `Analysis` table still exists for legacy compatibility
- New scans save to **both** `Scan` and `Analysis` tables

---

## Example Queries the AI Handles

The AI agent can now respond to queries like:

✅ "How do I treat my acne?"
✅ "What's causing my dark circles?"
✅ "How often should I exfoliate?"
✅ "Best ingredients for sensitive skin?"
✅ "How to improve my skin health score?"
✅ "What's the best morning skincare routine?"
✅ "How to fix dehydration?"
✅ "Should I use retinol?"
✅ "How to prevent photoaging?"
✅ And many more...

With Google Gemini API enabled, the AI will:
1. Read your recent scan history
2. Provide personalized recommendations
3. Reference your specific health metrics
4. Suggest protocols tailored to YOUR skin

---

## Troubleshooting

### "⚠️ GOOGLE_GEMINI_API_KEY not set"
- Check if `.env` file exists in root directory
- Ensure API key is correct (no extra spaces)
- Restart the Flask app after adding `.env`

### AI Responses are Generic/Slow
- Verify API key is active: https://aistudio.google.com/app/apikey
- Check internet connection
- Gemini API has rate limits (free tier is generous)

### Ledger Page is Empty
- Ensure you're logged in
- Create at least one scan via Spectral_Scan page
- Check database: should have entries in `scans` table

### Database Issues
Delete old database and let Flask recreate:
```bash
del backend\database\dermavision.db
python -m backend.app
```

---

## Features

### ✅ Ledger System
- [x] Scan model in database
- [x] Save all analyses to ledger
- [x] Display ledger page with cyberpunk UI
- [x] Show confidence scores and diagnoses
- [x] Link scans to detailed reports

### ✅ AI Agent Improvement
- [x] Google Gemini API integration
- [x] Contextual scan history consideration
- [x] Clinical terminology and proper formatting
- [x] Local fallback for offline mode
- [x] Structured response format
- [x] Real LLM responses instead of mocking

### 🚀 Future Enhancements
- [ ] Multi-language support (French, Spanish, Chinese)
- [ ] Advanced skin condition classification
- [ ] Treatment recommendation with product links
- [ ] Progress tracking over multiple scans
- [ ] Video tutorials for routines
- [ ] Integration with dermatology appointment booking

---

## API Reference

### New Endpoints

#### GET `/ledger`
Display all scans for current user (requires login)

**Response:**
```html
Renders ledger.html with logs array:
{
    "logs": [
        {
            "scan_id": "abc12345",
            "timestamp": "2026-05-10 14:30:00",
            "image_url": "/static/uploads/scan_xyz.jpg",
            "confidence": 87,
            "result": "Normal with mild dehydration",
            "status_class": "status-normal"
        }
    ]
}
```

#### POST `/api/chat`
Send message to AI agent

**Request:**
```json
{
    "message": "How do I treat acne?"
}
```

**Response:**
```json
{
    "status": "SUCCESS",
    "response": "[OBSERVATION]: ... [PATHOPHYSIOLOGY]: ... [INTERVENTION]: ..."
}
```

---

## File Structure

```
backend/
├── database/
│   ├── models.py  ← Updated with Scan model
│   └── dermavision.db
├── services/
│   └── chatbot_service.py  ← Upgraded to use Google Gemini
├── routes/
│   ├── api_routes.py  ← Updated to save Scan records
│   └── web_routes.py  ← Added /ledger route
└── app.py

frontend/
├── templates/
│   ├── base.html  ← Updated ledger link
│   └── ledger.html  ← Ledger page
└── frontend/
    └── static/
        ├── models/    ← Face detection model assets
        └── uploads/   ← Scan images

.env.example  ← API key template
requirements.txt  ← Updated with new packages
```

---

## Performance Notes

- **Gemini API Response Time**: 1-3 seconds typically
- **Ledger Load Time**: <500ms (depends on scan count)
- **Database Queries**: Optimized with limit() and order_by()
- **Concurrent Users**: Supports multi-user safely

---

## Support

For issues or questions:
1. Check `.env` file configuration
2. Verify API key at: https://aistudio.google.com/app/apikey
3. Review Flask debug output for error messages
4. Ensure database is initialized: `python -m backend.app`

---

**Last Updated**: May 10, 2026
**Version**: DermaVision v2.1 (PROTOCOL_NERVA_INIT)
