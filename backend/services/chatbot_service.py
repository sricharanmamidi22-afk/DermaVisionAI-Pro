import os
from datetime import datetime

# Try to import Google Gemini API (use newer google.genai if available, fallback to deprecated one)
try:
    try:
        import google.genai as genai
        GENAI_VERSION = "new"
        GEMINI_AVAILABLE = True
    except ImportError:
        import google.generativeai as genai
        GENAI_VERSION = "legacy"
        GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARN] google-generativeai not installed. Install it with: pip install google-generativeai")


class ChatbotService:
    def __init__(self):
        self.gemini_available = False
        self.api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                if GENAI_VERSION == "new":
                    genai.configure(api_key=self.api_key)
                else:
                    genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.gemini_available = True
                print("[OK] CHATBOT_SERVICE: Google Gemini API initialized")
            except Exception as e:
                print(f"[WARN] CHATBOT_SERVICE: Gemini initialization failed: {e}")
                print("[FALLBACK] CHATBOT_SERVICE: Using local knowledge base")
        else:
            if not GEMINI_AVAILABLE:
                print("[WARN] CHATBOT_SERVICE: google-generativeai not available")
            if not self.api_key:
                print("[WARN] CHATBOT_SERVICE: GOOGLE_GEMINI_API_KEY not set in environment")
            print("[FALLBACK] CHATBOT_SERVICE: Using local knowledge base")

    def generate_clinical_response(self, user_message, scan_context=None):
        """
        Generate clinical response to user queries, optionally contextualized with scan data.
        Falls back to local knowledge base if Gemini API is unavailable.
        """
        try:
            if self.gemini_available:
                # Build context-aware prompt
                context_str = ""
                if scan_context:
                    context_str = self._format_scan_context(scan_context)
                
                prompt = f"""You are a dermatology expert AI assistant for DermaVision.
                
{context_str}

User Query: {user_message}

Provide a professional, helpful response using proper dermatological terminology.
Format your response with:
[OBSERVATION] - What you observe about their skin concern
[PATHOPHYSIOLOGY] - The underlying mechanism
[CLINICAL_CORRELATION] - How it relates to their scan data
[INTERVENTION] - Recommended treatments or next steps
[TIMELINE] - Expected timeframe for improvement
[PREVENTION] - How to prevent recurrence
NEURAL_VERDICT - Your final clinical assessment"""
                
                response = self.model.generate_content(prompt)
                return response.text if response else self._get_fallback_response(user_message)
            else:
                return self._get_fallback_response(user_message)
        except Exception as e:
            print(f"[ERROR] CHATBOT_SERVICE: Response generation failed: {e}")
            return self._get_fallback_response(user_message)

    def generate_improvement_suggestions(self, skin_concerns, scan_data=None):
        """
        Generate comprehensive improvement suggestions based on identified skin concerns.
        Returns structured recommendations for daily routines, medications, and professional treatments.
        """
        try:
            if self.gemini_available:
                context_str = ""
                if scan_data:
                    context_str = self._format_scan_context(scan_data)
                
                prompt = f"""You are a dermatology expert creating a personalized skincare improvement plan.

{context_str}

Skin Concerns: {skin_concerns}

Create a comprehensive improvement plan including:

1. IMMEDIATE ACTIONS (Week 1-2)
2. DAILY ROUTINE
   - Morning: 5 steps with specific products
   - Evening: 6 steps with specific products
   - Weekly: Exfoliation and treatments

3. TARGETED TREATMENTS
   - Topical medications and their usage
   - Oral supplements with dosages
   - Professional treatments (monthly, quarterly)

4. LIFESTYLE MODIFICATIONS
   - Sleep, nutrition, exercise recommendations
   - Stress management techniques
   - Seasonal adaptations

5. PREVENTION STRATEGY
   - Long-term maintenance routine
   - Trigger avoidance
   - Regular monitoring

6. TIMELINE & EXPECTATIONS
   - 4-week expectations
   - 12-week goals
   - 6-month transformations

Format each section clearly with specific, actionable steps."""
                
                response = self.model.generate_content(prompt)
                return response.text if response else self._get_fallback_suggestions(skin_concerns)
            else:
                return self._get_fallback_suggestions(skin_concerns)
        except Exception as e:
            print(f"[ERROR] CHATBOT_SERVICE: Suggestion generation failed: {e}")
            return self._get_fallback_suggestions(skin_concerns)

    def _format_scan_context(self, scan_data):
        """Format scan data into readable context for the AI."""
        if not scan_data:
            return ""
        
        context_lines = ["RECENT SCAN DATA:"]
        
        # Add various metrics if available
        if isinstance(scan_data, dict):
            metrics = {
                'skin_type': 'Skin Type',
                'health_score': 'Overall Health Score',
                'hydration': 'Hydration Level',
                'oiliness': 'Oiliness Level',
                'acne': 'Acne Score',
                'hyperpigmentation': 'Hyperpigmentation Score',
                'dark_circles': 'Dark Circles Score',
                'wrinkles': 'Wrinkles Score',
                'fine_lines': 'Fine Lines Score',
                'dryness': 'Dryness Level',
                'brightness': 'Brightness Level',
                'large_pores': 'Pore Size Score',
            }
            
            for key, label in metrics.items():
                if key in scan_data:
                    value = scan_data[key]
                    context_lines.append(f"- {label}: {value}")
        
        return "\n".join(context_lines)

    def _get_fallback_response(self, user_message):
        """Fallback response using local knowledge base."""
        message_lower = user_message.lower()
        
        # Simple keyword-based responses
        responses = {
            'acne': """[OBSERVATION] You're inquiring about acne management.
[PATHOPHYSIOLOGY] Acne results from excess sebum production, bacterial colonization, and follicular obstruction.
[CLINICAL_CORRELATION] Your skin analysis shows elevated oiliness and acne markers.
[INTERVENTION] 
- Use a gentle BHA cleanser (salicylic acid)
- Apply benzoyl peroxide (2.5%) to affected areas
- Consider niacinamide serum to regulate sebum
[TIMELINE] Expect improvement within 4-6 weeks.
[PREVENTION] Maintain consistent skincare routine and avoid heavy makeup.
NEURAL_VERDICT: Acne is treatable with proper skincare and targeted treatments.""",
            
            'dry': """[OBSERVATION] Your skin appears to have dryness concerns.
[PATHOPHYSIOLOGY] Dry skin results from impaired barrier function and reduced natural moisturization.
[CLINICAL_CORRELATION] Elevated dryness markers detected in your scan.
[INTERVENTION]
- Use a hydrating cleanser without sulfates
- Apply hydrating toner with glycerin
- Use ceramide-rich moisturizer
- Consider weekly hydration masks
[TIMELINE] Skin barrier recovery takes 2-4 weeks.
[PREVENTION] Avoid hot water, use humidifier, maintain consistent moisturizing routine.
NEURAL_VERDICT: Dryness is manageable with barrier-supporting products.""",
            
            'aging': """[OBSERVATION] You're interested in anti-aging skincare.
[PATHOPHYSIOLOGY] Aging involves collagen breakdown, telomere shortening, and accumulation of oxidative stress.
[CLINICAL_CORRELATION] Fine lines and wrinkle markers detected in analysis.
[INTERVENTION]
- Start with retinol 0.25% gradually increasing strength
- Use Vitamin C serum in morning routine
- Apply peptide-based moisturizers
- Consider professional treatments: microneedling, LED therapy
[TIMELINE] Visible results appear at 12 weeks with consistent use.
[PREVENTION] Daily SPF 50+, antioxidant-rich diet, adequate sleep.
NEURAL_VERDICT: Anti-aging requires multi-modal approach combining topicals, lifestyle, and professional treatments.""",
            
            'sensitivity': """[OBSERVATION] Your skin shows sensitivity concerns.
[PATHOPHYSIOLOGY] Sensitive skin has compromised barrier function and heightened reactivity.
[CLINICAL_CORRELATION] Elevated sensitivity markers detected.
[INTERVENTION]
- Use gentle, fragrance-free cleansers
- Minimize product count to essentials
- Apply hydrating serums and barrier repair creams
- Avoid known irritants (vitamin C, acids, essential oils initially)
[TIMELINE] Barrier restoration takes 4-6 weeks.
[PREVENTION] Patch test new products, use lukewarm water, avoid physical exfoliation.
NEURAL_VERDICT: Sensitivity management requires a minimalist, barrier-focused approach.""",
        }
        
        # Check for keyword matches
        for keyword, response in responses.items():
            if keyword in message_lower:
                return response
        
        # Default response
        return """[OBSERVATION] Thank you for your inquiry about skincare.
[PATHOPHYSIOLOGY] Personalized recommendations depend on individual skin characteristics.
[CLINICAL_CORRELATION] Your skin analysis provides baseline data for targeted treatment.
[INTERVENTION] 
- Complete a full skin scan for comprehensive analysis
- Review your scan results in detail
- Consult dermatologist for persistent concerns
[TIMELINE] Results vary by individual and treatment chosen.
[PREVENTION] Consistent skincare and lifestyle habits support long-term skin health.
NEURAL_VERDICT: A data-driven approach using your scan results ensures optimal outcomes."""

    def _get_fallback_suggestions(self, skin_concerns):
        """Fallback suggestions using local knowledge base."""
        return f"""PERSONALIZED IMPROVEMENT PLAN FOR: {skin_concerns}

IMMEDIATE ACTIONS (Week 1-2):
1. Complete full skin assessment with DermaVision
2. Establish basic 3-step routine: Cleanse, Treat, Moisturize
3. Start with gentle, hydrating products to support barrier

DAILY ROUTINE:
Morning (5 steps):
- Gentle cleanser (lukewarm water, no scrubbing)
- Hydrating toner
- Vitamin C serum (optional)
- Moisturizer with ceramides
- SPF 50 sunscreen

Evening (6 steps):
- Oil cleanser (if makeup worn)
- Water-based cleanser
- Toner
- Targeted treatment (retinol, BHA, or hydrating serum)
- Eye cream
- Moisturizer

Weekly (1-2x):
- Gentle exfoliation (physical or chemical)
- Hydrating sheet mask
- Optional: Clay mask for oily zones

TARGETED TREATMENTS:
Topical: Start with single active ingredient, increase frequency gradually
Supplements: Vitamin D3 2000IU daily, Omega-3 1000mg daily, Zinc 15mg daily
Professional: Monthly facials, quarterly dermatologist check-ups

LIFESTYLE MODIFICATIONS:
- Sleep: 7-9 hours nightly in cool, dark environment
- Nutrition: Increase antioxidant-rich foods, hydrate (8 glasses water daily)
- Exercise: 30 minutes moderate activity 4-5x weekly
- Stress: Daily meditation, adequate work-life balance

TIMELINE & EXPECTATIONS:
Week 4: Skin texture improvement, reduced irritation
Week 12: Visible tone and clarity improvements
Week 24: Significant transformations in elasticity and radiance

NEURAL_VERDICT: Consistent application of personalized recommendations yields optimal skin health outcomes."""
