import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.models.schemas import (
    AnalysisResult,
    ComplianceRequest,
    Evidence,
    Judgment,
    RelevanceDecision,
    Requirement,
    RequirementStatus,
    RerankedChunk,
    Verdict,
)


load_dotenv()


def compute_verdict(
    is_relevant: bool,
    requirements: list[Requirement],
) -> Verdict:
    """
    Deterministic verdict calculation.

    Gemini evaluates obligations. Python determines the final verdict.
    """

    if not is_relevant:
        return Verdict.IRRELEVANT

    # Relevant policy exists, but no assessable policy obligation was found.
    # This is lack of usable evidence, not an irrelevant request.
    if not requirements:
        return Verdict.INSUFFICIENT_EVIDENCE

    statuses = {requirement.status for requirement in requirements}

    has_satisfied = RequirementStatus.SATISFIED in statuses
    has_not_satisfied = RequirementStatus.NOT_SATISFIED in statuses
    has_insufficient = (
        RequirementStatus.INSUFFICIENT_EVIDENCE in statuses
    )

    # This only represents genuinely independent obligations.
    if has_satisfied and has_not_satisfied:
        return Verdict.PARTIALLY_COMPLIANT

    # Preserve the test-set semantics from your existing decision tree:
    # uncertainty prevents a definitive COMPLIANT or NON_COMPLIANT result.
    if has_insufficient:
        return Verdict.INSUFFICIENT_EVIDENCE

    if statuses == {RequirementStatus.SATISFIED}:
        return Verdict.COMPLIANT

    if statuses == {RequirementStatus.NOT_SATISFIED}:
        return Verdict.NON_COMPLIANT

    return Verdict.INSUFFICIENT_EVIDENCE


class ComplianceJudge:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env")

        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL")

        if not self.model:
            raise ValueError("GEMINI_MODEL not found in .env")

    def analyze(
        self,
        request: ComplianceRequest,
        evidence: list[RerankedChunk],
    ) -> Judgment:
        evidence_text, valid_evidence_ids = self._format_evidence(evidence)

        relevance = self._classify_relevance(
            request=request,
            evidence_text=evidence_text,
        )

        # Do not allow a relevance claim without a citation to supplied text.
        relevance.governing_evidence_ids = [
            evidence_id
            for evidence_id in relevance.governing_evidence_ids
            if evidence_id in valid_evidence_ids
        ]

        if relevance.is_relevant and not relevance.governing_evidence_ids:
            relevance = RelevanceDecision(
                is_relevant=False,
                governing_evidence_ids=[],
                rationale=(
                    "The relevance classifier did not cite a supplied policy "
                    "section that governs this request."
                ),
            )

        if not relevance.is_relevant:
            return Judgment(
                verdict=Verdict.IRRELEVANT,
                relevance=relevance,
                requirements=[],
                violations=[],
                missing_evidence=[],
                evidence=[],
                explanation=relevance.rationale,
            )

        analysis = self._analyze_requirements(
            request=request,
            evidence_text=evidence_text,
        )

        # Keep only valid evidence citations.
        for requirement in analysis.requirements:
            requirement.evidence_ids = [
                evidence_id
                for evidence_id in requirement.evidence_ids
                if evidence_id in valid_evidence_ids
            ]

        analysis.evidence = [
            item
            for item in analysis.evidence
            if item.evidence_id in valid_evidence_ids
        ]

        verdict = compute_verdict(
            is_relevant=True,
            requirements=analysis.requirements,
        )

        return Judgment(
            verdict=verdict,
            relevance=relevance,
            requirements=analysis.requirements,
            violations=analysis.violations,
            missing_evidence=analysis.missing_evidence,
            evidence=analysis.evidence,
            explanation=analysis.explanation,
        )

    def _classify_relevance(
        self,
        request: ComplianceRequest,
        evidence_text: str,
    ) -> RelevanceDecision:
        prompt = f"""
You are a policy-evidence relevance classifier.

Your only task is to decide whether at least one supplied evidence item
contains a corporate-policy obligation that governs the SUBJECT of the
employee request.

Use only the supplied evidence.

RELEVANT:
At least one evidence item contains a policy obligation applicable to
the request's subject, even if the request lacks enough facts to assess
compliance.

IRRELEVANT:
No supplied evidence governs the request's subject.

Shared words do not establish relevance. For example, expense policy
that mentions "approval" is irrelevant to an access-control request.

If RELEVANT, cite one or more governing evidence IDs.
If IRRELEVANT, governing_evidence_ids must be empty.

EMPLOYEE REQUEST
Employee: {request.employee}
Department: {request.department}
Request: {request.request}
Reason: {request.reason}
Additional information: {request.additional_information}

SUPPLIED POLICY EVIDENCE
{evidence_text}
""".strip()

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RelevanceDecision,
            ),
        )

        if response.parsed is None:
            raise ValueError("Gemini returned no structured relevance result")

        return response.parsed

    def _analyze_requirements(
        self,
        request: ComplianceRequest,
        evidence_text: str,
    ) -> AnalysisResult:
        prompt = f"""
You are PolicyLens, a corporate policy compliance analyst.

Use only the supplied policy evidence and employee request.

Identify each applicable, independent POLICY OBLIGATION and evaluate it.

A policy obligation is one enforceable policy rule.

CRITICAL RULE:
Do not split mandatory conditions within a single policy rule into
separate requirements.

For example:

"MFA and manager approval are required for privileged access."

This is ONE requirement. If manager approval is absent, the one
requirement is NOT_SATISFIED. Do not create a SATISFIED "MFA" requirement
and a NOT_SATISFIED "approval" requirement.

Split requirements only when the policy contains genuinely independent
obligations that could independently be complied with or violated.

Assign exactly one status to every requirement:

SATISFIED:
The request clearly demonstrates the obligation is fulfilled.

NOT_SATISFIED:
The request explicitly demonstrates the obligation is violated or
unfulfilled.

INSUFFICIENT_EVIDENCE:
The policy applies, but the request lacks enough information to decide
whether the obligation is fulfilled or violated.

Rules:
- Missing information is not a violation.
- Do not invent policy text, sections, requirements, or facts.
- Cite supplied evidence IDs for every requirement.
- Do not use an unrelated policy merely because it shares words.
- Do not decide the final verdict. Python will calculate it.
- Return only applicable obligations.

EMPLOYEE REQUEST
Employee: {request.employee}
Department: {request.department}
Request: {request.request}
Reason: {request.reason}
Additional information: {request.additional_information}

SUPPLIED POLICY EVIDENCE
{evidence_text}
""".strip()

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalysisResult,
            ),
        )

        if response.parsed is None:
            raise ValueError("Gemini returned no structured analysis result")

        return response.parsed

    @staticmethod
    def _format_evidence(
        evidence: list[RerankedChunk],
    ) -> tuple[str, set[str]]:
        blocks: list[str] = []
        evidence_ids: set[str] = set()

        for index, chunk in enumerate(evidence, start=1):
            evidence_id = f"E{index}"
            evidence_ids.add(evidence_id)

            blocks.append(
                f"""
[EVIDENCE_ID: {evidence_id}]
Reranker score: {chunk.rerank_score:.3f}
Policy: {chunk.document}
Section: {chunk.section}
Title: {chunk.section_title}
Source: {chunk.source}

Content:
{chunk.text}
""".strip()
            )

        return "\n\n".join(blocks), evidence_ids