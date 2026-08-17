from src.models.schemas import ComplianceRequest

def build_retrieval_query(request: ComplianceRequest) ->str:
    return f"""
Request:
{request.request}

Reason:
{request.reason}

Department:
{request.department} 

Additional Information:
{request.additional_information}
""".strip()