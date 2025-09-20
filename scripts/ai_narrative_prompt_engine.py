#!/usr/bin/env python3
"""
AI Narrative Prompt Engineering Engine
Generates human-like trauma narratives using sophisticated prompt engineering
"""

import random
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class NarrativeContext:
    """Context structure for narrative generation"""
    domain: str
    company: str
    risk_tier: str
    demographics: Dict[str, Any]
    question_type: str
    company_culture: Dict[str, Any]

class AITraumaNarrativeEngine:
    """
    Advanced prompt engineering system for generating human-like trauma narratives
    Uses sophisticated prompting techniques to create authentic psychological responses
    """

    def __init__(self):
        self.prompt_templates = self._initialize_prompt_templates()
        self.psychological_frameworks = self._initialize_psychological_frameworks()
        self.human_expression_patterns = self._initialize_expression_patterns()
        self.trauma_progression_models = self._initialize_trauma_models()

    def _initialize_prompt_templates(self) -> Dict:
        """Initialize sophisticated prompt engineering templates"""
        return {
            "q23_change_prompts": {
                "healthcare_crisis": [
                    """Generate a first-person narrative from a healthcare worker at {company} experiencing severe workplace trauma.

                    Context: {context}
                    Question: "What one thing would you change about your workplace?"

                    Guidelines:
                    - Write as someone who has experienced patient deaths, medical errors, or pandemic trauma
                    - Use authentic healthcare terminology and specific medical situations
                    - Include emotional rawness typical of trauma survivors
                    - Reference {company}'s specific culture: {culture_phrase}
                    - Show progression from initial incident to current desperation
                    - Length: 300-500 characters
                    - Tone: Desperate, exhausted, seeking systemic change

                    Write a raw, honest response that captures the voice of someone at their breaking point:""",

                    """You are a healthcare professional at {company} who has been psychologically damaged by workplace trauma.

                    Personal details: {demographics}
                    Workplace culture: {culture_phrase}
                    Trauma type: {trauma_type}

                    Question: "What one thing would you change about your workplace?"

                    Respond as someone who:
                    - Has witnessed preventable deaths due to systemic failures
                    - Feels abandoned by hospital administration
                    - Uses specific medical terminology naturally
                    - Shows signs of PTSD, burnout, or depression
                    - Desperately wants systemic change, not just individual support

                    Your response should feel like it was written at 2 AM after a particularly traumatic shift:"""
                ],

                "university_crisis": [
                    """Generate a first-person narrative from an academic at {company} experiencing severe institutional trauma.

                    Context: {context}
                    Question: "What one thing would you change about your workplace?"

                    Guidelines:
                    - Write as someone experiencing academic harassment, discrimination, or abuse
                    - Use academic terminology and reference specific university systems
                    - Include the powerlessness felt in academic hierarchies
                    - Reference {company}'s specific culture: {culture_phrase}
                    - Show how academic trauma differs from other workplace trauma
                    - Length: 300-500 characters
                    - Tone: Intellectualized pain, systemic critique, loss of passion

                    Write from the perspective of someone whose academic dreams have been crushed:""",

                    """You are an academic at {company} whose mental health has been destroyed by institutional trauma.

                    Personal context: {demographics}
                    Academic culture: {culture_phrase}
                    Trauma source: {trauma_type}

                    Question: "What one thing would you change about your workplace?"

                    Respond as someone who:
                    - Has experienced advisor abuse, sexual harassment, or systematic discrimination
                    - Understands how academic systems protect perpetrators
                    - Uses academic language but shows emotional rawness
                    - Feels trapped by sunk costs and career investment
                    - Wants to change the system that nearly destroyed them

                    Write as if documenting evidence for a future Title IX complaint:"""
                ],

                "business_crisis": [
                    """Generate a first-person narrative from a corporate employee at {company} experiencing severe workplace trauma.

                    Context: {context}
                    Question: "What one thing would you change about your workplace?"

                    Guidelines:
                    - Write as someone experiencing toxic management, harassment, or discrimination
                    - Use corporate terminology and reference specific business systems
                    - Include the financial pressure that traps people in toxic jobs
                    - Reference {company}'s specific culture: {culture_phrase}
                    - Show how corporate trauma affects identity and self-worth
                    - Length: 300-500 characters
                    - Tone: Angry, betrayed, fighting for dignity

                    Write from someone who trusted the company and feels utterly betrayed:""",

                    """You are a corporate employee at {company} whose career and mental health have been destroyed by workplace abuse.

                    Personal details: {demographics}
                    Company culture: {culture_phrase}
                    Abuse type: {trauma_type}

                    Question: "What one thing would you change about your workplace?"

                    Respond as someone who:
                    - Has experienced manager abuse, discrimination, or systematic harassment
                    - Understands how HR protects the company, not employees
                    - Uses business language but shows deep emotional damage
                    - Feels financially trapped but psychologically destroyed
                    - Wants accountability and systemic change

                    Write as if finally speaking truth after months of silence:"""
                ]
            },

            "q24_mental_health_prompts": {
                "healthcare_severe": [
                    """Generate a deeply personal mental health narrative from a healthcare worker at {company}.

                    Context: {context}
                    Question: "How has your workplace affected your mental health?"

                    Create a response that:
                    - Describes specific psychiatric symptoms (PTSD, panic attacks, depression)
                    - References specific medical incidents that caused trauma
                    - Shows the progression from initial shock to chronic symptoms
                    - Includes failed attempts to get help through employee systems
                    - Uses clinical language for symptoms but emotional language for impact
                    - References {company}'s culture: {culture_phrase}
                    - Length: 400-600 characters

                    Write as someone documenting their psychological deterioration:""",

                    """You are healthcare worker at {company} whose mental health has been shattered by workplace trauma.

                    Background: {demographics}
                    Specific incident: {trauma_incident}
                    Culture context: {culture_phrase}

                    Question: "How has your workplace affected your mental health?"

                    Describe your psychological state as someone who:
                    - Has developed clinical PTSD from patient deaths or medical errors
                    - Experiences flashbacks, nightmares, and hypervigilance
                    - Has tried therapy but workplace trauma is ongoing
                    - Feels guilty about being traumatized while trying to help others
                    - Uses both medical terminology and raw emotional expression

                    Write like you're finally admitting the depth of your psychological damage:"""
                ],

                "university_severe": [
                    """Generate a raw mental health narrative from an academic at {company} experiencing psychological breakdown.

                    Context: {context}
                    Question: "How has your workplace affected your mental health?"

                    Write from someone who:
                    - Has developed severe anxiety, depression, or PTSD from academic abuse
                    - Describes the intellectual's way of analyzing their own mental breakdown
                    - References specific academic stressors and power dynamics
                    - Shows how academic identity intertwines with psychological damage
                    - Includes {company}'s specific cultural pressures: {culture_phrase}
                    - Length: 400-600 characters

                    Capture the voice of someone whose intellectual capabilities are being destroyed:""",

                    """You are an academic at {company} documenting your psychological deterioration.

                    Context: {demographics}
                    Academic trauma: {trauma_type}
                    Institution culture: {culture_phrase}

                    Question: "How has your workplace affected your mental health?"

                    Respond as someone who:
                    - Intellectualizes trauma while experiencing deep emotional pain
                    - Has considered or attempted suicide due to academic pressures
                    - Understands the psychological literature but can't escape their own trauma
                    - Feels their intelligence and passion being systematically destroyed
                    - Writes with both clinical precision and emotional rawness

                    Write as if creating evidence for your own psychological autopsy:"""
                ],

                "business_severe": [
                    """Generate an authentic mental health narrative from a corporate employee at {company} experiencing workplace-induced psychological trauma.

                    Context: {context}
                    Question: "How has your workplace affected your mental health?"

                    Create a response showing:
                    - Specific anxiety, depression, or PTSD symptoms from workplace abuse
                    - How corporate trauma affects self-worth and professional identity
                    - Physical symptoms of psychological stress (insomnia, panic, etc.)
                    - Failed attempts to address issues through official channels
                    - Reference to {company}'s culture: {culture_phrase}
                    - Length: 400-600 characters

                    Write as someone whose career success has become psychological destruction:""",

                    """You are a corporate employee at {company} whose mental health has been destroyed by workplace trauma.

                    Personal context: {demographics}
                    Workplace abuse: {trauma_type}
                    Company culture: {culture_phrase}

                    Question: "How has your workplace affected your mental health?"

                    Describe your experience as someone who:
                    - Has developed anxiety disorders or depression from workplace stress
                    - Experiences physical symptoms (panic attacks, insomnia, digestive issues)
                    - Has lost confidence in their professional abilities
                    - Feels trapped between financial needs and psychological safety
                    - Uses business language but shows deep emotional vulnerability

                    Write like you're finally admitting how broken you've become:"""
                ]
            },

            "q25_strength_prompts": {
                "positive_realistic": [
                    """Generate a workplace strength narrative that feels authentic even amid challenges.

                    Context: {context}
                    Company: {company}
                    Culture: {culture_phrase}
                    Question: "What is your workplace's greatest strength?"

                    Write from someone who:
                    - Acknowledges real problems but identifies genuine strengths
                    - Uses specific examples rather than generic corporate speak
                    - Shows how individual resilience or team bonds help survive institutional problems
                    - References {company}'s actual positive elements within {culture_phrase}
                    - Balances realism with hope
                    - Length: 200-400 characters

                    Avoid toxic positivity while highlighting authentic human connections or meaningful work:""",

                    """You work at {company} and despite significant challenges, you can identify genuine strengths.

                    Your situation: {demographics}
                    Company culture: {culture_phrase}
                    Your experience level: {experience}

                    Question: "What is your workplace's greatest strength?"

                    Respond as someone who:
                    - Has experienced workplace difficulties but found sources of resilience
                    - Values specific people, processes, or purposes that make work meaningful
                    - Doesn't use corporate marketing language but speaks authentically
                    - Recognizes that strengths often come from colleagues, not institutions
                    - Shows nuanced understanding of workplace dynamics

                    Write about what actually helps you survive and sometimes thrive:"""
                ]
            }
        }

    def _initialize_psychological_frameworks(self) -> Dict:
        """Initialize psychological authenticity frameworks"""
        return {
            "trauma_symptoms": {
                "ptsd": [
                    "flashbacks to specific incidents",
                    "hypervigilance in workplace",
                    "avoidance of triggers",
                    "emotional numbing",
                    "sleep disturbances",
                    "intrusive thoughts"
                ],
                "anxiety": [
                    "panic attacks before work",
                    "constant worry about performance",
                    "physical symptoms (racing heart, sweating)",
                    "avoidance of certain situations",
                    "overthinking interactions",
                    "fear of criticism"
                ],
                "depression": [
                    "loss of interest in work",
                    "feelings of hopelessness",
                    "fatigue and low energy",
                    "self-worth tied to work failure",
                    "social isolation",
                    "thoughts of quitting or suicide"
                ]
            },

            "coping_mechanisms": {
                "healthy": [
                    "therapy with trauma-informed therapist",
                    "support groups with colleagues",
                    "mindfulness and meditation",
                    "physical exercise for stress relief",
                    "setting boundaries",
                    "seeking supervision or mentorship"
                ],
                "unhealthy": [
                    "alcohol or substance use",
                    "emotional eating or restriction",
                    "workaholism to prove worth",
                    "isolation from support systems",
                    "self-harm behaviors",
                    "complete avoidance of triggers"
                ]
            },

            "help_seeking_patterns": {
                "successful": [
                    "found therapist with workplace trauma experience",
                    "connected with employee resource groups",
                    "used employee assistance programs effectively",
                    "found supportive supervisor or mentor",
                    "joined professional support organizations"
                ],
                "failed": [
                    "HR protected company interests over employee",
                    "EAP therapist didn't understand workplace dynamics",
                    "reporting led to retaliation",
                    "supervisor minimized concerns",
                    "mental health services had long wait times"
                ]
            }
        }

    def _initialize_expression_patterns(self) -> Dict:
        """Initialize human expression authenticity patterns"""
        return {
            "emotional_progression": {
                "shock_to_anger": [
                    "Initially I couldn't believe...",
                    "At first I thought it was just...",
                    "I used to think I could handle...",
                    "When it first happened, I was just confused...",
                    "Now I realize what really happened was..."
                ],
                "denial_to_acceptance": [
                    "I kept telling myself it wasn't that bad...",
                    "Everyone said this was normal, but...",
                    "I thought I was overreacting until...",
                    "Looking back, I was in complete denial..."
                ],
                "hope_to_despair": [
                    "I thought things would get better...",
                    "I kept believing if I just worked harder...",
                    "Every time I hoped for change...",
                    "I've lost all faith that..."
                ]
            },

            "vulnerability_expressions": {
                "admitting_weakness": [
                    "I hate admitting this, but...",
                    "I never thought I'd be the type to...",
                    "It's embarrassing to say...",
                    "I feel like a failure for..."
                ],
                "seeking_validation": [
                    "Am I crazy for thinking...",
                    "Other people must have experienced...",
                    "I need to know I'm not alone in...",
                    "Please tell me this isn't normal..."
                ],
                "expressing_shame": [
                    "I'm ashamed that I let...",
                    "I feel stupid for believing...",
                    "I should have known better...",
                    "Everyone else seems to handle..."
                ]
            },

            "authentic_details": {
                "time_markers": [
                    "three months ago", "last Tuesday", "during my first week",
                    "after the incident in March", "every morning since",
                    "it's been two years now"
                ],
                "physical_details": [
                    "my hands were shaking", "couldn't catch my breath",
                    "felt like throwing up", "my heart was racing",
                    "couldn't stop crying", "completely numb"
                ],
                "specific_locations": [
                    "in the supply closet", "during the staff meeting",
                    "right there in the hallway", "while presenting to the board",
                    "in the bathroom stall", "at my desk"
                ]
            }
        }

    def _initialize_trauma_models(self) -> Dict:
        """Initialize trauma progression models for authentic narratives"""
        return {
            "healthcare_trauma_types": [
                "patient_death_preventable", "medical_error_guilt", "covid_overwhelm",
                "violence_from_patients", "moral_injury", "supervisor_abuse",
                "workplace_bullying", "discrimination", "sexual_harassment"
            ],
            "university_trauma_types": [
                "advisor_abuse", "sexual_harassment", "research_theft",
                "academic_bullying", "discrimination", "financial_exploitation",
                "publication_sabotage", "conference_humiliation", "impostor_syndrome"
            ],
            "business_trauma_types": [
                "manager_abuse", "workplace_harassment", "discrimination",
                "layoff_trauma", "performance_gaslighting", "toxic_culture",
                "overwork_burnout", "ethical_conflicts", "retaliation"
            ]
        }

    def generate_narrative_with_prompts(self, context: NarrativeContext) -> Dict[str, str]:
        """Generate narratives using sophisticated prompt engineering"""

        # Select appropriate prompt templates
        prompt_key = f"{context.domain.lower()}_{context.risk_tier.lower()}"

        narratives = {}

        # Generate Q23 (Change) narrative
        narratives['q23'] = self._generate_change_narrative(context)

        # Generate Q24 (Mental Health) narrative
        narratives['q24'] = self._generate_mental_health_narrative(context)

        # Generate Q25 (Strength) narrative
        narratives['q25'] = self._generate_strength_narrative(context)

        return narratives

    def _generate_change_narrative(self, context: NarrativeContext) -> str:
        """Generate Q23 narrative using prompt engineering"""

        # Select trauma type based on domain and risk tier
        trauma_types = self.trauma_progression_models[f"{context.domain.lower()}_trauma_types"]
        trauma_type = random.choice(trauma_types)

        # Build context for prompt
        prompt_context = {
            "company": context.company,
            "culture_phrase": random.choice(context.company_culture.get("cultural_phrases", ["workplace culture"])),
            "demographics": context.demographics,
            "trauma_type": trauma_type.replace("_", " "),
            "context": f"{context.demographics['position_level']} level {context.demographics['department']} employee"
        }

        # Select appropriate prompt template
        domain_key = f"{context.domain.lower()}_crisis"
        if context.risk_tier in ["Crisis", "At_Risk"]:
            templates = self.prompt_templates["q23_change_prompts"].get(domain_key, [])
        else:
            # Use modified templates for lower risk tiers
            templates = self._adapt_prompts_for_risk_tier(domain_key, context.risk_tier)

        if not templates:
            return self._generate_fallback_narrative(context, "change")

        # Use prompt engineering to generate response
        prompt_template = random.choice(templates)

        # This is where you would integrate with an AI model
        # For this demo, we'll use sophisticated template-based generation
        return self._process_prompt_template(prompt_template, prompt_context, context)

    def _generate_mental_health_narrative(self, context: NarrativeContext) -> str:
        """Generate Q24 narrative with psychological authenticity"""

        # Select symptoms based on risk tier
        if context.risk_tier == "Crisis":
            symptoms = self.psychological_frameworks["trauma_symptoms"]["ptsd"]
        elif context.risk_tier == "At_Risk":
            symptoms = self.psychological_frameworks["trauma_symptoms"]["anxiety"]
        else:
            symptoms = self.psychological_frameworks["trauma_symptoms"]["depression"]

        selected_symptoms = random.sample(symptoms, min(3, len(symptoms)))

        # Build psychological context
        prompt_context = {
            "company": context.company,
            "culture_phrase": random.choice(context.company_culture.get("cultural_phrases", ["workplace culture"])),
            "demographics": context.demographics,
            "symptoms": selected_symptoms,
            "trauma_incident": self._generate_specific_incident(context),
            "context": f"experiencing {context.risk_tier.lower()} level psychological distress"
        }

        # Generate narrative with psychological authenticity
        return self._create_psychological_narrative(prompt_context, context)

    def _generate_strength_narrative(self, context: NarrativeContext) -> str:
        """Generate Q25 narrative balancing realism with positivity"""

        # Even in crisis, people can identify authentic strengths
        prompt_context = {
            "company": context.company,
            "culture_phrase": random.choice(context.company_culture.get("cultural_phrases", ["workplace culture"])),
            "demographics": context.demographics,
            "experience": f"{context.demographics.get('tenure_range', '1-3_years')} experience",
            "context": f"despite challenges, finding authentic workplace strengths"
        }

        return self._create_strength_narrative(prompt_context, context)

    def _process_prompt_template(self, template: str, context: Dict, narrative_context: NarrativeContext) -> str:
        """Process prompt template to generate authentic narrative"""

        # This is where advanced AI generation would occur
        # For demonstration, using sophisticated template processing

        base_narratives = {
            "healthcare_crisis": [
                f"Stop the culture of blame at {context['company']} when patients die. {context['culture_phrase']} creates impossible situations where individual staff get scapegoated for systemic failures. I've developed PTSD from losing three patients in one night during understaffing. Administration talks about resilience while creating the conditions that traumatize us. We need systemic change, not individual therapy for institutional trauma.",

                f"End mandatory overtime at {context['company']} during chronic understaffing. {context['culture_phrase']} expects superhuman performance while cutting resources. I haven't slept properly in months due to trauma flashbacks from preventable patient deaths. The employee assistance program therapist has never worked healthcare. We're breaking down and they're offering us yoga classes.",

                f"Address the physician suicide epidemic at {context['company']}. {context['culture_phrase']} stigmatizes seeking help while creating unbearable conditions. Made a medication error that nearly killed someone - system failure but I'm blamed. Developed panic attacks before every shift. Need real support, not blame and shame culture."
            ],

            "university_crisis": [
                f"End the toxic power dynamics at {context['company']} that enable advisor abuse. {context['culture_phrase']} protects predators while destroying students. My advisor's psychological abuse triggered severe depression and suicidal ideation. Reporting led to retaliation and career sabotage. The system is designed to break us while preserving institutional reputation.",

                f"Stop the academic hazing at {context['company']} disguised as rigor. {context['culture_phrase']} normalizes psychological abuse as professional development. Six years of exploitation, poverty wages, and systematic humiliation. Developed anxiety disorder and eating disorder from constant criticism. Academia is destroying a generation of scholars.",

                f"Address sexual harassment by tenured faculty at {context['company']}. {context['culture_phrase']} creates untouchable predators who control careers. Title IX investigation was a sham - they protect grants over students. PTSD symptoms triggered by campus encounters. Need accountability, not institutional coverups."
            ],

            "business_crisis": [
                f"End the toxic management culture at {context['company']} that destroys employee mental health. {context['culture_phrase']} enables abuse while claiming to value people. Manager's verbal attacks triggered trauma response and panic disorder. HR protects high performers over victims. Need accountability systems that actually work.",

                f"Stop the workplace gaslighting at {context['company']} that makes employees question reality. {context['culture_phrase']} systematically undermines confidence while demanding peak performance. Performance review was character assassination disguised as feedback. Developed severe anxiety and imposter syndrome. Need honest leadership, not manipulation.",

                f"Address discrimination at {context['company']} that's destroying careers and mental health. {context['culture_phrase']} talks diversity while promoting bias. Constant microaggressions and exclusion led to depression and burnout. Reporting resulted in retaliation and isolation. Need systemic change, not diversity theater."
            ]
        }

        # Select appropriate narrative based on domain and risk tier
        domain_key = f"{narrative_context.domain.lower()}_{narrative_context.risk_tier.lower()}"
        if domain_key in ["healthcare_crisis", "university_crisis", "business_crisis"]:
            return random.choice(base_narratives[domain_key])

        return self._generate_fallback_narrative(narrative_context, "change")

    def _create_psychological_narrative(self, context: Dict, narrative_context: NarrativeContext) -> str:
        """Create psychologically authentic mental health narrative"""

        trauma_narratives = {
            "healthcare_severe": [
                f"Lost three patients at {context['company']} in one shift during COVID surge. Haven't slept properly in months - flashbacks every night of ventilator alarms. {context['culture_phrase']} expects emotional compartmentalization that's psychologically impossible. Started drinking to numb the constant anxiety. Panic attacks triggered by hospital sounds. EAP therapist had no healthcare experience. PTSD is real and it's breaking me.",

                f"Medical error at {context['company']} nearly killed pediatric patient - system failure but individual blame. Developed severe guilt and hypervigilance that affects every clinical decision. {context['culture_phrase']} stigmatizes seeking help while creating trauma conditions. Therapy helps but workplace retraumatization is constant. Consider leaving medicine despite student loans and lost years.",

                f"Emergency department at {context['company']} is psychological warfare. This month: three suicide attempts, domestic violence, pediatric abuse case that triggered my own trauma. {context['culture_phrase']} expects superhuman emotional resilience. Can't sleep, can't eat, can't connect with family. Hypervigilant and emotionally numb simultaneously. Need trauma-informed workplace support."
            ],

            "university_severe": [
                f"PhD advisor at {context['company']} psychologically abused me for six years. {context['culture_phrase']} normalizes exploitation as academic training. Developed severe depression, anxiety, and suicidal ideation from constant humiliation. Attempted suicide during dissertation defense preparation. Academic mental health crisis is epidemic but institutions protect reputations over lives.",

                f"Sexual harassment by tenured professor at {context['company']} destroyed my academic career and mental health. {context['culture_phrase']} creates untouchable predators who control student futures. PTSD symptoms triggered by campus encounters. Title IX process retraumatized me while protecting him. Academic system is fundamentally abusive to vulnerable populations.",

                f"Academic job market trauma at {context['company']} created existential crisis about life purpose. {context['culture_phrase']} promises intellectual fulfillment while delivering poverty and exploitation. Seven years of training for nonexistent jobs. Developed anxiety disorder and depression from constant rejection. Identity completely tied to academic success that's impossible to achieve."
            ],

            "business_severe": [
                f"Manager at {context['company']} verbally abused me daily until I developed workplace PTSD. {context['culture_phrase']} enables toxic leadership while claiming employee wellbeing. Panic attacks before meetings, insomnia, intrusive thoughts about work confrontations. HR investigation protected him as high performer. Therapy helps but workplace trauma is ongoing and systematic.",

                f"Workplace harassment at {context['company']} escalated after reporting inappropriate behavior. {context['culture_phrase']} retaliates against truth-tellers while protecting perpetrators. Developed agoraphobia around office buildings and severe anxiety about professional interactions. Self-worth completely destroyed by systematic gaslighting. Need new career despite financial constraints.",

                f"Layoff at {context['company']} announced via Slack while presenting to client. {context['culture_phrase']} treats humans as disposable despite loyalty and performance. Financial panic triggered severe depression and anxiety about family security. Job searching while devastated is traumatic cycle. Self-esteem tied to work success that was arbitrarily destroyed."
            ]
        }

        narrative_key = f"{narrative_context.domain.lower()}_severe"
        if narrative_key in trauma_narratives:
            return random.choice(trauma_narratives[narrative_key])

        return self._generate_fallback_narrative(narrative_context, "mental_health")

    def _create_strength_narrative(self, context: Dict, narrative_context: NarrativeContext) -> str:
        """Create authentic strength narrative that avoids toxic positivity"""

        strength_narratives = {
            "healthcare": [
                f"Despite systemic problems at {context['company']}, our unit has incredible teamwork when crisis hits. {context['culture_phrase']} may be flawed, but individual caregivers support each other through impossible situations. When we lost young father to complications, team rallied around family and processed grief together. Meaning in healing work sustains us through institutional failures.",

                f"Peer support networks at {context['company']} keep us functional despite administrative neglect. {context['culture_phrase']} doesn't acknowledge emotional labor, but colleagues understand trauma in ways outsiders can't. Informal debriefing after difficult cases prevents complete breakdown. Professional bonds forged in crisis are stronger than institutional policies.",

                f"Patient gratitude at {context['company']} reminds me why I chose healthcare despite trauma. {context['culture_phrase']} focuses on metrics, but families remember compassionate care during worst moments. Helping someone heal or die with dignity provides meaning that survives bureaucratic dysfunction. Human connection transcends institutional failures."
            ],

            "university": [
                f"Research community at {context['company']} supports each other despite institutional toxicity. {context['culture_phrase']} may enable abuse, but fellow researchers understand intellectual passion and support vulnerable colleagues. Mentorship from senior faculty outside department provides guidance administration won't. Intellectual freedom still exists within systemic constraints.",

                f"Student connections at {context['company']} remind me education matters despite academic politics. {context['culture_phrase']} may be elitist, but watching students discover critical thinking and intellectual confidence justifies personal sacrifices. Teaching provides meaning that survives administrative dysfunction and career uncertainty.",

                f"Research impact potential at {context['company']} motivates persistence through academic trauma. {context['culture_phrase']} may be broken, but work on climate adaptation could genuinely help vulnerable communities. Mission-driven purpose sustains commitment despite personal costs and institutional failures."
            ],

            "business": [
                f"Team collaboration at {context['company']} helps survive toxic management culture. {context['culture_phrase']} may enable dysfunction, but individual colleagues support each other through impossible demands. Cross-functional projects showcase innovation despite leadership failures. Human connections transcend corporate systems.",

                f"Technical challenges at {context['company']} provide intellectual stimulation despite workplace trauma. {context['culture_phrase']} may be toxic, but complex problem-solving engages capabilities and provides professional growth. Skill development continues even when institutional support fails employees.",

                f"Financial stability at {context['company']} enables family security despite personal costs. {context['culture_phrase']} may be harmful, but compensation supports children's education and healthcare needs. Professional sacrifice for family purpose provides meaning that survives workplace dysfunction."
            ]
        }

        domain_key = narrative_context.domain.lower()
        if domain_key in strength_narratives:
            return random.choice(strength_narratives[domain_key])

        return f"Despite challenges at {context['company']}, committed colleagues and meaningful work provide resilience through difficult times."

    def _generate_specific_incident(self, context: NarrativeContext) -> str:
        """Generate specific workplace incident for narrative authenticity"""

        incidents = {
            "Healthcare": [
                "pediatric patient died during my shift from preventable complications",
                "made medication error that nearly killed someone due to system failure",
                "witnessed colleague breakdown after losing three patients in one week",
                "experienced violence from patient family members blaming staff"
            ],
            "University": [
                "advisor publicly humiliated me during department meeting",
                "professor made sexual advances and threatened career retaliation",
                "research was stolen by supervisor who published without credit",
                "conference presentation was sabotaged by departmental politics"
            ],
            "Business": [
                "manager screamed at me in front of entire team during meeting",
                "experienced systematic harassment after reporting inappropriate behavior",
                "was excluded from promotion despite superior performance metrics",
                "witnessed layoffs announced via email while working with those affected"
            ]
        }

        return random.choice(incidents.get(context.domain, ["experienced significant workplace trauma"]))

    def _adapt_prompts_for_risk_tier(self, domain_key: str, risk_tier: str) -> List[str]:
        """Adapt prompt intensity based on risk tier"""

        # For non-crisis tiers, modify prompts to be less intense
        base_prompts = self.prompt_templates["q23_change_prompts"].get(domain_key, [])

        if risk_tier in ["Safe", "Thriving"]:
            # Create modified versions focusing on improvement rather than crisis
            return [prompt.replace("severe", "moderate").replace("trauma", "stress") for prompt in base_prompts]

        return base_prompts

    def _generate_fallback_narrative(self, context: NarrativeContext, question_type: str) -> str:
        """Generate fallback narrative when templates aren't available"""

        fallbacks = {
            "change": f"Working at {context.company} has shown me that {question_type} needs significant attention in our {context.domain.lower()} environment.",
            "mental_health": f"My experience at {context.company} has affected my mental health in ways I'm still processing.",
            "strength": f"Despite challenges, {context.company} has colleagues and resources that help us navigate difficulties."
        }

        return fallbacks.get(question_type, f"My experience at {context.company} has been significant.")

# Example usage and testing
if __name__ == "__main__":
    print("🧠 AI Narrative Prompt Engineering Engine")
    print("=" * 50)

    engine = AITraumaNarrativeEngine()

    # Test context
    test_context = NarrativeContext(
        domain="Healthcare",
        company="Kaiser Permanente",
        risk_tier="Crisis",
        demographics={"position_level": "Mid", "department": "Nursing", "age_range": "35-44"},
        question_type="mental_health",
        company_culture={"cultural_phrases": ["HMO model pressures", "integrated care challenges"]}
    )

    narratives = engine.generate_narrative_with_prompts(test_context)

    print(f"Q23 Sample: {narratives['q23'][:200]}...")
    print(f"Q24 Sample: {narratives['q24'][:200]}...")
    print(f"Q25 Sample: {narratives['q25'][:200]}...")