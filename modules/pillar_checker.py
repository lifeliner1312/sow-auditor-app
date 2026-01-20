"""
Pillar Checker Module
Validates SOW analysis against 9 Mandatory Divestment Pillars
"""

from config import Config
from datetime import datetime

class PillarChecker:
    """Validates and scores SOW compliance against 9 mandatory pillars"""

    def __init__(self):
        self.pillars = Config.PILLARS
        self.pillar_descriptions = Config.PILLAR_DESCRIPTIONS

    def validate_analysis(self, analysis):
        """
        Validate that analysis contains all 9 required pillars

        Args:
            analysis: Dict with 'pillars' list

        Returns:
            Tuple (is_valid, message)
        """

        if not analysis or 'pillars' not in analysis:
            return False, "Invalid analysis structure: missing 'pillars' field"

        validated_pillars = []
        for pillar in analysis['pillars']:
            if 'name' not in pillar:
                return False, "Pillar missing 'name' field"

            if pillar['name'] not in self.pillars:
                return False, f"Invalid pillar: '{pillar['name']}' (not in mandatory 9 pillars)"

            validated_pillars.append(pillar['name'])

        # Check for missing pillars
        missing = set(self.pillars) - set(validated_pillars)
        if missing:
            return False, f"Missing mandatory pillars: {', '.join(missing)}"

        return True, "All 9 mandatory pillars validated successfully"

    def calculate_compliance_score(self, analysis):
        """
        Calculate overall compliance score (0-100%)

        Met = 1.0, Partial = 0.5, Not Met = 0
        """

        if 'pillars' not in analysis:
            return 0

        total = len(analysis['pillars'])
        if total == 0:
            return 0

        met = sum(1 for p in analysis['pillars'] if p.get('status') == 'Met')
        partial = sum(0.5 for p in analysis['pillars'] if p.get('status') == 'Partial')

        score = ((met + partial) / total) * 100
        return round(score, 1)

    def get_critical_failures(self, analysis):
        """
        Identify critical failures requiring immediate escalation

        Returns:
            List of dicts with critical pillar failures
        """

        critical = []

        if 'pillars' not in analysis:
            return critical

        for pillar in analysis['pillars']:
            # Critical if: Not Met OR High/Critical risk
            if (pillar.get('status') == 'Not Met' or 
                pillar.get('risk_level') in ['Critical', 'High']):

                critical.append({
                    'pillar': pillar['name'],
                    'status': pillar.get('status', 'Unknown'),
                    'risk': pillar.get('risk_level', 'Unknown'),
                    'evidence': pillar.get('evidence', 'No evidence provided'),
                    'recommendation': pillar.get('recommendation', 'Immediate escalation required'),
                    'requires_planner_task': self.should_create_planner_task(pillar)
                })

        return critical

    def should_create_planner_task(self, pillar):
        """
        Determine if pillar failure requires Microsoft Planner task creation

        Critical pillars:
        - Pricing Model (must be Fixed Cost)
        - Schedule (must align with timeline)
        """

        critical_pillars = ['Pricing Model', 'Schedule']

        return (pillar['name'] in critical_pillars and 
                pillar.get('status') in ['Not Met', 'Partial'])

    def get_pillar_summary(self, analysis):
        """
        Generate summary statistics for pillars

        Returns:
            Dict with counts and percentages
        """

        if 'pillars' not in analysis:
            return {}

        total = len(analysis['pillars'])
        met = sum(1 for p in analysis['pillars'] if p.get('status') == 'Met')
        partial = sum(1 for p in analysis['pillars'] if p.get('status') == 'Partial')
        not_met = sum(1 for p in analysis['pillars'] if p.get('status') == 'Not Met')

        critical = sum(1 for p in analysis['pillars'] if p.get('risk_level') == 'Critical')
        high = sum(1 for p in analysis['pillars'] if p.get('risk_level') == 'High')
        medium = sum(1 for p in analysis['pillars'] if p.get('risk_level') == 'Medium')
        low = sum(1 for p in analysis['pillars'] if p.get('risk_level') == 'Low')

        return {
            'total': total,
            'met': met,
            'partial': partial,
            'not_met': not_met,
            'critical_risk': critical,
            'high_risk': high,
            'medium_risk': medium,
            'low_risk': low,
            'compliance_rate': round((met / total) * 100, 1) if total > 0 else 0
        }

    def format_compliance_table(self, analysis):
        """
        Format pillar analysis as table data for reports

        Returns:
            List of dicts with table row data
        """

        if 'pillars' not in analysis:
            return []

        table_data = []
        for pillar in analysis['pillars']:
            evidence_text = pillar.get('evidence', 'Not found')
            if len(evidence_text) > 150:
                evidence_text = evidence_text[:150] + '...'

            table_data.append({
                'Pillar': pillar['name'],
                'Status': pillar.get('status', 'Unknown'),
                'Risk Level': pillar.get('risk_level', 'Unknown'),
                'Evidence': evidence_text,
                'Recommendation': pillar.get('recommendation', 'N/A')
            })

        return table_data

    def get_detailed_recommendations(self, analysis):
        """
        Get prioritized recommendations for non-compliant pillars

        Returns:
            List of dicts sorted by priority
        """

        recommendations = []

        for pillar in analysis.get('pillars', []):
            if pillar.get('status') in ['Not Met', 'Partial']:
                priority = 'CRITICAL' if pillar.get('risk_level') == 'Critical' else \
                          'HIGH' if pillar.get('risk_level') == 'High' else \
                          'MEDIUM'

                recommendations.append({
                    'pillar': pillar['name'],
                    'status': pillar.get('status', 'Unknown'),
                    'risk': pillar.get('risk_level', 'Unknown'),
                    'evidence': pillar.get('evidence', 'No evidence'),
                    'recommendation': pillar.get('recommendation', 'Review compliance gap'),
                    'priority': priority,
                    'requires_escalation': self.should_create_planner_task(pillar)
                })

        # Sort by priority (CRITICAL > HIGH > MEDIUM)
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return recommendations

    def check_pricing_model_compliance(self, analysis):
        """
        Special check for Pricing Model pillar (most critical)

        Returns:
            Dict with detailed pricing compliance info
        """

        pricing_pillar = None
        for pillar in analysis.get('pillars', []):
            if pillar['name'] == 'Pricing Model':
                pricing_pillar = pillar
                break

        if not pricing_pillar:
            return {
                'compliant': False,
                'is_fixed_cost': False,
                'has_tm_clauses': True,
                'issues': ['Pricing Model pillar not found in analysis']
            }

        evidence_lower = pricing_pillar.get('evidence', '').lower()

        # Check for Fixed Cost indicators
        fixed_cost_keywords = ['fixed cost', 'fixed price', 'lump sum', 'firm fixed']
        is_fixed_cost = any(keyword in evidence_lower for keyword in fixed_cost_keywords)

        # Check for Time & Material (critical risk)
        tm_keywords = ['time and material', 't&m', 'hourly rate', 'daily rate']
        has_tm_clauses = any(keyword in evidence_lower for keyword in tm_keywords)

        issues = []
        if has_tm_clauses:
            issues.append("⚠️ CRITICAL: Time & Material clauses detected")
        if not is_fixed_cost:
            issues.append("⚠️ Fixed Cost model not clearly stated")

        return {
            'compliant': is_fixed_cost and not has_tm_clauses,
            'is_fixed_cost': is_fixed_cost,
            'has_tm_clauses': has_tm_clauses,
            'status': pricing_pillar.get('status'),
            'risk_level': pricing_pillar.get('risk_level'),
            'issues': issues if issues else ['Pricing model appears compliant']
        }

    def check_schedule_compliance(self, analysis, project_timeline):
        """
        Special check for Schedule pillar against project timeline

        Args:
            analysis: Full analysis dict
            project_timeline: Dict with build/test/cutover dates

        Returns:
            Dict with schedule compliance info
        """

        schedule_pillar = None
        for pillar in analysis.get('pillars', []):
            if pillar['name'] == 'Schedule':
                schedule_pillar = pillar
                break

        if not schedule_pillar:
            return {
                'compliant': False,
                'issues': ['Schedule pillar not found in analysis'],
                'details': 'Unable to verify schedule compliance'
            }

        issues = []
        evidence_lower = schedule_pillar.get('evidence', '').lower()

        # Check if required phases are mentioned
        required_phases = ['build', 'test', 'cutover']
        for phase in required_phases:
            if phase not in evidence_lower:
                issues.append(f"{phase.title()} phase not clearly defined in SOW")

        # Check pillar status
        if schedule_pillar.get('status') != 'Met':
            issues.append(f"Schedule pillar status: {schedule_pillar.get('status')}")

        compliant = len(issues) == 0 and schedule_pillar.get('status') == 'Met'

        return {
            'compliant': compliant,
            'issues': issues if issues else ['Schedule appears aligned with project timeline'],
            'details': schedule_pillar.get('evidence', 'No schedule information found'),
            'status': schedule_pillar.get('status'),
            'risk_level': schedule_pillar.get('risk_level')
        }
