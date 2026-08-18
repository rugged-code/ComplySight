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
[EVIDENCE {i}] (relevance score: {chunk.rerank_score:.3f})
Policy: {chunk.document}
Section: {chunk.section}
Title: {chunk.section_title}
Source: {chunk.source}

Content:
{chunk.text}

"""

        prompt = f"""
You are PolicyLens, a corporate policy compliance analyzer.

Your task is to determine whether an employee request complies with
the provided corporate policy evidence.

IMPORTANT RULES:

1. Use ONLY the provided policy evidence.
2. Do not use general knowledge to invent policy requirements.
3. Do not invent policy sections, policy text, or sources.
4. Identify every policy requirement that applies to the request.
5. Evaluate EACH applicable requirement independently.
6. Explicitly stated violations must be marked NOT_SATISFIED.
7. Missing information must be marked INSUFFICIENT_EVIDENCE.
8. Do not assume missing information means a violation.
9. Consider exceptions in the provided policy evidence when applicable.
10. Every evidence item in the final answer must come from the provided
    policy evidence.
11. Do not evaluate unrelated policy requirements.
12. Do not let one uncertain requirement override another requirement
    whose status is clearly known.

REQUIREMENT STATUS:

For every applicable requirement, assign exactly ONE status:

SATISFIED:
The request and provided evidence clearly demonstrate that the
requirement has been fulfilled.

NOT_SATISFIED:
The request or provided evidence clearly demonstrates that the
requirement has been violated or not fulfilled.

INSUFFICIENT_EVIDENCE:
The requirement applies, but the provided request and evidence do not
contain enough information to determine whether it is satisfied or
violated.

NON-APPLICABLE:
The requirement does not apply to this request.

IMPORTANT:
Do NOT use INSUFFICIENT_EVIDENCE when the requirement is clearly
violated.

Do NOT use NOT_SATISFIED merely because information is missing.

DECISION LOGIC:

First determine which requirements actually apply.

Then evaluate EVERY applicable requirement independently.

Do NOT stop after finding the first uncertain requirement.

The final verdict must be determined using the following logic:

1. If the provided evidence does not contain any policy requirement
   relevant to the subject of the request:
   → IRRELEVANT

2. If at least one applicable requirement is NOT_SATISFIED and at least
   one other applicable requirement is SATISFIED:
   → PARTIALLY_COMPLIANT

3. If all applicable requirements are SATISFIED:
   → COMPLIANT

4. If all applicable requirements are NOT_SATISFIED:
   → NON_COMPLIANT

5. If there is no mixture of SATISFIED and NOT_SATISFIED requirements,
   but at least one applicable requirement has INSUFFICIENT_EVIDENCE:
   → INSUFFICIENT_EVIDENCE

6. If some requirements are NON-APPLICABLE, ignore them when determining
   the final verdict.

CRITICAL PARTIAL-COMPLIANCE RULE:

PARTIALLY_COMPLIANT means that the request clearly satisfies some
applicable requirements and clearly fails some other applicable
requirements.

Example:

Requirement A → SATISFIED
Requirement B → NOT_SATISFIED
Requirement C → NON-APPLICABLE

Final verdict → PARTIALLY_COMPLIANT

Another example:

Requirement A → SATISFIED
Requirement B → NOT_SATISFIED
Requirement C → INSUFFICIENT_EVIDENCE

Final verdict → PARTIALLY_COMPLIANT

The existence of INSUFFICIENT_EVIDENCE does NOT override a clear
mixture of SATISFIED and NOT_SATISFIED requirements.

However:

Requirement A → SATISFIED
Requirement B → INSUFFICIENT_EVIDENCE

Final verdict → INSUFFICIENT_EVIDENCE

And:

Requirement A → NOT_SATISFIED
Requirement B → INSUFFICIENT_EVIDENCE

Final verdict → INSUFFICIENT_EVIDENCE

IRRELEVANT RULE:

Use IRRELEVANT only when the provided policy evidence does not contain
a policy requirement addressing the subject of the employee request.

For example:

Employee request → database access
Provided evidence → expense reimbursement policy only

Final verdict → IRRELEVANT

Do NOT use IRRELEVANT simply because the evidence is incomplete.

EVIDENCE RULES:

For every requirement marked SATISFIED, NOT_SATISFIED, or
INSUFFICIENT_EVIDENCE, provide the relevant evidence items that support
that determination.

Every evidence item must come directly from the provided evidence.

Do not invent evidence.

Do not use evidence from an unrelated policy merely because it contains
similar words.

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