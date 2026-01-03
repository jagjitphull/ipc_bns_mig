"""
AI Legal Reasoning Agent
Analyzes IPC-BNS transitions and generates lawyer-style memos
"""
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class LegalReasoningAgent:
    def __init__(self, db_session, rag_system, llm_client=None):
        """
        Initialize legal reasoning agent

        Args:
            db_session: SQLAlchemy session for database access
            rag_system: CaseLawRAG instance for case retrieval
            llm_client: Optional LLM client (Anthropic Claude or OpenAI)
        """
        self.db = db_session
        self.rag = rag_system
        self.llm = llm_client

    def analyze_section_transition(self, ipc_section: str) -> Dict[str, Any]:
        """
        Analyze transition from IPC to BNS for a specific section

        Returns comprehensive analysis including:
        - IPC section details
        - BNS equivalent
        - Doctrinal changes
        - Relevant case law
        - Validity warnings
        """
        from database import IPCBNSMapping

        # Get mapping from database
        mapping = self.db.query(IPCBNSMapping).filter(
            IPCBNSMapping.ipc_section == ipc_section
        ).first()

        if not mapping:
            return {
                "error": f"IPC Section {ipc_section} not found in database",
                "ipc_section": ipc_section
            }

        # Retrieve relevant case law
        cases = self.rag.search_by_section(ipc_section, n_results=10)

        # Get associated landmark cases from database
        landmark_cases = []
        for case in mapping.cases:
            landmark_cases.append({
                "case_name": case.case_name,
                "citation": case.citation,
                "year": case.year,
                "court": case.court,
                "ratio_decidendi": case.ratio_decidendi,
                "validity_status": case.validity_status,
                "validity_reasoning": case.validity_reasoning
            })

        # Analyze doctrinal changes
        change_analysis = self._analyze_doctrinal_changes(mapping)

        # Generate validity warnings for precedents
        validity_warnings = self._generate_validity_warnings(mapping, landmark_cases)

        return {
            "ipc_section": mapping.ipc_section,
            "ipc_description": mapping.ipc_description,
            "ipc_text": mapping.ipc_text,
            "bns_section": mapping.bns_section,
            "bns_description": mapping.bns_description,
            "bns_text": mapping.bns_text,
            "category": mapping.category,
            "punishment": mapping.punishment,
            "has_changes": mapping.has_changes,
            "change_type": mapping.change_type,
            "change_summary": mapping.change_summary,
            "change_analysis": change_analysis,
            "landmark_cases": landmark_cases,
            "validity_warnings": validity_warnings,
            "rag_results": cases
        }

    def _analyze_doctrinal_changes(self, mapping) -> Dict[str, Any]:
        """Detailed analysis of doctrinal changes between IPC and BNS"""

        if not mapping.has_changes:
            return {
                "has_substantive_changes": False,
                "summary": "No substantive changes identified",
                "implications": []
            }

        implications = []

        if mapping.change_type == "substantive":
            implications.append({
                "type": "substantive",
                "severity": "high",
                "description": mapping.change_summary,
                "legal_effect": "This change may affect the interpretation and application of the law. Existing precedents should be reviewed for continued applicability."
            })

        elif mapping.change_type == "procedural":
            implications.append({
                "type": "procedural",
                "severity": "medium",
                "description": mapping.change_summary,
                "legal_effect": "Procedural changes may affect how cases are filed and prosecuted."
            })

        elif mapping.change_type == "repealed":
            implications.append({
                "type": "repealed",
                "severity": "critical",
                "description": f"Section {mapping.ipc_section} has been repealed/decriminalized",
                "legal_effect": "This provision no longer exists in BNS. All precedents under this section are no longer applicable for criminal prosecution."
            })

        return {
            "has_substantive_changes": mapping.change_type in ["substantive", "repealed"],
            "summary": mapping.change_summary,
            "implications": implications
        }

    def _generate_validity_warnings(self, mapping, cases: List[Dict]) -> List[Dict[str, Any]]:
        """Generate warnings about precedent validity under BNS"""

        warnings = []

        # If section is repealed
        if mapping.change_type == "repealed":
            warnings.append({
                "level": "critical",
                "type": "section_repealed",
                "message": f"IPC Section {mapping.ipc_section} has been repealed. All precedents are no longer applicable for criminal prosecution.",
                "affected_cases": "all",
                "recommendation": "Do not rely on these precedents for criminal matters. They may have civil law implications only."
            })
            return warnings

        # If there are substantive changes
        if mapping.has_changes and mapping.change_type == "substantive":
            warnings.append({
                "level": "high",
                "type": "substantive_changes",
                "message": f"BNS Section {mapping.bns_section} contains substantive changes from IPC {mapping.ipc_section}",
                "details": mapping.change_summary,
                "recommendation": "Review each precedent for continued applicability. Elements of the offence may have changed."
            })

        # Check individual case validity status
        for case in cases:
            if case['validity_status'] == 'requires_review':
                warnings.append({
                    "level": "medium",
                    "type": "case_requires_review",
                    "case": case['case_name'],
                    "citation": case['citation'],
                    "message": f"Case requires review under BNS",
                    "reasoning": case.get('validity_reasoning', 'Legal framework has changed'),
                    "recommendation": "Verify that the legal reasoning in this case aligns with BNS provisions before citing."
                })

            elif case['validity_status'] == 'questionable':
                warnings.append({
                    "level": "medium",
                    "type": "questionable_validity",
                    "case": case['case_name'],
                    "citation": case['citation'],
                    "message": "Precedent validity is questionable under BNS",
                    "reasoning": case.get('validity_reasoning', ''),
                    "recommendation": "Use with caution and provide alternative authorities if possible."
                })

        return warnings

    def generate_legal_memo(self, ipc_sections: List[str],
                           query_context: str = "") -> str:
        """
        Generate comprehensive lawyer-style memo analyzing IPC to BNS transition

        Args:
            ipc_sections: List of IPC sections to analyze
            query_context: Optional context about the legal query

        Returns:
            Formatted legal memorandum as string
        """

        memo_sections = []

        # Header
        memo_sections.append("=" * 80)
        memo_sections.append("LEGAL MEMORANDUM")
        memo_sections.append("IPC to BNS Transition Analysis")
        memo_sections.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        memo_sections.append("=" * 80)
        memo_sections.append("")

        if query_context:
            memo_sections.append("RE: " + query_context)
            memo_sections.append("")

        # Executive Summary
        memo_sections.append("I. EXECUTIVE SUMMARY")
        memo_sections.append("-" * 80)
        memo_sections.append(f"This memorandum analyzes the transition from the Indian Penal Code (IPC)")
        memo_sections.append(f"to the Bhartiya Nyaya Sanhita (BNS) for the following sections:")
        memo_sections.append("")
        for section in ipc_sections:
            memo_sections.append(f"  • IPC Section {section}")
        memo_sections.append("")
        memo_sections.append("")

        # Detailed Analysis for each section
        all_warnings = []

        for section in ipc_sections:
            analysis = self.analyze_section_transition(section)

            if "error" in analysis:
                memo_sections.append(f"ERROR: {analysis['error']}")
                memo_sections.append("")
                continue

            memo_sections.append(f"II. ANALYSIS - IPC SECTION {section}")
            memo_sections.append("-" * 80)
            memo_sections.append("")

            # A. IPC Provision
            memo_sections.append(f"A. Indian Penal Code Section {section}")
            memo_sections.append(f"   Description: {analysis['ipc_description']}")
            memo_sections.append(f"   Category: {analysis['category']}")
            memo_sections.append(f"   Punishment: {analysis['punishment']}")
            memo_sections.append("")
            memo_sections.append(f"   Full Text:")
            memo_sections.append(f"   {analysis['ipc_text']}")
            memo_sections.append("")

            # B. BNS Equivalent
            memo_sections.append(f"B. Bhartiya Nyaya Sanhita Equivalent")
            if analysis['bns_section']:
                memo_sections.append(f"   Section: {analysis['bns_section']}")
                memo_sections.append(f"   Description: {analysis['bns_description']}")
                memo_sections.append("")
                memo_sections.append(f"   Full Text:")
                memo_sections.append(f"   {analysis['bns_text']}")
            else:
                memo_sections.append(f"   STATUS: REPEALED/NOT INCLUDED IN BNS")
            memo_sections.append("")

            # C. Doctrinal Changes
            memo_sections.append(f"C. Doctrinal Changes Analysis")
            change_analysis = analysis['change_analysis']

            if change_analysis['has_substantive_changes']:
                memo_sections.append(f"   ⚠️  SUBSTANTIVE CHANGES IDENTIFIED")
            else:
                memo_sections.append(f"   ✓ No substantive changes")

            memo_sections.append(f"   Change Type: {analysis['change_type'].upper()}")
            memo_sections.append(f"   Summary: {analysis['change_summary']}")
            memo_sections.append("")

            if change_analysis['implications']:
                memo_sections.append(f"   Legal Implications:")
                for impl in change_analysis['implications']:
                    memo_sections.append(f"   - [{impl['severity'].upper()}] {impl['description']}")
                    memo_sections.append(f"     Effect: {impl['legal_effect']}")
            memo_sections.append("")

            # D. Landmark Cases
            memo_sections.append(f"D. Relevant Precedents")
            if analysis['landmark_cases']:
                for case in analysis['landmark_cases']:
                    memo_sections.append(f"   • {case['case_name']}")
                    memo_sections.append(f"     Citation: {case['citation']}")
                    memo_sections.append(f"     Court: {case['court']} ({case['year']})")
                    memo_sections.append(f"     Ratio Decidendi: {case['ratio_decidendi'][:200]}...")
                    memo_sections.append(f"     Validity Status: {case['validity_status'].upper()}")
                    if case['validity_reasoning']:
                        memo_sections.append(f"     ⚠️  {case['validity_reasoning']}")
                    memo_sections.append("")
            else:
                memo_sections.append(f"   No landmark cases found in database for this section.")
                memo_sections.append("")

            # Collect warnings
            all_warnings.extend(analysis['validity_warnings'])

            memo_sections.append("")

        # III. Consolidated Validity Warnings
        memo_sections.append("III. VALIDITY WARNINGS FOR PRECEDENTS")
        memo_sections.append("=" * 80)
        memo_sections.append("")

        if all_warnings:
            # Group by severity
            critical = [w for w in all_warnings if w['level'] == 'critical']
            high = [w for w in all_warnings if w['level'] == 'high']
            medium = [w for w in all_warnings if w['level'] == 'medium']

            if critical:
                memo_sections.append("🚨 CRITICAL WARNINGS:")
                memo_sections.append("")
                for warning in critical:
                    memo_sections.append(f"   [{warning['type'].upper()}]")
                    memo_sections.append(f"   {warning['message']}")
                    if 'recommendation' in warning:
                        memo_sections.append(f"   Recommendation: {warning['recommendation']}")
                    memo_sections.append("")

            if high:
                memo_sections.append("⚠️  HIGH PRIORITY WARNINGS:")
                memo_sections.append("")
                for warning in high:
                    memo_sections.append(f"   [{warning['type'].upper()}]")
                    memo_sections.append(f"   {warning['message']}")
                    if 'details' in warning:
                        memo_sections.append(f"   Details: {warning['details']}")
                    if 'recommendation' in warning:
                        memo_sections.append(f"   Recommendation: {warning['recommendation']}")
                    memo_sections.append("")

            if medium:
                memo_sections.append("ℹ️  ADVISORY WARNINGS:")
                memo_sections.append("")
                for warning in medium:
                    memo_sections.append(f"   Case: {warning.get('case', 'N/A')}")
                    memo_sections.append(f"   {warning['message']}")
                    if 'reasoning' in warning:
                        memo_sections.append(f"   Reasoning: {warning['reasoning']}")
                    memo_sections.append("")
        else:
            memo_sections.append("✓ No validity warnings identified.")
            memo_sections.append("")

        # IV. Recommendations
        memo_sections.append("IV. RECOMMENDATIONS")
        memo_sections.append("=" * 80)
        memo_sections.append("")
        memo_sections.append("1. Review all cited precedents for continued applicability under BNS")
        memo_sections.append("2. For sections with substantive changes, conduct fresh legal research")
        memo_sections.append("3. Update case citations to reference BNS section numbers")
        memo_sections.append("4. Monitor emerging case law under BNS for new interpretations")
        memo_sections.append("5. Exercise caution when relying on precedents marked 'requires review'")
        memo_sections.append("")

        # Footer
        memo_sections.append("=" * 80)
        memo_sections.append("END OF MEMORANDUM")
        memo_sections.append("")
        memo_sections.append("DISCLAIMER: This memorandum is generated by an AI legal reasoning system")
        memo_sections.append("and should be reviewed by qualified legal professionals before reliance.")
        memo_sections.append("=" * 80)

        return "\n".join(memo_sections)
