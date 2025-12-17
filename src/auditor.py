import os
import json
import google.generativeai as genai
class Auditor:
    def __init__(self, gemini_key=None):
        self.gemini_key = gemini_key or os.getenv("GEMINI_API_KEY")
        
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
    def audit_interaction(self, transcript_text, policy_context):
        """
        Sends transcript and policy context to LLM for auditing.
        Returns a structured dictionary (Score, Violations, Summary).
        """
        
        prompt = f"""
        You are an expert Compliance Auditor for Customer Support.
        
        CONTEXT (Company Policies):
        {policy_context}
        
        TRANSCRIPT TO AUDIT:
        {transcript_text}
        
        INSTRUCTIONS:
        1. Analyze the transcript against the provided policies.
        2. Score the interaction (0-100) based on: Agent Empathy, Professionalism, Clarity, Problem Resolution, Compliance.
        3. Identify any SPECIFIC policy violations.
        4. Provide improvement suggestions.
        
        OUTPUT FORMAT (Strict JSON):
        {{
            "score": <number 0-100>,
            "breakdown": {{
                "empathy": <score>,
                "professionalism": <score>,
                "clarity": <score>,
                "resolution": <score>,
                "compliance": <score>
            }},
            "violations": ["violation 1", "violation 2"],
            "suggestions": ["suggestion 1", "suggestion 2"],
            "summary": "Brief summary of the audit."
        }}
        """
        try:
            if self.gemini_key:
                response = self.gemini_model.generate_content(prompt)
                response_text = response.text
            else:
                return {"error": "No Gemini API Key Configured"}
                
            # Parse JSON
            # Clean up potential markdown formatting ```json ... ```
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            return {"error": f"Audit failed: {str(e)}"}