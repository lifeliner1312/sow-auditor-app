"""
LLM Analyzer Module - Deepseek AI Integration
Analyzes SOW documents using 9 Mandatory Divestment Pillars
NOW WITH SOW CONTENT SUMMARY GENERATION
"""

import requests
import json
from config import Config
from datetime import datetime

class LLMAnalyzer:
    """DeepSeek AI integration for divestment SOW analysis"""

    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_url = Config.DEEPSEEK_API_URL
        self.model = Config.DEEPSEEK_MODEL
        self.max_tokens = Config.DEEPSEEK_MAX_TOKENS
        self.temperature = Config.DEEPSEEK_TEMPERATURE

    def analyze_sow(self, document_text, project_timeline, tables=None):
        """
        Analyze SOW document against 9 mandatory pillars

        Args:
            document_text: Extracted text from SOW
            project_timeline: Dict with build/test/cutover dates
            tables: Extracted tables (for cost breakdown analysis)

        Returns:
            Dict with executive_summary, go_no_go, pillars, critical_risks, actionable_redlines
        """
        system_prompt = Config.SYSTEM_PROMPT
        user_prompt = self._build_user_prompt(document_text, project_timeline, tables)

        try:
            response = self._call_deepseek_api(system_prompt, user_prompt)
            analysis = self._parse_response(response)

            # Add metadata
            analysis['analysis_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')
            analysis['ai_model'] = self.model

            return analysis

        except Exception as e:
            raise Exception(f"LLM Analysis failed: {str(e)}")

    def generate_sow_content_summary(self, document_text, tables=None):
        """
        NEW FEATURE: Generate structured SOW content summary

        Args:
            document_text: Full SOW document text
            tables: Extracted tables from document

        Returns:
            Dict with structured summary including:
            - overview (2-3 paragraphs)
            - key_sections (bullet points)
            - scope_highlights (important scope items)
            - deliverables (key deliverables)
            - timeline_overview (schedule summary)
            - cost_structure (pricing breakdown)
            - parties_involved (vendor/client info)
            - special_terms (notable terms/conditions)
        """
        system_prompt = """You are a senior contract analyst specializing in Statement of Work (SOW) documents for IT divestment projects. Your task is to create a comprehensive, well-structured summary of SOW content that executives and stakeholders can quickly understand.

Focus on:
- Clear, professional language
- Structured paragraphs with logical flow
- Important details highlighted
- Key numbers and dates emphasized
- Executive-friendly presentation"""

        # Build summary prompt
        tables_info = f"\n\nEXTRACTED TABLES:\n{json.dumps(tables, indent=2)}" if tables else ""

        user_prompt = f"""Analyze this Statement of Work (SOW) document and create a comprehensive content summary.

SOW DOCUMENT TEXT:
{document_text[:20000]}
{tables_info}

Generate a structured JSON summary with these sections:

1. **overview**: 2-3 well-written paragraphs summarizing:
   - What the SOW is about (project name, purpose)
   - Who the parties are (vendor and client)
   - What work is being performed
   - Why this project matters

2. **key_sections**: List of 5-8 major sections found in the SOW with brief descriptions
   Format: ["Section Name: Brief description", ...]

3. **scope_highlights**: 4-6 bullet points of the most important scope items
   Focus on: Technical work, deliverables, exclusions, dependencies
   Format: ["Important scope item 1", "Important scope item 2", ...]

4. **deliverables**: List of key deliverables mentioned
   Include: Reports, systems, documentation, training
   Format: ["Deliverable 1: Description", ...]

5. **timeline_overview**: Paragraph summarizing the project timeline
   Include: Start/end dates, major phases, milestones, duration

6. **cost_structure**: Paragraph describing the cost/pricing model
   Include: Total cost (if mentioned), payment terms, cost breakdown approach

7. **parties_involved**: Object with:
   - vendor_name: Name of service provider
   - client_name: Client organization
   - vendor_role: What vendor is responsible for
   - client_role: What client is responsible for

8. **special_terms**: List of 3-5 notable terms, conditions, or requirements
   Focus on: Unique clauses, important constraints, special conditions
   Format: ["Special term 1", ...]

9. **technology_stack**: List of technologies, systems, or tools mentioned (if any)
   Format: ["Technology 1", "Technology 2", ...]

10. **assumptions_constraints**: List of key assumptions or constraints
    Format: ["Assumption/Constraint 1", ...]

RESPONSE FORMAT (Valid JSON):
{{
    "overview": "Well-written 2-3 paragraph summary...",
    "key_sections": [
        "Introduction: Overview of project scope and objectives",
        "Technical Requirements: Detailed system specifications..."
    ],
    "scope_highlights": [
        "Migration of 50+ enterprise applications to new infrastructure",
        "Data validation and reconciliation for 10TB dataset"
    ],
    "deliverables": [
        "Technical Design Document: Complete system architecture specifications",
        "Migration Scripts: Automated tools for data transfer"
    ],
    "timeline_overview": "The project spans 6 months from January to June 2025...",
    "cost_structure": "Fixed-price contract valued at $500,000 with milestone-based payments...",
    "parties_involved": {{
        "vendor_name": "Acme IT Solutions",
        "client_name": "Shell",
        "vendor_role": "Full end-to-end migration services including...",
        "client_role": "Provide access to systems and subject matter experts..."
    }},
    "special_terms": [
        "Vendor assumes all data migration risks with 99.9% accuracy guarantee",
        "Client has right to terminate with 30 days notice"
    ],
    "technology_stack": [
        "SAP ECC 6.0",
        "Oracle Database 12c"
    ],
    "assumptions_constraints": [
        "Client will provide access to all source systems by project start date",
        "No changes to source systems during migration window"
    ]
}}

CRITICAL: Return ONLY valid JSON. No markdown. No extra text. Use professional language suitable for executive review."""

        try:
            # Call Deepseek API
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }

            data = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': 0.3,  # Focused, consistent summaries
                'max_tokens': 3000   # Enough for comprehensive summary
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=120
            )

            if response.status_code != 200:
                raise Exception(f"API Error {response.status_code}: {response.text}")

            result = response.json()
            content = result['choices'][0]['message']['content'].strip()

            # Clean markdown code blocks
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                content = content[start:end].strip()
            elif '```' in content:
                start = content.find('```') + 3
                end = content.find('```', start)
                content = content[start:end].strip()

            # Parse JSON
            summary = json.loads(content)

            # Add metadata
            summary['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')
            summary['ai_model'] = self.model

            return summary

        except Exception as e:
            raise Exception(f"SOW Content Summary generation failed: {str(e)}")

    def _build_user_prompt(self, document_text, project_timeline, tables):
        """Build detailed user prompt with SOW content"""

        tables_info = f"\n\nEXTRACTED TABLES: {len(tables)} tables found" if tables else "\n\nNo tables extracted"

        prompt = f"""Analyze this SOW document for a Shell divestment project:

PROJECT TIMELINE (Hard Deadlines):
- Project: {project_timeline.get('project_name', 'N/A')}
- Build Phase End: {project_timeline.get('build_end_date', 'N/A')}
- Test Phase End: {project_timeline.get('test_end_date', 'N/A')}
- Cutover Phase End: {project_timeline.get('cutover_end_date', 'N/A')}

SOW DOCUMENT TEXT (First 15,000 chars):
{document_text[:15000]}
{tables_info}

ANALYZE AGAINST 9 MANDATORY PILLARS:

1. **Pricing Model** (CRITICAL)
   - Must be Fixed Cost (flag T&M as CRITICAL)
   - Check for granular cost breakdown
   - Look for payment milestones

2. **Responsibilities**
   - Shell vs. Vendor responsibilities explicitly defined
   - No ambiguous language
   - RACI matrix or clear accountability

3. **Schedule**
   - Clear Build, Test, Cutover dates
   - Must align with project timeline above
   - Milestones defined

4. **Licensing**
   - Temporary licenses for Build/Test/Cutover
   - Start/end dates specified
   - License costs itemized

5. **Master Contract Reference**
   - Explicit MSA or contract number
   - Shell-Vendor agreement referenced

6. **Sign-off Blocks**
   - Formal signature spaces
   - Both parties (Shell & Vendor)

7. **Change Management**
   - Clear change request process
   - Approval workflows defined

8. **Risk & Terms Mitigation**
   - Check for vendor-favoring clauses
   - Liability terms favor Shell
   - No delay-causing T&Cs

9. **Data Handling**
   - If extraction scope: Data Verification step exists
   - Data quality checks before cutover
   - Carve-out process defined

RESPONSE FORMAT (Valid JSON):
{{
    "executive_summary": "3-sentence overview of SOW quality and findings",
    "go_no_go": "Go" or "No-Go",
    "pillars": [
        {{
            "name": "Pricing Model",
            "status": "Met" | "Partial" | "Not Met",
            "risk_level": "Critical" | "High" | "Medium" | "Low",
            "evidence": "Specific quote or finding from document",
            "recommendation": "Actionable suggestion to protect Shell"
        }},
        ... (all 9 pillars)
    ],
    "critical_risks": [
        "Risk 1: Description",
        "Risk 2: Description"
    ],
    "actionable_redlines": [
        "Redline 1: Change X to Y because...",
        "Redline 2: Add clause Z to protect..."
    ]
}}

CRITICAL: Return ONLY valid JSON. No markdown. No extra text."""

        return prompt

    def _call_deepseek_api(self, system_prompt, user_prompt):
        """Call Deepseek API"""

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=120
            )

            if response.status_code != 200:
                raise Exception(f"API Error {response.status_code}: {response.text}")

            return response.json()

        except requests.exceptions.Timeout:
            raise Exception("API request timed out (120s)")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def _parse_response(self, response):
        """Parse Deepseek API response"""

        try:
            content = response['choices'][0]['message']['content'].strip()

            # Clean markdown code blocks
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                content = content[start:end].strip()
            elif '```' in content:
                start = content.find('```') + 3
                end = content.find('```', start)
                content = content[start:end].strip()

            # Parse JSON
            analysis = json.loads(content)

            # Validate structure
            if 'pillars' not in analysis:
                raise ValueError("Response missing 'pillars' field")
            if 'executive_summary' not in analysis:
                raise ValueError("Response missing 'executive_summary' field")

            return analysis

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}\n\nResponse: {content[:500]}")
        except KeyError as e:
            raise Exception(f"Invalid API response structure: {str(e)}")
        except Exception as e:
            raise Exception(f"Response parsing error: {str(e)}")

    def get_redline_suggestions(self, pillar_name, current_text):
        """
        Get specific redline suggestions for a problematic clause

        Args:
            pillar_name: Which pillar the clause relates to
            current_text: The problematic clause text

        Returns:
            Dict with redline suggestions
        """
        prompt = f"""As a Shell IT contracts expert, provide redline suggestions for this clause:

PILLAR: {pillar_name}
CURRENT TEXT: "{current_text}"

Provide 2-3 specific redline suggestions to protect Shell's interests in this divestment project.

Format as JSON:
{{
    "suggestions": [
        {{
            "original": "text to replace",
            "redlined": "improved text",
            "reason": "why this protects Shell"
        }}
    ]
}}"""

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        data = {
            'model': self.model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.2,
            'max_tokens': 1000
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60
            )

            result = response.json()
            content = result['choices'][0]['message']['content'].strip()

            # Clean markdown
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                content = content[start:end].strip()

            return json.loads(content)

        except Exception as e:
            return {'suggestions': [{'error': str(e)}]}
