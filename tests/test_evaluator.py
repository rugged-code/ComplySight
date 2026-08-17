from src.evaluation.evaluator import PolicyLensEvaluator


evaluator = PolicyLensEvaluator()

test_cases = evaluator.load_test_cases(
    "data/evaluation"
)

print(f"Total test cases: {len(test_cases)}")


# Test only the first case
test_case = test_cases[0]

print("\nTesting:", test_case["case_id"])
print("Expected:", test_case["expected_verdict"])


result = evaluator.evaluate_case(test_case)


print("Actual:", result["actual_verdict"])
print("Passed:", result["passed"])

print("\nRetrieved Sections:")

for chunk in result["retrieved_chunks"]:
    print(
        f"Section: {chunk.section} | "
        f"Score: {chunk.score if hasattr(chunk, 'score') else 'N/A'}"
    )


print("\nReranked Sections:")

for chunk in result["reranked_chunks"]:
    print(
        f"Section: {chunk.section} | "
        f"Rerank Score: {chunk.rerank_score}"
    )

print(
    "Expected relevant sections:",
    test_case["relevant_sections"]
)
print("\nRERANKED EVIDENCE SENT TO GEMINI:")

for chunk in result["reranked_chunks"]:
    print("\n" + "=" * 60)
    print(f"Section: {chunk.section}")
    print(f"Title: {chunk.section_title}")
    print(f"Score: {chunk.rerank_score}")
    print(f"Text:\n{chunk.text}")