from src.retrieval.query_builder import build_retrieval_query
from src.retrieval.retriever import PolicyRetriever
from src.retrieval.reranker import JinaReranker
from src.analysis.compliance_judge import ComplianceJudge

from src.models.schemas import ComplianceRequest, Judgment

class PolicyLensPipeline:

    def __init__(self):
        self.retriever = PolicyRetriever(top_k=30)
        self.reranker = JinaReranker()
        self.judge = ComplianceJudge()

    def run(self, requests: ComplianceRequest) -> Judgment:

        query = build_retrieval_query(requests)

        retrieved_chunks = self.retriever.retrieve(query)

        reranked_chunks = self.reranker.rerank(query, retrieved_chunks, top_n = 8)

        judgement = self.judge.analyze(request = requests, evidence=reranked_chunks, query=query, reranker = self.reranker)

        return judgement    
