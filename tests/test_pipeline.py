from src.pipeline import PolicyLensPipeline
from src.models.schemas import ComplianceRequest


pipeline = PolicyLensPipeline()


test_cases = [

    {
        "id": "COMPLIANT",
        "expected": "COMPLIANT",
        "request": ComplianceRequest(
            employee="Rahul Sharma",
            department="Engineering",
            request="I need database administrator access to the production SQL server. I have attached the documented approvals from my direct manager, Sarah Jenkins, and the Director of Information Security, Mark Vance. Please provision this access to my dedicated administrative account, 'rsharma-admin'.",
            reason="Requesting elevated system permissions for database management.",
            additional_information=""
        )
    },

    {
        "id": "PARTIALLY_COMPLIANT",
        "expected": "PARTIALLY_COMPLIANT",
        "request": ComplianceRequest(
            employee="David Kim",
            department="Engineering",
            request="I want to work remotely while taking care of my 2-year-old child during working hours. My remote work arrangement has been approved by my manager and HRBP. I have a dedicated workspace, VPN access, and a 100 Mbps internet connection.",
            reason="Requesting remote work while acting as the primary caregiver.",
            additional_information=""
        )
    },

    {
        "id": "NON_COMPLIANT",
        "expected": "NON_COMPLIANT",
        "request": ComplianceRequest(
            employee="Test Employee",
            department="Engineering",
            request="I want to access corporate data from my personal laptop without using company-issued hardware.",
            reason="I prefer using my personal device.",
            additional_information=""
        )
    },

    {
        "id": "INSUFFICIENT_EVIDENCE",
        "expected": "INSUFFICIENT_EVIDENCE",
        "request": ComplianceRequest(
            employee="Test Employee",
            department="Engineering",
            request="I need access to a legacy system that only supports TLS 1.1.",
            reason="The system cannot currently support TLS 1.2.",
            additional_information="The system is isolated on an internal network."
        )
    },

    {
        "id": "IRRELEVANT",
        "expected": "IRRELEVANT",
        "request": ComplianceRequest(
            employee="Test Employee",
            department="Finance",
            request="I need reimbursement for a business dinner.",
            reason="Client entertainment expense.",
            additional_information=""
        )
    }
]


for case in test_cases:

    print("=" * 60)
    print(f"Testing: {case['id']}")
    print(f"Expected: {case['expected']}")

    try:
        result = pipeline.run(case["request"])

        actual = result.verdict.value

        print(f"Actual:   {actual}")

        if actual == case["expected"]:
            print("Result:   PASS")
        else:
            print("Result:   FAIL")

        print(f"Explanation: {result.explanation}")

    except Exception as e:
        print(f"ERROR: {e}")

    print()