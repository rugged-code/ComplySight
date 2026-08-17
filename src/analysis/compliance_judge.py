import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.models.schemas import (ComplianceRequest, RerankedChunk, Judgment)

load_dotenv()


class ComplianceJudge:

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE API KEY not found")

        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL")

    def analyze(
        self,
        request: ComplianceRequest,
        evidence: list[RerankedChunk]
    ) -> Judgment:

        prompt = self._build_prompt(request, evidence)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Judgment,
            ),
        )

        return response.parsed

    def _build_prompt(
        self,
        request: ComplianceRequest,
        evidence: list[RerankedChunk]
    ) -> str:

        evidence_text = ""

        for i, chunk in enumerate(evidence, start=1):

            evidence_text += f"""
[EVIDENCE {i}]
Policy: {chunk.document}
Section: {chunk.section}
Title: {chunk.section_title}
Source: {chunk.source}

Content:
{chunk.text}

"""

        prompt = f"""
You are PolicyLens, a corporate policy compliance analyzer.

Your task is to determine whether an employee request complies
with the provided corporate policy evidence.

IMPORTANT RULES:

1. Use ONLY the provided policy evidence.
2. Do not use your general knowledge to invent policy requirements.
3. Do not invent policy sections, policy text, or sources.
4. Identify every policy requirement that applies to the request.
5. Determine whether each applicable requirement is satisfied.
6. Explicitly stated violations should be treated as violations.
7. Missing information should normally be treated as insufficient
   evidence rather than automatically assuming a violation.
8. Consider exceptions in the provided policy evidence when applicable.
9. Every evidence item in the final answer must come from the
   provided evidence.
10. Base the final verdict on the applicable requirements.

VERDICT DEFINITIONS:

COMPLIANT:
All applicable requirements are satisfied.

NON_COMPLIANT:
The request explicitly violates an applicable requirement.

PARTIALLY_COMPLIANT:
Some applicable requirements are satisfied while at least one
applicable requirement is violated.

INSUFFICIENT_EVIDENCE:
There is not enough information to determine whether one or more
applicable requirements are satisfied.

For every policy requirement:
- Set applicable=true if the requirement applies to the request.
- Set applicable=false if the requirement does not apply.
- Only evaluate satisfied when the requirement is applicable.
- A non-applicable requirement must not be treated as a violation.

EMPLOYEE REQUEST:

Employee: {request.employee}
Department: {request.department}

Request:
{request.request}

Reason:
{request.reason}

Additional Information:
{request.additional_information}


POLICY EVIDENCE:

{evidence_text}

Return a structured compliance judgment.
"""

        return prompt