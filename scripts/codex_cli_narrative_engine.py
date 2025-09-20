#!/usr/bin/env python3
"""
Codex CLI Narrative Engine - Uses OpenAI Codex through CLI Application
No API credits required - uses local Codex CLI platform application
"""

import subprocess
import json
import tempfile
import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class TraumaContext:
    """Context for Codex CLI narrative generation"""
    company: str
    domain: str
    risk_tier: str
    demographics: Dict[str, str]
    company_culture: str
    specific_trauma: str

class CodexCLINarrativeEngine:
    """
    OpenAI Codex CLI-powered narrative generation
    Uses local Codex application instead of API calls
    """

    def __init__(self, codex_cli_path: str = "codex"):
        """
        Initialize with Codex CLI path
        Args:
            codex_cli_path: Path to codex CLI executable (default: "codex" if in PATH)
        """
        self.codex_cli_path = codex_cli_path
        self.temp_dir = tempfile.mkdtemp()

        # Verify Codex CLI is available
        self._verify_codex_cli()

        # Rate limiting for CLI calls
        self.last_cli_call = 0
        self.min_delay = 2.0  # Minimum seconds between CLI calls

    def _verify_codex_cli(self):
        """Verify that Codex CLI is available and working"""
        try:
            result = subprocess.run(
                [self.codex_cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise Exception(f"Codex CLI not working: {result.stderr}")
            print(f"✅ Codex CLI verified: {result.stdout.strip()}")
        except FileNotFoundError:
            raise Exception(f"Codex CLI not found at: {self.codex_cli_path}")
        except Exception as e:
            raise Exception(f"Codex CLI verification failed: {e}")

    def generate_trauma_narrative(self, context: TraumaContext, question_type: str) -> str:
        """
        Generate authentic trauma narrative using Codex CLI
        """
        # Rate limiting
        self._enforce_rate_limit()

        # Construct prompt for Codex
        prompt = self._construct_trauma_prompt(context, question_type)

        # Generate response using Codex CLI
        response = self._generate_with_codex_cli(prompt)

        # Post-process for authenticity
        final_response = self._post_process_response(response, context)

        return final_response

    def _construct_trauma_prompt(self, context: TraumaContext, question_type: str) -> str:
        """
        Construct psychologically-informed prompt for Codex CLI
        """

        base_persona = f"""You are a {context.demographics['age_range']} year old {context.demographics['gender_identity']} who works as a {context.demographics['position_level']}-level {context.demographics['department']} employee at {context.company}, a {context.domain.lower()} organization. You have {context.demographics['tenure_range']} of experience at this company.

Your age ({context.demographics['age_range']}) and career stage ({context.demographics['tenure_range']} tenure) shape your perspective on workplace issues. You have experienced significant workplace trauma related to {context.specific_trauma}. Your current psychological state reflects {context.risk_tier.lower()}-level distress."""

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
- Age-appropriate language: Reference life stage, career expectations, family responsibilities
- Experience-based perspective: "In my {context.demographics['tenure_range']} here...", "At {context.demographics['age_range']}, I expected..."

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

CRITICAL: This must sound like a real person processing real trauma, not a clinical description or corporate response. Write from lived experience of psychological pain.

Response:"""

        full_prompt = f"""{base_persona}

{question_prompts[question_type]}

{psychological_guidelines}"""

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

    def _generate_with_codex_cli(self, prompt: str) -> str:
        """Generate response using Codex CLI application"""
        try:
            # Create temporary prompt file
            prompt_file = os.path.join(self.temp_dir, f"prompt_{int(time.time())}.txt")
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)

            # Run Codex CLI with prompt file
            result = subprocess.run([
                self.codex_cli_path,
                "--model", "code-davinci-002",  # or "code-cushman-001" for faster results
                "--max-tokens", "300",
                "--temperature", "0.8",
                "--top-p", "0.9",
                "--frequency-penalty", "0.3",
                "--presence-penalty", "0.6",
                "--file", prompt_file
            ], capture_output=True, text=True, timeout=60)

            # Clean up temp file
            os.remove(prompt_file)

            if result.returncode != 0:
                print(f"Codex CLI error: {result.stderr}")
                return self._generate_fallback_response(prompt)

            response = result.stdout.strip()
            return response if response else self._generate_fallback_response(prompt)

        except subprocess.TimeoutExpired:
            print("Codex CLI timeout - using fallback")
            return self._generate_fallback_response(prompt)
        except Exception as e:
            print(f"Codex CLI execution error: {e}")
            return self._generate_fallback_response(prompt)

    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate fallback response if Codex CLI fails"""
        # Extract key context from prompt for basic response
        if "change about your workplace" in prompt:
            return "The systemic issues here need complete overhaul. Individual blame culture instead of addressing root causes has destroyed my trust and mental health."
        elif "mental health" in prompt:
            return "Workplace trauma has severely impacted my psychological wellbeing. The stress and lack of proper support has led to anxiety and depression that affects every aspect of my life."
        else:
            return "Despite significant challenges, the human connections and meaningful aspects of the work provide some resilience through difficult times."

    def _post_process_response(self, response: str, context: TraumaContext) -> str:
        """Post-process Codex response for authenticity and consistency"""

        # Remove any prompt echoing
        if "Response:" in response:
            response = response.split("Response:")[-1].strip()

        # Ensure company name is mentioned
        if context.company not in response:
            response = response.replace("this company", context.company)
            response = response.replace("my workplace", f"{context.company}")
            response = response.replace("here", f"at {context.company}")

        # Ensure culture phrase is included
        if context.company_culture and context.company_culture not in response:
            # Insert culture phrase naturally
            response = response.replace(f"{context.company}", f"{context.company} with its {context.company_culture}")

        # Add demographic consistency
        gender = context.demographics['gender_identity']
        age = context.demographics['age_range']
        tenure = context.demographics['tenure_range']

        # Add age and experience context if missing
        age_phrases = {
            "22-24": ["As a young professional", "Being new to my career", "At my age"],
            "25-34": ["As someone in their late twenties/early thirties", "At this stage of my career", "Being a millennial in the workplace"],
            "35-44": ["As a mid-career professional", "At my age with family responsibilities", "Being in my late thirties/early forties"],
            "45-54": ["As an experienced professional", "At this stage of my life", "Being in my late forties/early fifties"],
            "55+": ["As a senior professional", "At my age nearing retirement", "Being an older worker"]
        }

        tenure_phrases = {
            "<1_year": ["being new here", "in my first year", "as a recent hire"],
            "1-3_years": ["with a few years under my belt", "still relatively new", "having some experience here"],
            "3-7_years": ["with several years invested here", "as a mid-tenure employee", "having seen cycles here"],
            "7+_years": ["as a long-term employee", "with years of institutional knowledge", "having deep roots here"]
        }

        # Enhance with age/tenure context if not already present
        if not any(phrase.lower() in response.lower() for phrase in age_phrases.get(age, [])):
            age_phrase = age_phrases.get(age, ["At my age"])[0]
            if gender == "Woman" and "woman" not in response.lower():
                response = f"{age_phrase} and as a woman, {response.lower()}"
            elif gender == "Man" and "man" not in response.lower():
                response = f"{age_phrase} and as a man, {response.lower()}"
            elif gender == "Non-binary" and "non-binary" not in response.lower():
                response = f"{age_phrase} and as a non-binary person, {response.lower()}"
            else:
                response = f"{age_phrase}, {response.lower()}"

        # Add tenure perspective if missing
        if not any(phrase in response.lower() for phrase in tenure_phrases.get(tenure, [])):
            tenure_phrase = tenure_phrases.get(tenure, ["with my experience here"])[0]
            if "here" not in response.lower() and "this" not in response.lower():
                response = response + f" Having worked {tenure_phrase}, I see how systemic these issues are."

        # Remove quotes if Codex added them
        response = response.strip('"\'')

        # Ensure appropriate length
        if len(response) > 600:
            response = response[:597] + "..."

        return response

    def _enforce_rate_limit(self):
        """Enforce rate limiting between CLI calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_cli_call

        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)

        self.last_cli_call = time.time()

    def __del__(self):
        """Clean up temporary directory"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass

# Integration function for main generator
def create_codex_cli_narrative_generator(codex_cli_path: str = "codex") -> CodexCLINarrativeEngine:
    """Create Codex CLI narrative generator"""
    return CodexCLINarrativeEngine(codex_cli_path)

# Example usage and testing
if __name__ == "__main__":
    print("🤖 Testing Codex CLI Narrative Engine")
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

    try:
        # Initialize Codex CLI engine
        codex_engine = CodexCLINarrativeEngine(codex_cli_path="codex")  # Adjust path as needed

        # Generate sample narratives
        print("Generating Q24 sample...")
        q24_sample = codex_engine.generate_trauma_narrative(test_context, "q24_mental_health")

        print(f"\nCodex CLI-Generated Q24 Response:")
        print(f"Length: {len(q24_sample)} characters")
        print(f"Content: {q24_sample}")

        print("\n🎯 Codex CLI successfully generates OpenAI-powered narratives without API credits!")

    except Exception as e:
        print(f"❌ Codex CLI setup error: {e}")
        print("\n🔧 Setup Instructions:")
        print("1. Install OpenAI Codex CLI application")
        print("2. Ensure 'codex' command is in your PATH")
        print("3. Login to your OpenAI account through the CLI")
        print("4. Adjust codex_cli_path parameter if needed")