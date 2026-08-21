import os
import time

from dotenv import find_dotenv, load_dotenv
from google import genai
from google.genai import types

from src.ingestion.qdrant_store import QdrantStore
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


load_dotenv(find_dotenv())


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
        load_dotenv(find_dotenv())
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            from pathlib import Path

            env_path = Path(__file__).resolve().parent.parent.parent / ".env"
            if env_path.exists():
                load_dotenv(env_path)
                api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env")

        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )

        self.store = QdrantStore()

    def _generate_structured(
        self,
        prompt: str,
        schema,
        max_retries: int = 5,
    ):
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                    ),
                )

                if response.parsed is not None:
                    time.sleep(1.0)
                    return response.parsed

            except Exception as exc:
                if attempt == max_retries - 1:
                    raise exc

                err_str = str(exc)

                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    time.sleep(15.0)
                else:
                    time.sleep(2.0 * (attempt + 1))

        raise ValueError("Failed to get structured output from model")

    def analyze(
        self,
        request: ComplianceRequest,
        evidence: list[RerankedChunk],
        query: str | None = None,
        reranker=None,
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

        # Scoped document expansion after relevance is confirmed.
        id_to_chunk = {
            f"E{i}": chunk
            for i, chunk in enumerate(evidence, start=1)
        }

        governing_docs = {
            id_to_chunk[evidence_id].document
            for evidence_id in relevance.governing_evidence_ids
            if evidence_id in id_to_chunk
        }

        expanded = list(evidence)
        seen = {
            (chunk.document, chunk.section)
            for chunk in evidence
        }

        for doc_name in governing_docs:
            for point in self.store.get_chunks_by_document(doc_name):
                payload = point.payload

                key = (
                    payload["document"],
                    payload.get("section"),
                )

                if key in seen:
                    continue

                seen.add(key)

                expanded.append(
                    RerankedChunk(
                        text=payload["text"],
                        document=payload["document"],
                        source=payload["source"],
                        section=payload.get("section"),
                        section_title=payload.get("section_title"),
                        page_start=payload.get("page_start"),
                        page_end=payload.get("page_end"),
                        qdrant_score=0.0,
                        rerank_score=0.0,
                    )
                )

        evidence_text, valid_evidence_ids = self._format_evidence(
            expanded
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
You are a policy relevance classifier for a corporate compliance system.

YOUR TASK:
Determine whether any supplied policy evidence contains rules, standards, limits, or approval obligations governing the SUBJECT of the employee's request.

RELEVANCE RULES:
1. SUBJECT MATTER GOVERNANCE: If the supplied policy governs the topic or activity in the request (e.g. expense reimbursement, business meals, vendor contracts, software subscriptions, access control, hardware usage, incident reporting, remote work), mark is_relevant = true and cite the governing evidence ID(s).
2. INCOMPLETE REQUESTS / INQUIRIES ON POLICY TOPICS: Even if the request is an inquiry or lacks full receipt/approval details, if it concerns a topic governed by a supplied policy (e.g. asking about dinner limits or software renewals), mark is_relevant = true. The compliance evaluation stage will handle missing evidence.
3. OUT OF SCOPE TOPICS: Mark is_relevant = false only if the subject of the request has no governing policy among the supplied documents (e.g., charity event t-shirt logos, ergonomic chair discount codes, pets in the office).
4. IMPLICIT DATA TYPES: Social media handles, email addresses, phone numbers, and lead generation forms constitute Personally Identifiable Information (PII) governed by Data Protection Policy.
5. CLOUD & IT INFRASTRUCTURE: Cloud storage provisioning, resource allocation, and data classification requests are governed by Information Security Policy.
6. SHARED WORDS: Shared generic words (like "approval" or "portal") do not establish relevance if the subject matter is unrelated.

If RELEVANT, cite the governing evidence IDs.
If IRRELEVANT, governing_evidence_ids must be empty.

EMPLOYEE REQUEST:
Employee: {request.employee}
Department: {request.department}
Request: {request.request}
Reason: {request.reason}
Additional information: {request.additional_information}

SUPPLIED POLICY EVIDENCE:
{evidence_text}
""".strip()

        return self._generate_structured(
            prompt,
            RelevanceDecision,
        )

    def _analyze_requirements(
        self,
        request: ComplianceRequest,
        evidence_text: str,
    ) -> AnalysisResult:
        prompt = f"""
You are PolicyLens, an expert corporate compliance analyst.

Analyze the employee request against the supplied policy evidence.

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

Requirement Scope:
- For requests involving a prohibited action, unallowable expense, or
  policy violation (e.g. alcohol reimbursement, browser password saving,
  personal hardware usage, 60-day account expiration, contract over
  threshold lacking executive approval, unencrypted PII transfer):
  Focus strictly on the specific policy rule/section governing that item
  or action and mark it NOT_SATISFIED.

- Do NOT extract baseline administrative sections such as general
  employee eligibility, standard password length, routine receipt
  attachments, or lower-level approvals as satisfied checkmarks when
  they are not relevant to the actual violation.

- For incomplete requests lacking critical verification data (e.g. hotel
  expense without destination city, remote work without internet speed
  details, legacy exception without security approval):
  Evaluate the requirement as INSUFFICIENT_EVIDENCE.

- For legitimate multi-step operational workflows (e.g. BYOD
  registration and MDM profile installation; incident response team
  assembly and communication channel; absence notification channel and
  notification timing; access request portal ticket and manager approval):
  Extract the distinct operational conditions and evaluate each
  separately.

Assign exactly one status to every requirement:

SATISFIED:
The request clearly demonstrates the obligation is fulfilled.

NOT_SATISFIED:
The request explicitly demonstrates the obligation is violated or
unfulfilled.

INSUFFICIENT_EVIDENCE:
The policy applies, but the request lacks enough information to decide
whether the obligation is fulfilled or violated.

Status Definitions:
- SATISFIED: Documented evidence that the required condition, approval,
  or step is fulfilled.
- NOT_SATISFIED: The request explicitly violates or fails to meet a
  mandatory policy rule, limit, or restriction.
- INSUFFICIENT_EVIDENCE: The policy applies, but the request lacks
  information to verify whether the requirement is fulfilled.

Rules:
- Missing information is not a violation; mark it INSUFFICIENT_EVIDENCE.
- Cite supplied evidence IDs (E1, E2, etc.) for each requirement.
- Base analysis strictly on the supplied policy evidence and request
  details.

EMPLOYEE REQUEST:
Employee: {request.employee}
Department: {request.department}
Request: {request.request}
Reason: {request.reason}
Additional information: {request.additional_information}

SUPPLIED POLICY EVIDENCE:
{evidence_text}
""".strip()

        return self._generate_structured(
            prompt,
            AnalysisResult,
        )

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
