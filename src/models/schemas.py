from enum import Enum

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    IRRELEVANT = "IRRELEVANT"


class RequirementStatus(str, Enum):
    SATISFIED = "SATISFIED"
    NOT_SATISFIED = "NOT_SATISFIED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class ComplianceRequest(BaseModel):
    employee: str
    department: str
    request: str
    reason: str
    additional_information: str = ""


class Evidence(BaseModel):
    evidence_id: str
    policy: str
    section: str | None = None
    content: str
    source: str


class Requirement(BaseModel):
    """
    One independent policy obligation.

    Do not represent every internal condition of one policy rule as a
    separate Requirement. For example:
    "MFA and manager approval are required" is one obligation.
    """

    description: str
    section: str | None = None
    status: RequirementStatus
    evidence_ids: list[str] = Field(default_factory=list)
    rationale: str


class RelevanceDecision(BaseModel):
    is_relevant: bool
    governing_evidence_ids: list[str] = Field(default_factory=list)
    rationale: str


class AnalysisResult(BaseModel):
    """
    Gemini returns this model after policy relevance has already passed.
    Gemini does not decide the final verdict.
    """

    requirements: list[Requirement] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    explanation: str


class Judgment(BaseModel):
    """
    Final application result. The Python code calculates `verdict`.
    """

    verdict: Verdict
    relevance: RelevanceDecision
    requirements: list[Requirement] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    explanation: str


class ParsedSection(BaseModel):
    title: str
    number: str | None = None
    content: str
    page_start: int | None = None
    page_end: int | None = None


class ParsedDocument(BaseModel):
    title: str
    source: str
    file_type: str
    sections: list[ParsedSection]


class DocumentChunk(BaseModel):
    text: str
    document: str
    source: str
    section: str | None = None
    section_title: str | None = None
    page_start: int | None = None
    page_end: int | None = None


class RetrievedChunk(BaseModel):
    text: str
    document: str
    source: str
    section: str | None = None
    section_title: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    qdrant_score: float


class RerankedChunk(BaseModel):
    text: str
    document: str
    source: str
    section: str | None = None
    section_title: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    qdrant_score: float
    rerank_score: float