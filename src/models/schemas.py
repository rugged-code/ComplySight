from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class Verdict(str, Enum):
    COMPLAINT = "COMPLAINT"
    NON_COMPLAINT = "NON_COMPLAINT"
    PARTIALLY_COMPLAINT = "PARTIALLY_COMPLAINT"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class ComplianceRequest(BaseModel):
    employee : str
    department : str
    request : str
    reason : str
    additional_information : str = ""

class Requirement(BaseModel):
    description: str
    section : str
    satified: bool

class Evidence(BaseModel):
    policy: str
    section: str
    content: str
    source: str

class Judgment(BaseModel):
    verdict: Verdict
    requirements: List[Requirement]
    violations: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    evidence : List[Evidence]
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
    section : str | None = None
    section_title : str
    page_start : int | None = None
    page_end : int | None = None

class RetrievedChunk(BaseModel):
    text : str
    document : str
    source : str
    section : str | None = None
    section_title : str | None = None
    page_start : int | None = None
    page_end : int  | None = None

    qdrant_score : float


class RerankedChunk(BaseModel):
    text : str
    document : str
    source : str
    section : str | None = None
    section_title : str | None = None
    page_start : int | None = None
    page_end : int  | None = None

    qdrant_score : float
    reranked_score : float