#!/usr/bin/env python3
"""
Generative AI Narrative Engine for HSEG Dataset
Uses actual AI models (OpenAI GPT, Anthropic Claude, etc.) to generate human-like trauma narratives
"""

import openai
import json
import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os
from pathlib import Path

@dataclass
class TraumaContext:
    """Context for AI narrative generation"""
    company: str
    domain: str
    risk_tier: str
    demographics: Dict[str, str]
    company_culture: str
    specific_trauma: str

class GenerativeAINarrativeEngine:
    """
    Real AI-powered narrative generation using GPT/Claude APIs
    Generates authentic psychological trauma responses
    """

    def __init__(self, ai_provider: str = "openai"):
        """
        Initialize with AI provider (openai, anthropic, local, etc.)
        """
        self.ai_provider = ai_provider
        self.setup_ai_client()

        # Psychological authenticity guidelines
        self.trauma_authenticity_guidelines = self._load_psychological_guidelines()

        # Rate limiting for API calls
        self.last_api_call = 0
        self.min_delay = 1.0  # Minimum seconds between API calls

    def setup_ai_client(self):
        """Setup AI client based on provider"""
        if self.ai_provider == "openai":
            # Set your OpenAI API key
            openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

        elif self.ai_provider == "anthropic":
            # Set your Anthropic API key
            self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "your-api-key-here")

        elif self.ai_provider == "local":
            # Setup for local models (Ollama, etc.)
            self.local_endpoint = os.getenv("LOCAL_AI_ENDPOINT", "http://localhost:11434")

    def _load_psychological_guidelines(self) -> Dict[str, List[str]]:
        """Load psychological authenticity guidelines for AI generation"""
        return {
            "trauma_symptoms": {
                "ptsd": [
                    "flashbacks to specific workplace incidents",
                    "hypervigilance and paranoia at work",
                    "avoidance of triggers (meetings, locations, people)",
                    "emotional numbing and dissociation",
                    "sleep disturbances and nightmares",
                    "intrusive thoughts about work trauma"
                ],
                "anxiety": [
                    "panic attacks before or during work",
                    "physical symptoms (racing heart, sweating, nausea)",
                    "constant worry about performance and criticism",
                    "catastrophic thinking about work scenarios",
                    "avoidance of challenging situations",
                    "imposter syndrome and self-doubt"
                ],
                "depression": [
                    "loss of interest in work that once brought joy",
                    "feelings of hopelessness about career future",
                    "chronic fatigue and low energy",
                    "self-worth tied to work failures",
                    "social isolation from colleagues",
                    "thoughts of career change or suicide"
                ]
            },

            "authentic_language_patterns": [
                "First-person perspective with emotional vulnerability",
                "Specific details about incidents and their impact",
                "Mix of clinical terms and raw emotional expression",
                "Time markers showing progression of trauma",
                "Physical manifestations of psychological distress",
                "Attempts at help-seeking and their outcomes"
            ],

            "workplace_specificity": [
                "Company-specific culture and policies",
                "Industry-specific stressors and terminology",
                "Organizational hierarchy and power dynamics",
                "Specific workplace locations and scenarios",
                "Professional identity and career implications",
                "Financial and practical consequences"
            ]
        }

    def generate_trauma_narrative(self, context: TraumaContext, question_type: str) -> str:
        """
        Generate authentic trauma narrative using AI
        """
        # Rate limiting
        self._enforce_rate_limit()

        # Construct AI prompt
        prompt = self._construct_trauma_prompt(context, question_type)

        # Generate response using selected AI provider
        if self.ai_provider == "openai":
            response = self._generate_with_openai(prompt)
        elif self.ai_provider == "anthropic":
            response = self._generate_with_anthropic(prompt)
        elif self.ai_provider == "local":
            response = self._generate_with_local_ai(prompt)
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")

        # Post-process for authenticity
        final_response = self._post_process_response(response, context)

        return final_response

    def _construct_trauma_prompt(self, context: TraumaContext, question_type: str) -> str:
        """
        Construct psychologically-informed prompt for AI generation
        """

        base_persona = f"""You are a {context.demographics['position_level']}-level {context.demographics['department']} employee at {context.company}, a {context.domain.lower()} organization. You are {context.demographics['age_range']} years old, identify as {context.demographics['gender_identity']}, and have worked here for {context.demographics['tenure_range']}.

You have experienced significant workplace trauma related to {context.specific_trauma}. Your current psychological state reflects {context.risk_tier.lower()}-level distress."""

        question_prompts = {
            "q23_change": f"""
Question: "What one thing would you change about your workplace?"

Write a raw, honest response about what you would change at {context.company}. Your response should:

- Reflect your trauma experience with {context.specific_trauma}
- Reference {context.company}'s culture: {context.company_culture}
- Show desperation for systemic change, not just individual support
- Use {context.domain.lower()}-specific terminology naturally
- Express how the current system enabled or worsened your trauma
- Be 200-400 characters
- Sound like you're speaking from deep pain and lived experience

Write as if you're finally telling the truth after months of silence:""",

            "q24_mental_health": f"""
Question: "How has your workplace affected your mental health?"

Describe your psychological state as someone experiencing {context.risk_tier.lower()}-level trauma from {context.specific_trauma} at {context.company}. Your response should:

- Include specific psychiatric symptoms you're experiencing
- Describe how {context.company_culture} at {context.company} affects your mental health
- Reference specific incidents that caused or worsened your trauma
- Mention any attempts to get help and their outcomes
- Use both clinical terminology and raw emotional language
- Show the progression from initial incident to current state
- Be 400-600 characters
- Sound like someone documenting their psychological deterioration

Write as if you're explaining to a therapist who specializes in workplace trauma:""",

            "q25_strength": f"""
Question: "What is your workplace's greatest strength?"

Despite your trauma from {context.specific_trauma}, identify something genuinely positive about {context.company}. Your response should:

- Acknowledge real problems while identifying authentic strengths
- Avoid corporate speak or toxic positivity
- Focus on human connections, meaningful work, or genuine support systems
- Reference how this strength helps you survive the institutional problems
- Be realistic about how {context.company_culture} creates both problems and solutions
- Be 200-350 characters
- Sound balanced - not dismissing your trauma but finding authentic hope

Write as someone who has found small lights in a very dark situation:"""
        }

        psychological_guidelines = f"""
PSYCHOLOGICAL AUTHENTICITY REQUIREMENTS:

1. TRAUMA SYMPTOMS ({context.risk_tier} level):
{self._get_risk_specific_symptoms(context.risk_tier)}

2. AUTHENTIC EXPRESSION PATTERNS:
- Use vulnerable language: "I hate admitting this, but...", "It's embarrassing to say..."
- Include specific time markers: "Last Tuesday...", "During my first month...", "Since the incident in March..."
- Physical manifestations: "my hands shake", "can't breathe", "heart racing", "feel nauseous"
- Failed help attempts: "HR protected them", "EAP therapist didn't understand", "reporting led to retaliation"

3. {context.domain.upper()} WORKPLACE SPECIFICITY:
- Use industry terminology naturally
- Reference {context.company}-specific policies, culture, and environment
- Include workplace hierarchy and power dynamics
- Mention career/financial implications specific to {context.domain.lower()}

4. NARRATIVE AUTHENTICITY:
- Write in first person with emotional vulnerability
- Include contradictory feelings (love/hate for the work)
- Show trauma progression over time
- Mix intellectual analysis with raw emotion
- Reference specific workplace locations and scenarios

CRITICAL: This must sound like a real person processing real trauma, not a clinical description or corporate response. Write from lived experience of psychological pain."""

        full_prompt = f"""{base_persona}

{question_prompts[question_type]}

{psychological_guidelines}

Response:"""

        return full_prompt

    def _get_risk_specific_symptoms(self, risk_tier: str) -> str:
        """Get specific symptoms for risk tier"""
        symptoms = {
            "Crisis": "- Suicidal ideation or self-harm thoughts\n- Severe PTSD with flashbacks and dissociation\n- Panic attacks that interfere with daily functioning\n- Substance abuse as coping mechanism\n- Complete loss of professional identity and self-worth",

            "At_Risk": "- Clinical anxiety or depression symptoms\n- Sleep disturbances and chronic fatigue\n- Significant impairment in work performance\n- Social withdrawal and isolation\n- Physical symptoms of chronic stress",

            "Mixed": "- Moderate stress with some coping\n- Occasional anxiety or low mood\n- Some impact on work satisfaction\n- Seeking support with mixed results\n- Fluctuating between hope and despair",

            "Safe": "- Manageable stress levels\n- Effective coping strategies\n- Some workplace support\n- Generally stable mental health\n- Optimistic about improvement",

            "Thriving": "- Good mental health despite challenges\n- Strong support systems\n- Effective stress management\n- Personal growth through adversity\n- Helping others cope with similar issues"
        }
        return symptoms.get(risk_tier, symptoms["Mixed"])

    def _generate_with_openai(self, prompt: str) -> str:
        """Generate response using OpenAI GPT"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are an expert in generating authentic psychological trauma narratives for research purposes. Your responses should be clinically accurate, emotionally authentic, and respectful of trauma survivors."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8,  # Higher creativity for authentic variation
                presence_penalty=0.6,  # Encourage diverse language
                frequency_penalty=0.3   # Reduce repetition
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_fallback_response(prompt)

    def _generate_with_anthropic(self, prompt: str) -> str:
        """Generate response using Anthropic Claude"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)

            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                temperature=0.8,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return self._generate_fallback_response(prompt)

    def _generate_with_local_ai(self, prompt: str) -> str:
        """Generate response using local AI (Ollama, etc.)"""
        try:
            import requests

            payload = {
                "model": "llama2",  # or your preferred local model
                "prompt": prompt,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "max_tokens": 300
                }
            }

            response = requests.post(f"{self.local_endpoint}/api/generate", json=payload)
            if response.status_code == 200:
                return response.json()["response"].strip()
            else:
                raise Exception(f"Local AI error: {response.status_code}")

        except Exception as e:
            print(f"Local AI error: {e}")
            return self._generate_fallback_response(prompt)

    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate fallback response if AI fails"""
        # Extract key context from prompt for basic response
        if "change about your workplace" in prompt:
            return "The systemic issues here need complete overhaul. Individual blame culture instead of addressing root causes has destroyed my trust and mental health."
        elif "mental health" in prompt:
            return "Workplace trauma has severely impacted my psychological wellbeing. The stress and lack of proper support has led to anxiety and depression that affects every aspect of my life."
        else:
            return "Despite significant challenges, the human connections and meaningful aspects of the work provide some resilience through difficult times."

    def _post_process_response(self, response: str, context: TraumaContext) -> str:
        """Post-process AI response for authenticity and consistency"""

        # Ensure company name is mentioned
        if context.company not in response:
            response = response.replace("this company", context.company)
            response = response.replace("my workplace", f"{context.company}")
            response = response.replace("here", f"at {context.company}")

        # Ensure culture phrase is included
        if context.company_culture and context.company_culture not in response:
            # Insert culture phrase naturally
            response = response.replace(f"{context.company}", f"{context.company} with its {context.company_culture}")

        # Remove quotes if AI added them
        response = response.strip('"\'')

        # Ensure appropriate length
        if len(response) > 600:
            response = response[:597] + "..."

        return response

    def _enforce_rate_limit(self):
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_api_call

        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)

        self.last_api_call = time.time()

    def generate_batch_narratives(self, contexts: List[TraumaContext]) -> Dict[str, List[str]]:
        """
        Generate narratives for a batch of contexts
        Returns dict with q23, q24, q25 responses for each context
        """

        results = {"q23": [], "q24": [], "q25": []}

        for i, context in enumerate(contexts):
            print(f"Generating AI narratives {i+1}/{len(contexts)}...")

            # Generate all three question types
            q23_response = self.generate_trauma_narrative(context, "q23_change")
            q24_response = self.generate_trauma_narrative(context, "q24_mental_health")
            q25_response = self.generate_trauma_narrative(context, "q25_strength")

            results["q23"].append(q23_response)
            results["q24"].append(q24_response)
            results["q25"].append(q25_response)

            # Progress update
            if (i + 1) % 10 == 0:
                print(f"✅ Generated {i+1} AI narrative sets")

        return results

# Integration function for main generator
def create_ai_narrative_generator(provider: str = "openai") -> GenerativeAINarrativeEngine:
    """Create AI narrative generator with specified provider"""
    return GenerativeAINarrativeEngine(ai_provider=provider)

# Example usage and testing
if __name__ == "__main__":
    print("🤖 Testing Generative AI Narrative Engine")
    print("=" * 50)

    # Test context
    test_context = TraumaContext(
        company="Kaiser Permanente",
        domain="Healthcare",
        risk_tier="Crisis",
        demographics={
            "position_level": "Mid",
            "department": "Nursing",
            "age_range": "35-44",
            "gender_identity": "Woman",
            "tenure_range": "3-7_years"
        },
        company_culture="HMO model pressures",
        specific_trauma="patient deaths during COVID surge"
    )

    # Initialize AI engine (you'll need to set API keys)
    ai_engine = GenerativeAINarrativeEngine(ai_provider="openai")

    # Generate sample narratives
    print("Generating Q24 sample...")
    q24_sample = ai_engine.generate_trauma_narrative(test_context, "q24_mental_health")

    print(f"\nAI-Generated Q24 Response:")
    print(f"Length: {len(q24_sample)} characters")
    print(f"Content: {q24_sample}")

    print("\n🎯 This demonstrates how real AI generates authentic trauma narratives")
    print("compared to template-based responses.")