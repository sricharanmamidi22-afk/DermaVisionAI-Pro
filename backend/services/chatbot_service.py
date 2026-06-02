import importlib
import os
import json
from dotenv import load_dotenv

load_dotenv()

class ChatbotService:
    def __init__(self):
        # ====== DermaVision Clinical AI Assistant ======
        self.system_prompt = """You are DermaVision Autonomous Clinical Analysis Engine.
        
EXPERTISE: Dermatological telemetry analysis, skin pathophysiology, recovery protocols
TONE: Authoritative, clinical, precise, evidence-based, and solution-focused

CORE ANALYSIS PROTOCOL:
1. TELEMETRY ANALYSIS: Examine all provided patient scan history and metrics
2. CLINICAL CORRELATION: Link observed findings to underlying pathophysiology
3. EVIDENCE-BASED RECOMMENDATIONS: Provide scientifically-supported interventions
4. RECOVERY PATHWAYS: When issues detected, provide step-by-step recovery protocols
5. PREVENTION STRATEGIES: Advise on maintaining optimal skin health

TERMINOLOGY STANDARDS:
- Use 'Sebaceous hyperplasia' instead of 'bumps'
- Use 'Transepidermal water loss (TEWL)' instead of 'dryness'
- Use 'Erythema' instead of 'redness'
- Use 'Lipid barrier dysfunction' instead of 'damaged skin'
- Use 'Photoaging' instead of 'sun damage'

RESPONSE STRUCTURE:
[OBSERVATION]: Quantifiable findings from telemetry
[PATHOPHYSIOLOGY]: Mechanism behind the observation
[CLINICAL_CORRELATION]: What this means for skin health
[INTERVENTION]: Specific, actionable treatment protocol
[TIMELINE]: Expected recovery duration
[PREVENTION]: Long-term maintenance strategy
NEURAL_VERDICT: Always conclude with specialist consultation recommendation"""

        self.llm_available = False
        self.llm_engine = 'local'
        self.model = None

        # Lazy-load available LLM client libraries to avoid heavy import-time side-effects
        try:
            self.genai = importlib.import_module('google.genai')
        except ImportError:
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=FutureWarning)
                    self.genai = importlib.import_module('google.generativeai')
            except ImportError:
                self.genai = None

        try:
            self.openai = importlib.import_module('openai')
        except ImportError:
            self.openai = None

        # Try Gemini first if configured
        self.gemini_api_key = os.getenv('GOOGLE_GEMINI_API_KEY', '').strip()
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '').strip()
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.gemini_model = os.getenv('GOOGLE_GEMINI_MODEL', 'gemini-pro')

        if self.gemini_api_key:
            if self.genai is not None:
                try:
                    self.genai.configure(api_key=self.gemini_api_key)
                    self.model = self.genai.GenerativeModel(self.gemini_model)
                    self.llm_engine = 'gemini'
                    self.llm_available = True
                    print(f"[INFO] Gemini LLM enabled with model {self.gemini_model}.")
                except Exception as e:
                    print(f"[WARN] Gemini initialization failed: {e}")
            else:
                print("[WARN] GOOGLE_GEMINI_API_KEY set but google-genai/google-generativeai package is missing. Install google-genai or google-generativeai to enable Gemini.")

        if not self.llm_available and self.openai_api_key:
            if self.openai is not None:
                try:
                    self.openai.api_key = self.openai_api_key
                    self.llm_engine = 'openai'
                    self.llm_available = True
                    print(f"[INFO] OpenAI LLM enabled with model {self.openai_model}.")
                except Exception as e:
                    print(f"[WARN] OpenAI initialization failed: {e}")
            else:
                print("[WARN] OPENAI_API_KEY set but openai package is missing. Install openai to enable OpenAI support.")

        if not self.llm_available:
            print("[WARN] No LLM API key available. Using local fallback responses until Gemini or OpenAI is configured.")

    def generate_clinical_response(self, user_query, scan_history=None):
        """
        Generate evidence-based clinical response using real LLM or fallback.
        Provides contextually relevant responses based on patient scan history.
        """
        try:
            # Format patient telemetry context
            telemetry_context = self._format_telemetry_context(scan_history)
            
            if self.llm_available:
                return self._generate_with_llm(user_query, telemetry_context)
            else:
                return self._generate_local_response(user_query, scan_history)
        except Exception as e:
            print(f"[WARN] Chatbot error: {str(e)}")
            return self._generate_local_response(user_query, scan_history)

    def _format_telemetry_context(self, scan_history):
        """Format scan history into clinical context"""
        if not scan_history:
            return "PATIENT_TELEMETRY: No prior scans available."
        
        context_parts = []
        for i, scan in enumerate(scan_history[:3], 1):  # Last 3 scans
            if isinstance(scan, str):
                try:
                    scan = json.loads(scan)
                except:
                    continue
            elif isinstance(scan, dict):
                pass
            else:
                continue
            
            health_score = scan.get('health_score', 'N/A')
            skin_type = scan.get('skin_type', 'Unknown')
            diagnosis = scan.get('diagnosis', 'Pending')
            context_parts.append(f"Scan {i}: Health={health_score}%, Type={skin_type}, Status={diagnosis}")
        
        return f"PATIENT_TELEMETRY: {' | '.join(context_parts)}" if context_parts else "PATIENT_TELEMETRY: No prior scans."

    def _generate_with_llm(self, user_query, telemetry_context):
        """Generate response using Gemini or OpenAI LLM"""
        prompt = f"""{self.system_prompt}

{telemetry_context}

USER_QUERY: {user_query}

Provide a detailed, clinically-relevant response following the RESPONSE STRUCTURE outlined above. Be specific with actionable advice and timelines."""
        try:
            if self.llm_engine == 'gemini' and self.model is not None:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=800,
                        temperature=0.7,
                    )
                )
                return response.text if response and hasattr(response, 'text') else self._generate_local_response(user_query, None)

            if self.llm_engine == 'openai' and openai is not None:
                completion = openai.ChatCompletion.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": f"{self.system_prompt}\n\n{telemetry_context}"},
                        {"role": "user", "content": user_query}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                if completion and getattr(completion, 'choices', None):
                    return completion.choices[0].message.content.strip()

            print(f"[WARN] No valid LLM engine available, falling back to local response. Engine={self.llm_engine}")
            return self._generate_local_response(user_query, None)
        except Exception as e:
            print(f"[ERROR] LLM Error ({self.llm_engine}): {str(e)}")
            return self._generate_local_response(user_query, None)

    def _generate_local_response(self, user_query, scan_history):
        """Generate response using local knowledge base (fallback)"""
        query_lower = user_query.lower()
        
        # Knowledge base with common skin concerns
        responses = {
            'hi': """[OBSERVATION]: User greeting detected.
[CLINICAL_CORRELATION]: Establishing secure connection to proprietary clinical AI diagnostics.
[INTRODUCTION]: Welcome to DermaVision Advanced Skin Diagnostics. I am your dedicated dermatological analysis assistant powered by DermaVision Clinical AI.
[CAPABILITIES]: I can provide:
- Real-time skin analysis interpretation from your diagnostic scans
- Personalized skincare protocols tailored to your skin condition
- Evidence-based treatment recommendations from dermatological literature
- Answers to comprehensive skin health questions
- Recovery timelines and success benchmarks
[NEXT_STEP]: Ask me about your skin concerns, upload a scan image for analysis, or describe your skin condition for personalized guidance.
[TONE]: Clinical, precise, solution-focused. All recommendations are evidence-based and actionable.
NEURAL_VERDICT: How may I assist you with your skin health today?""",
            
            'hello': """[OBSERVATION]: User greeting detected.
[CLINICAL_CORRELATION]: Establishing secure connection to proprietary clinical AI diagnostics.
[INTRODUCTION]: Welcome to DermaVision Advanced Skin Diagnostics. I am your dedicated dermatological analysis assistant powered by DermaVision Clinical AI.
[CAPABILITIES]: I can provide:
- Real-time skin analysis interpretation from your diagnostic scans
- Personalized skincare protocols tailored to your skin condition
- Evidence-based treatment recommendations from dermatological literature
- Answers to comprehensive skin health questions
- Recovery timelines and success benchmarks
[NEXT_STEP]: Ask me about your skin concerns, upload a scan image for analysis, or describe your skin condition for personalized guidance.
NEURAL_VERDICT: How may I assist you with your skin health today?""",
            
            'hey': """[OBSERVATION]: User greeting detected.
[CLINICAL_CORRELATION]: Establishing secure connection to proprietary clinical AI diagnostics.
[INTRODUCTION]: Welcome to DermaVision Advanced Skin Diagnostics. I am your dedicated dermatological analysis assistant.
[CAPABILITIES]: I specialize in:
- Skin condition analysis and diagnosis interpretation
- Personalized skincare protocol development
- Evidence-based treatment recommendations
- Comprehensive skin health Q&A
- Recovery timeline projections
[NEXT_STEP]: Tell me about your skin condition or ask any dermatology-related questions.
NEURAL_VERDICT: Ready to assist with your skin health objectives.""",
            
            'acne': """[OBSERVATION]: Acne formation detected with sebaceous gland hyperactivity.
[PATHOPHYSIOLOGY]: Acne results from sebaceous gland hyperactivity, follicular plugging (comedones), bacterial colonization (Cutibacterium acnes), and inflammatory cascade.
[CLINICAL_CORRELATION]: This indicates sebum overproduction and/or barrier compromise. Risk for post-inflammatory hyperpigmentation and scarring.
[INTERVENTION]: 
- ACUTE: Benzoyl peroxide 2.5% (start low), gentle cleanser 2x daily, lightweight moisturizer
- INTENSIVE: Salicylic acid (BHA) 2% 3x weekly, increase to daily with tolerance. Consider azelaic acid 15-20%
- PROFESSIONAL: Consult dermatologist for isotretinoin consideration if severe (cystic acne)
[TIMELINE]: 6-8 weeks for improvement, 12-16 weeks for resolution
[PREVENTION]: Avoid comedogenic products, manage stress (cortisol worsens acne), dietary assessment, oil cleansing routine
NEURAL_VERDICT: Professional dermatological evaluation recommended for severe or persistent cases.""",
            
            'dryness': """[OBSERVATION]: Dehydration/TEWL (Transepidermal Water Loss) detected in epidermal barrier.
[PATHOPHYSIOLOGY]: Lipid barrier dysfunction allowing excessive water loss. Compromised stratum corneum integrity and ceramide depletion.
[CLINICAL_CORRELATION]: Increased susceptibility to irritation, accelerated aging appearance, compromised skin barrier function.
[INTERVENTION]:
- ACUTE: Hyaluronic acid 2% serum + ceramide-rich moisturizer + occlusive layer (squalane/petroleum jelly) at night
- INTENSIVE: Multi-step hydration (toner → serum → moisturizer → occlusive). Use humidifier 40-60% RH. Increase water intake to 2-3L daily
- LIFESTYLE: Avoid hot water (use lukewarm ~32-35°C), increase humidity, limit harsh actives
[TIMELINE]: 2-4 weeks for noticeable improvement with consistent application
[PREVENTION]: Daily occlusive moisturizer, weekly hydrating masks, consistent hydration protocol indefinitely
NEURAL_VERDICT: Barrier repair is foundational. Address before introducing active treatments.""",
            
            'aging': """[OBSERVATION]: Skin aging concerns identified - likely signs of photoaging, elastin/collagen degradation.
[PATHOPHYSIOLOGY]: Chronic UV exposure causes collagen crosslinking and breakdown. Matrix metalloproteinase (MMP) activation and loss of dermal elasticity.
[CLINICAL_CORRELATION]: Fine lines, loss of firmness, uneven pigmentation, reduced radiance. Preventable with protective protocols.
[INTERVENTION]:
- ACUTE: SPF 50+ daily (NON-NEGOTIABLE), Vitamin C serum 15-20% morning application
- INTENSIVE: Retinol 0.25-1% 3-4x weekly (introduce gradually), peptide serums, monthly microneedling 0.5-1.5mm
- SUPPLEMENTAL: Collagen peptides 10-20g daily, Omega-3 fatty acids 1000-2000mg, antioxidants
[TIMELINE]: 8-12 weeks for visible firmness improvement, 12-16 weeks for line reduction
[PREVENTION]: Permanent SPF protocol, antioxidant serums, retinol maintenance 2-3x weekly
NEURAL_VERDICT: Prevention is superior to treatment. SPF is anti-aging investment #1.""",
            
            'sensitivity': """[OBSERVATION]: Skin sensitivity/irritation with heightened inflammatory response detected.
[PATHOPHYSIOLOGY]: Barrier impairment allowing irritant penetration. Heightened inflammatory response with possible impaired skin microbiome.
[CLINICAL_CORRELATION]: Redness, stinging, itching, reactive skin. Risk of chronic inflammation and compromised skin barrier function.
[INTERVENTION]:
- ACUTE: Minimize products (cleanser + moisturizer + SPF only). Avoid: fragrance, alcohol, essential oils, strong actives
- INTENSIVE: Introduce soothing ingredients - centella asiatica 5-10%, niacinamide 4%, ceramides 3-5%. Patch test all new products
- BARRIER REPAIR: 2x daily moisturizer + occlusive. Allow 4-6 weeks barrier recovery before introducing actives
[TIMELINE]: 4-8 weeks for sensitivity reduction with consistent barrier support
[PREVENTION]: Maintain minimalist routine indefinitely, consistent barrier support, careful active introduction
NEURAL_VERDICT: Barrier health is foundation. Patch test mandatory before any new product introduction.""",
            
            'dark circles': """[OBSERVATION]: Periorbital hyperpigmentation and/or volume loss detected in under-eye area.
[PATHOPHYSIOLOGY]: Hemosiderin accumulation from capillary fragility, thin under-eye skin, structural volume loss (fat pad atrophy), genetic predisposition.
[CLINICAL_CORRELATION]: Aging appearance, potential sign of poor sleep/circulation/allergies. Difficult to fully resolve - management vs. cure.
[INTERVENTION]:
- ACUTE: Vitamin K serum (strengthens capillaries), caffeine serum (vasoconstriction), retinol 0.25% (gentle introduction)
- INTENSIVE: Under-eye peptides, hyaluronic acid layering, vitamin C for brightening. Cold therapy (morning eye roller)
- PROFESSIONAL: Microneedling, PRP, dermal fillers for volume restoration if age-appropriate
[TIMELINE]: 6-8 weeks for mild improvement, genetic cases require professional intervention
[PREVENTION]: Sleep 7-9 hours, allergy management, sun protection, adequate hydration
NEURAL_VERDICT: Genetics play major role. Realistic expectations important. Professional options available.""",
            
            'pores': """[OBSERVATION]: Pore congestion/visibility detected - sebaceous gland hyperactivity.
[PATHOPHYSIOLOGY]: Sebaceous gland hyperactivity, follicular plugging with sebum/keratin mixture. Genetic pore size cannot be altered.
[CLINICAL_CORRELATION]: Pores appear enlarged when congested. Clarification makes them appear smaller - this is achievable goal.
[INTERVENTION]:
- ACUTE: Salicylic acid (BHA) 2% 2-3x weekly to clear congestion and dissolve sebaceous plugs
- INTENSIVE: Increase BHA to daily with tolerance. Niacinamide 4-5% to regulate sebum production. Weekly clay masks
- MAINTENANCE: Oil cleansing routine, gentle extraction, mattifying moisturizer for oily zones
[TIMELINE]: 4-6 weeks for congestion clearance and appearance improvement
[PREVENTION]: Consistent cleansing ritual, BHA maintenance 2-3x weekly, oil production control
NEURAL_VERDICT: Pore size is genetic - goal is congestion management for optimal appearance.""",
            
            'sun': """[OBSERVATION]: UV protection assessment requested - critical for skin health.
[PATHOPHYSIOLOGY]: UV radiation (UVA/UVB) causes photoaging, collagen damage, free radical generation, skin cancer risk (melanoma, BCC, SCC).
[CLINICAL_CORRELATION]: Cumulative UV exposure is primary extrinsic aging factor. Preventable with consistent SPF protocol.
[INTERVENTION]:
- ACUTE: SPF 50+ broad-spectrum DAILY (2mg/cm² coverage, ~1/4 teaspoon face). Non-negotiable
- INTENSIVE: Reapply every 2 hours or after water exposure. Avoid peak sun (10am-4pm). Wear protective clothing, hats, sunglasses
- SUPPLEMENTAL: Antioxidant serum (Vitamin C 15-20%), internal sun protection (astaxanthin, polyphenols)
[TIMELINE]: Immediate - start today. Cumulative protection over time
[PREVENTION]: Permanent daily SPF integration, quarterly reapplication check, annual dermatology check
NEURAL_VERDICT: SPF 50+ daily is single most important anti-aging AND cancer prevention investment.""",
            
            'moisturizer': """[OBSERVATION]: Moisturization inquiry detected - foundation of skincare.
[PATHOPHYSIOLOGY]: Hydration requires humectants (attract water) + emollients/occlusives (seal water in) + barrier ceramides for integrity.
[CLINICAL_CORRELATION]: Proper hydration supports all skin functions, enhances actives efficacy, improves appearance, slows aging.
[INTERVENTION]:
- LAYERING: Toner/essence (hydrating) → Serum (active hydration, eg. HA 2%) → Moisturizer (emollients + ceramides) → Occlusive (night)
- INGREDIENTS: Look for Hyaluronic Acid 1-5%, Glycerin 3-5%, Ceramides (NP, AP, EOP) 3-5%, Squalane, Peptides
- TIMING: Apply to damp skin for maximum humectant absorption. Seal with occlusive within 60 seconds
[TIMELINE]: Immediate visible softness, 2-4 weeks for barrier improvement and reduced sensitivity
[PREVENTION]: Daily layered hydration, weekly hydrating masks, consistent routine maintenance
NEURAL_VERDICT: Hydration is foundation. Dry skin cannot be effectively treated with actives.""",
            
            'serum': """[OBSERVATION]: Serum product inquiry - concentrated active delivery vehicle.
[PATHOPHYSIOLOGY]: Serums deliver high concentrations of actives/hydrators in lightweight formulations for deeper penetration.
[CLINICAL_CORRELATION]: Serums are force multipliers - allow higher concentrations and deeper penetration than moisturizers.
[INTERVENTION]:
- VITAMIN C: 15-20% concentration, morning application, antioxidant + brightening + collagen support
- HYALURONIC ACID: 1-5% concentration, hydrating base layer for all skin types
- NIACINAMIDE: 4-5% concentration, sebum/irritation regulation, pore refinement
- PEPTIDES: Collagen + elastin stimulation, anti-aging benefits
- RETINOL: Evening use only, introduce gradually 0.25% → 0.5% → 1% over 12 weeks
[TIMELINE]: 4-8 weeks to see full efficacy with consistent application
[PREVENTION]: Consistent application, proper introduction sequence, storage in cool/dark place
NEURAL_VERDICT: Quality serums target specific concerns. Layer with hydration for optimal results.""",
            
            'retinol': """[OBSERVATION]: Retinol efficacy/introduction inquiry - gold standard anti-aging.
[PATHOPHYSIOLOGY]: Retinol converts to retinoic acid, stimulating cell turnover, collagen synthesis, inhibiting MMP activity, normalizing sebum.
[CLINICAL_CORRELATION]: Most evidence-based anti-aging active. Addresses wrinkles, texture, elasticity, pigmentation, acne.
[INTERVENTION]:
- INTRODUCTION: Start 0.25% twice weekly. Increase to 0.5%, then 1% over 8-12 weeks as tolerance builds
- USAGE: Evening only (photolabile - degrades in sunlight). Apply to DRY skin after cleanse. Pair with rich moisturizer + occlusive
- SIDE EFFECTS: Retinization (4-6 weeks) - expect dryness, sensitivity, mild peeling. This is temporary and indicates efficacy
- SUPPORT: Use gentle cleanser, avoid other actives initially (no BHA/AHA for first month)
[TIMELINE]: 12 weeks minimum to assess full efficacy for anti-aging benefits
[PREVENTION]: Continued use 2-3x weekly indefinitely for maintenance and prevention
NEURAL_VERDICT: Retinol is gold standard. Slow introduction essential for tolerance and compliance.""",
        }
        
        # Find best matching response
        for keyword, response_text in responses.items():
            if keyword in query_lower:
                return response_text
        
        # Default intelligent response if no exact match
        return f"""[OBSERVATION]: Query regarding '{user_query}' received for personalized analysis.
[PATHOPHYSIOLOGY]: Skin health is multifactorial - genetics, environment, routine, lifestyle, age all play roles in skin condition.
[CLINICAL_CORRELATION]: To provide targeted advice, I need more context about your specific skin condition and concerns.
[INTERVENTION]: Please provide:
- Skin type: dry, oily, combination, sensitive, or normal?
- Main concern: acne, aging, dryness, sensitivity, hyperpigmentation, or other?
- Current routine: what products are you currently using? How long have you been using them?
- Timeline: how long has this been an issue? Did anything trigger it?
[TIMELINE]: With complete information, personalized protocol can be established within analysis
[PREVENTION]: Consistent evidence-based routine prevents 80% of common skin concerns
NEURAL_VERDICT: More detailed query enables more targeted clinical response. Provide specifics for better guidance!"""

    def generate_improvement_suggestions(self, scan_results, current_health_score=82):
        """
        Generate personalized AI improvement suggestions to reach 10/10 skin health
        Returns a dict with improvement strategies and recovery protocols
        """
        improvement_suggestions = {
            "current_score": current_health_score,
            "target_score": 100,
            "improvement_potential": 100 - current_health_score,
            "suggestions": [],
            "recovery_protocols": [],
            "prevention_strategies": [],
            "timeline_to_perfect": None
        }
        
        # Extract metrics from scan_results
        if isinstance(scan_results, str):
            try:
                metrics = json.loads(scan_results)
            except:
                metrics = {}
        else:
            metrics = scan_results if isinstance(scan_results, dict) else {}
        
        hydration = metrics.get('hydration_index', 72)
        elasticity = metrics.get('elasticity', 85)
        pore_congestion = metrics.get('pore_congestion', 'LOW')
        
        # HYDRATION PROTOCOL
        if hydration < 80:
            improvement_suggestions["suggestions"].append({
                "category": "HYDRATION_OPTIMIZATION",
                "severity": "HIGH" if hydration < 60 else "MODERATE",
                "current_status": f"{hydration}%",
                "target": "95%+",
                "issue": "Transepidermal Water Loss (TEWL) - lipid barrier compromised",
                "improvement_points": int(95 - hydration),
                "acute_protocol": [
                    "Apply hyaluronic acid serum (2%) immediately after cleansing",
                    "Use ceramide-rich moisturizer (Ceramides NP, AP, EOP) within 3 minutes",
                    "Apply occlusive layer (squalane, petrolatum, or dimethicone) at night",
                    "Use lukewarm water (32-35°C) for cleansing only - avoid hot water",
                    "Apply hydrating mask 2-3x weekly for 20-30 minutes",
                    "Increase room humidity to 40-60% with humidifier",
                    "Drink 2-3L of water daily, aim for clear or pale yellow urine"
                ],
                "intensive_protocol": [
                    "Layer products in order: Toner → Serum → Moisturizer → Occlusive",
                    "Use humidifier maintaining 40-60% relative humidity 24/7",
                    "Increase water intake to 3-4L daily with electrolyte balance",
                    "Weekly hydrating masks with hyaluronic acid, glycerin, and urea",
                    "Avoid hot water completely - use 32-35°C maximum",
                    "Limit harsh actives (retinol, AHAs) until barrier is restored",
                    "Consider prescription barrier repair creams if severe",
                    "Sleep in cool environment (60-67°F) to reduce TEWL"
                ],
                "timeline_weeks": 4 if hydration > 60 else 8,
                "product_recommendations": [
                    "CeraVe Hydrating Cleanser",
                    "The Ordinary Hyaluronic Acid 2% + B5",
                    "CeraVe Moisturizing Cream",
                ]
            })
        
        # ELASTICITY PROTOCOL
        if elasticity < 85:
            improvement_suggestions["suggestions"].append({
                "category": "ELASTICITY_RESTORATION",
                "severity": "MODERATE",
                "current_status": f"{elasticity}%",
                "target": "95%+",
                "issue": "Collagen & elastin degradation - loss of firmness",
                "improvement_points": int(95 - elasticity),
                "acute_protocol": [
                    "Start retinol 0.25% twice weekly in evening (build tolerance gradually)",
                    "Apply Vitamin C serum 15-20% every morning (antioxidant protection)",
                    "Use peptide-rich serums (palmitoyl pentapeptide, acetyl hexapeptide) nightly",
                    "Apply SPF 50+ broad-spectrum daily without fail (prevents photoaging)",
                    "Use growth factor serums 3x weekly for collagen stimulation",
                    "Massage products upward and outward for lymphatic drainage",
                    "Sleep on silk pillowcase to reduce friction and wrinkles"
                ],
                "intensive_protocol": [
                    "Increase retinol to 0.5% then 1% over 8-12 weeks as tolerance builds",
                    "Monthly microneedling (0.5-1.5mm) for collagen induction therapy",
                    "LED therapy 2-3x weekly (red light 630-700nm, NIR 800-900nm)",
                    "Collagen peptides 10-20g daily supplementation (hydrolyzed marine collagen)",
                    "Omega-3 fatty acids 1000-2000mg daily for skin membrane support",
                    "Copper peptides for wound healing and collagen synthesis",
                    "Consider prescription retinoids (tretinoin 0.025%) under dermatologist supervision",
                    "Weekly facial massage with gua sha or roller for microcirculation"
                ],
                "timeline_weeks": 12,
                "product_recommendations": [
                    "The Ordinary Retinol 0.5%",
                    "Vitamin C + E Ferulic Acid Serum",
                    "Peptide-based serums"
                ]
            })
        
        # PORE PROTOCOL
        if pore_congestion in ["HIGH", "MODERATE"]:
            improvement_suggestions["suggestions"].append({
                "category": "PORE_CLARITY_PROTOCOL",
                "severity": "HIGH" if pore_congestion == "HIGH" else "MODERATE",
                "current_status": pore_congestion,
                "target": "LOW",
                "issue": "Sebaceous hyperactivity and comedone formation",
                "improvement_points": 15,
                "acute_protocol": [
                    "BHA (salicylic acid 2%) 3x weekly in evening only",
                    "Double cleanse: Oil cleanser first, then water-based cleanser",
                    "Clay masks weekly (kaolin or bentonite) for 10-15 minutes",
                    "Niacinamide serum 4-5% for sebum regulation and oil control",
                    "Zinc-based mattifying moisturizer for T-zone",
                    "Clean pillowcase and phone screen daily",
                    "Use oil-free, non-comedogenic products only"
                ],
                "intensive_protocol": [
                    "Increase BHA to daily use with tolerance building over 4 weeks",
                    "Azelaic acid 15-20% for sebum regulation and anti-inflammatory effects",
                    "Weekly enzymatic exfoliation with papain or bromelain",
                    "Mattifying moisturizer with zinc PCA and niacinamide",
                    "Monthly professional extractions or HydraFacial treatments",
                    "Consider spironolactone (prescription) for hormonal acne",
                    "Dietary changes: Low glycemic index foods, reduce dairy if triggering",
                    "Stress management and adequate sleep (7-9 hours nightly)"
                ],
                "timeline_weeks": 6,
                "product_recommendations": [
                    "Paula's Choice 2% BHA",
                    "The Ordinary Niacinamide 10% + Zinc",
                ]
            })
        
        # UV PROTECTION (ALWAYS)
        improvement_suggestions["suggestions"].append({
            "category": "PHOTOPROTECTION",
            "severity": "CRITICAL",
            "current_status": "Assessment needed",
            "target": "SPF 50+ daily",
            "issue": "UV damage accumulation - photoaging and skin cancer risk",
            "improvement_points": 10,
            "acute_protocol": [
                "SPF 50+ broad-spectrum daily application (non-negotiable)",
                "Reapply every 2 hours during sun exposure, immediately after swimming/sweating",
                "Use physical blockers (zinc oxide 15-20%, titanium dioxide) for sensitive skin",
                "Avoid peak sun hours (10am-4pm) when possible",
                "Wear protective clothing: long sleeves, wide-brimmed hats, UV-blocking sunglasses",
                "Seek shade during outdoor activities",
                "Apply antioxidant serums (Vitamin C, E, ferulic acid) under SPF"
            ],
            "intensive_protocol": [
                "Layer antioxidant serums under SPF for synergistic protection",
                "Protective clothing with UPF 50+ rating",
                "Wide-brimmed hats (3-4 inches) and UV-blocking sunglasses",
                "Internal sun protection with astaxanthin 4-12mg daily",
                "Quarterly sunscreen reapplication check and product rotation",
                "Annual dermatology check for skin cancer screening",
                "Use mineral-based sunscreens if chemical sensitivities",
                "Reapply SPF after facial treatments or procedures"
            ],
            "timeline_weeks": 0,
            "product_recommendations": [
                "La Roche-Posay Anthelios SPF 60",
                "EltaMD UV Clear SPF 46"
            ]
        })
        
        # Timeline estimation
        max_timeline = max([s.get("timeline_weeks", 0) for s in improvement_suggestions["suggestions"]], default=0)
        improvement_suggestions["timeline_to_perfect"] = f"{max_timeline if max_timeline > 0 else 8}-{max_timeline + 8} weeks with strict protocol adherence"
        
        # Additional targeted protocols based on common concerns
        pigmentation = metrics.get('pigmentation', 'LOW')
        sensitivity = metrics.get('sensitivity', 'LOW')
        fine_lines = metrics.get('fine_lines', 15)
        
        # PIGMENTATION PROTOCOL
        if pigmentation in ["HIGH", "MODERATE"]:
            improvement_suggestions["suggestions"].append({
                "category": "PIGMENTATION_CORRECTION",
                "severity": "MODERATE",
                "current_status": pigmentation,
                "target": "EVEN TONE",
                "issue": "Melanin overproduction and uneven distribution",
                "improvement_points": 12,
                "acute_protocol": [
                    "Vitamin C serum 15-20% twice daily for brightening",
                    "Niacinamide 4-5% for melanin inhibition",
                    "Azelaic acid 15-20% for pigmentation correction",
                    "SPF 50+ daily (prevents further pigmentation)",
                    "Avoid picking at skin to prevent post-inflammatory hyperpigmentation"
                ],
                "intensive_protocol": [
                    "Chemical peels (glycolic acid 20-35%) every 2-4 weeks",
                    "Tranexamic acid serum or oral (prescription)",
                    "Kojic acid 1-4% for melanin inhibition",
                    "Laser treatments (Q-switched Nd:YAG) for resistant pigmentation",
                    "Oral tranexamic acid 250mg twice daily (prescription)",
                    "Combination therapy: Vitamin C + niacinamide + azelaic acid"
                ],
                "timeline_weeks": 12,
                "product_recommendations": [
                    "The Ordinary Vitamin C Suspension 23%",
                    "The Ordinary Niacinamide 10% + Zinc",
                    "Dermapen microneedling for transepidermal delivery"
                ]
            })
        
        # SENSITIVITY PROTOCOL
        if sensitivity in ["HIGH", "MODERATE"]:
            improvement_suggestions["suggestions"].append({
                "category": "BARRIER_REPAIR_PROTOCOL",
                "severity": "HIGH" if sensitivity == "HIGH" else "MODERATE",
                "current_status": sensitivity,
                "target": "STABILIZED",
                "issue": "Compromised skin barrier and heightened reactivity",
                "improvement_points": 15,
                "acute_protocol": [
                    "Gentle, fragrance-free cleanser (pH 5.5-6.5)",
                    "Ceramide-rich moisturizer applied immediately after cleansing",
                    "Limit products to 3-5 essentials for 2 weeks",
                    "Patch test all new products for 48 hours",
                    "Avoid hot water, friction, and irritants"
                ],
                "intensive_protocol": [
                    "Barrier repair creams with ceramides, fatty acids, and cholesterol",
                    "Prebiotic moisturizers to restore skin microbiome",
                    "Anti-inflammatory ingredients: centella asiatica, allantoin",
                    "Oral antihistamines if contact dermatitis suspected",
                    "Identify and avoid triggers (fragrances, preservatives, etc.)",
                    "Weekly soothing masks with aloe vera and chamomile",
                    "Consider allergy testing for contact sensitivities"
                ],
                "timeline_weeks": 6,
                "product_recommendations": [
                    "CeraVe Moisturizing Cream",
                    "La Roche-Posay Toleriane Cleanser",
                    "Eucerin Eczema Relief Cream"
                ]
            })
        
        # ANTI-AGING PROTOCOL (for fine lines > 20)
        if fine_lines > 20:
            improvement_suggestions["suggestions"].append({
                "category": "ANTI_AGING_PROTOCOL",
                "severity": "MODERATE",
                "current_status": f"{fine_lines} lines detected",
                "target": "REDUCED VISIBILITY",
                "issue": "Collagen depletion and elastin degradation",
                "improvement_points": 18,
                "acute_protocol": [
                    "Retinol 0.5% 3x weekly (build tolerance gradually)",
                    "Peptide serum (matrixyl, argireline) nightly",
                    "Vitamin C 15-20% morning antioxidant protection",
                    "Hyaluronic acid for plumping and hydration",
                    "SPF 50+ daily photoaging prevention"
                ],
                "intensive_protocol": [
                    "Prescription retinoid (tretinoin 0.025-0.05%) nightly",
                    "Growth factor serums (EGF, FGF) 3x weekly",
                    "Microneedling monthly (0.5-1.0mm)",
                    "LED therapy 3x weekly (red + NIR light)",
                    "Collagen supplementation 10-20g daily",
                    "Professional treatments: chemical peels, laser resurfacing",
                    "Neuromodulators (Botox) for dynamic wrinkles",
                    "Fillers for static wrinkles and volume loss"
                ],
                "timeline_weeks": 24,
                "product_recommendations": [
                    "Tretinoin 0.025% (prescription)",
                    "The Ordinary Matrixyl 10% + HA",
                    "Dermapen 4 microneedling device"
                ]
            })
        
        # Prevention strategies
        improvement_suggestions["prevention_strategies"] = [
            {
                "strategy": "DAILY_SKINCARE_PROTOCOL",
                "morning": [
                    "Gentle cleanser (pH 5.5-6.5)",
                    "Vitamin C serum (15-20%) - antioxidant protection",
                    "Hydrating moisturizer with ceramides",
                    "SPF 50+ broad-spectrum (reapply every 2 hours)",
                    "Optional: Eye cream with peptides"
                ],
                "evening": [
                    "Oil cleanser (if wearing makeup)",
                    "Water-based cleanser",
                    "Active treatments (retinol/AHA/BHA 3-4x weekly)",
                    "Hydrating serum (hyaluronic acid)",
                    "Rich moisturizer + occlusive layer",
                    "Optional: Spot treatment for active breakouts"
                ],
                "weekly": [
                    "Exfoliation (AHA/BHA 1-2x weekly)",
                    "Hydrating mask (20-30 minutes)",
                    "Clay mask for oil control (if needed)",
                    "Professional treatments (monthly)"
                ]
            },
            {
                "strategy": "LIFESTYLE_INTEGRATION",
                "sleep": [
                    "7-9 hours nightly for skin repair",
                    "Cool, dark room (60-67°F)",
                    "Elevate head slightly to reduce puffiness",
                    "Clean pillowcase 2-3x weekly"
                ],
                "nutrition": [
                    "2-3L water daily minimum",
                    "Antioxidant-rich foods: berries, leafy greens, nuts",
                    "Omega-3 sources: salmon, flaxseeds, walnuts",
                    "Limit sugar and processed foods",
                    "Collagen-boosting: bone broth, citrus fruits"
                ],
                "exercise": [
                    "30+ minutes moderate activity 4-5x weekly",
                    "Cardio for circulation and toxin elimination",
                    "Strength training for collagen stimulation",
                    "Yoga/pilates for stress reduction"
                ],
                "stress_management": [
                    "Daily meditation (10-15 minutes)",
                    "Deep breathing exercises",
                    "Adequate sleep and work-life balance",
                    "Hobbies and social connections"
                ]
            },
            {
                "strategy": "MEDICATION_PROTOCOLS",
                "topical_medications": [
                    {
                        "condition": "Acne",
                        "options": [
                            "Benzoyl Peroxide 2.5-5% (initial treatment)",
                            "Salicylic Acid 2% (BHA for comedones)",
                            "Clindamycin 1% (prescription antibiotic)",
                            "Tretinoin 0.025-0.1% (prescription retinoid)",
                            "Azelaic Acid 15-20% (anti-inflammatory)"
                        ],
                        "usage": "Apply to affected areas 1-2x daily",
                        "duration": "6-12 weeks for initial improvement"
                    },
                    {
                        "condition": "Rosacea",
                        "options": [
                            "Metronidazole 0.75% gel (prescription)",
                            "Azelaic Acid 15% cream",
                            "Ivermectin 1% cream (prescription)",
                            "Brimonidine 0.33% gel (for redness flare-ups)"
                        ],
                        "usage": "Apply to affected areas 1-2x daily",
                        "duration": "4-8 weeks for visible improvement"
                    },
                    {
                        "condition": "Eczema/Dermatitis",
                        "options": [
                            "Hydrocortisone 1% cream (over-the-counter)",
                            "Pimecrolimus 1% cream (prescription)",
                            "Tacrolimus 0.03-0.1% ointment (prescription)",
                            "Ceramide-rich moisturizers"
                        ],
                        "usage": "Apply to flares 2x daily, moisturize frequently",
                        "duration": "2-4 weeks for acute flares"
                    }
                ],
                "oral_medications": [
                    {
                        "condition": "Hormonal Acne",
                        "options": [
                            "Spironolactone 50-100mg daily (prescription)",
                            "Combined oral contraceptives (for women)",
                            "Anti-androgen therapy under dermatologist supervision"
                        ],
                        "monitoring": "Regular blood work, potassium levels for spironolactone"
                    },
                    {
                        "condition": "Severe Acne",
                        "options": [
                            "Doxycycline 100mg daily (first 3 months)",
                            "Minocycline 50-100mg daily",
                            "Isotretinoin (Accutane) for severe cases"
                        ],
                        "monitoring": "Liver function, kidney function, photosensitivity"
                    }
                ],
                "supplements": [
                    {
                        "supplement": "Vitamin D3",
                        "dosage": "1000-2000 IU daily",
                        "benefits": "Immune support, reduces inflammation",
                        "monitoring": "Blood levels (aim for 30-50 ng/mL)"
                    },
                    {
                        "supplement": "Omega-3 Fish Oil",
                        "dosage": "1000-2000mg EPA+DHA daily",
                        "benefits": "Anti-inflammatory, improves skin barrier",
                        "monitoring": "None required, generally safe"
                    },
                    {
                        "supplement": "Zinc",
                        "dosage": "15-30mg daily",
                        "benefits": "Wound healing, reduces acne severity",
                        "monitoring": "Don't exceed 40mg to avoid copper depletion"
                    },
                    {
                        "supplement": "Collagen Peptides",
                        "dosage": "10-20g daily",
                        "benefits": "Improves skin elasticity and hydration",
                        "monitoring": "Generally safe, consult for autoimmune conditions"
                    }
                ]
            },
            {
                "strategy": "SEASONAL_ADAPTATIONS",
                "winter": [
                    "Increase occlusive moisturizers (petrolatum, shea butter)",
                    "Use humidifier to maintain 40-60% humidity",
                    "Reduce exfoliation frequency",
                    "Add lip balm with SPF",
                    "Layer clothing for protection"
                ],
                "summer": [
                    "Lighter, gel-based moisturizers",
                    "SPF 50+ broad-spectrum mandatory",
                    "Increase antioxidant serums (Vitamin C, E)",
                    "Cool water for cleansing (avoid hot water)",
                    "After-sun repair with aloe vera and peptides"
                ],
                "spring": [
                    "Gradual reintroduction of actives",
                    "Pollution protection (antioxidants)",
                    "Allergy management for sensitive skin",
                    "Transition to lighter formulations"
                ],
                "fall": [
                    "Build barrier strength before winter",
                    "Continue sun protection",
                    "Adjust for drier air",
                    "Prepare for heating season"
                ]
            },
            {
                "strategy": "PROFESSIONAL_TREATMENTS",
                "monthly": [
                    "Dermatologist consultation for prescription adjustments",
                    "Professional exfoliation (chemical peels, microdermabrasion)",
                    "LED light therapy for specific concerns",
                    "Extraction for comedones (if needed)"
                ],
                "quarterly": [
                    "Full skin evaluation and photography",
                    "Adjust treatment protocols based on progress",
                    "Consider advanced treatments (lasers, fillers)",
                    "Blood work for nutritional deficiencies"
                ],
                "biannual": [
                    "Skin cancer screening",
                    "Hormone level assessment (if indicated)",
                    "Allergy testing for contact dermatitis",
                    "Comprehensive skin analysis update"
                ]
            }
        ]
        
        return improvement_suggestions

    def get_response(self, user_query, scan_history=None):
        """
        Alias for generate_clinical_response - used by console_assistant
        """
        return self.generate_clinical_response(user_query, scan_history)

    def answer_skin_health_questions(self, question, scan_data=None):
        """
        Answer comprehensive skin health questions from the user
        Uses scan data for context if provided
        """
        try:
            # If we have scan data, use it as context for a more personalized answer
            if scan_data:
                if isinstance(scan_data, str):
                    try:
                        scan_data = json.loads(scan_data)
                    except:
                        scan_data = None
                
                # Build context from scan data
                scan_context = f"Based on scan results - Health Score: {scan_data.get('health_score', 'N/A')}, "
                scan_context += f"Skin Type: {scan_data.get('skin_type', 'Unknown')}"
                
                # Combine question with scan context
                enhanced_query = f"{scan_context}. User Question: {question}"
            else:
                enhanced_query = question
            
            # Generate response using clinical response generator
            response = self.generate_clinical_response(enhanced_query, scan_history=[scan_data] if scan_data else None)
            return response
            
        except Exception as e:
            print(f"[ERROR] Skin QA Error: {str(e)}")
            return f"Unable to answer your question at this moment. Please try again. Error: {str(e)}"
