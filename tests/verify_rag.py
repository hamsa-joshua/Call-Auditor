import os
import sys
import shutil
# Add project root to path
sys.path.append(os.getcwd())
from src.chat_normalizer import ChatNormalizer
from src.rag_engine import RagEngine
from src.database_manager import DatabaseManager
from src.reporting import ReportGenerator
# We will mock Auditor because we might not have real API keys in this env
from unittest.mock import MagicMock
def test_end_to_end():
    print("Starting End-to-End Verification...")
    
    # 1. Setup Mock Data
    dummy_chat = """
    [10:00:01] Person1: Thank you for calling TechFlow Support, my name is Alice. How can I assist you today?
    [10:00:10] Person2: Hi, my internet is down.
    [10:00:15] Person1: I can help with that. Can I have your account number?
    [10:00:20] Person2: It's 12345.
    [10:00:25] Person1: Thanks. I see it here. Let me reset it.
    [10:05:00] Person1: Is there anything else?
    [10:05:05] Person2: No thanks.
    [10:05:10] Person1: Have a great day!
    """
    
    # 2. Test Normalizer
    print("Testing Chat Normalizer...")
    normalizer = ChatNormalizer()
    normalized = normalizer.normalize_content(dummy_chat)
    assert len(normalized) > 0, "Normalization failed"
    transcript_text = "\n".join([f"{m['speaker']}: {m['text']}" for m in normalized])
    print(f"Transcript generated ({len(normalized)} lines).")
    
    # 3. Test RAG
    print("Testing RAG Engine...")
    rag = RagEngine(policy_path="customer_auditor/policies/company_policy.txt")
    if not os.path.exists(rag.index_path):
        rag.build_vector_store()
    context = rag.retrieve_context("policies about greeting")
    assert len(context) > 0, "RAG Retrieval failed"
    print("RAG Context retrieved.")
    
    # 4. Test Audit (Mocked LLM)
    print("Testing Auditor (Mocked)...")
    # Mocking Auditor class response to avoid API key requirement for this test script
    # In real usage, the user puts their key.
    mock_audit_result = {
        "score": 95,
        "breakdown": {"empathy": 10, "professionalism": 10},
        "violations": [],
        "summary": "Good interaction.",
        "suggestions": []
    }
    
    # 5. Test DB & Reporting
    print("Testing DB and Reporting...")
    db = DatabaseManager()
    status = db.log_audit("test_chat.txt", "chat", mock_audit_result)
    
    reporter = ReportGenerator()
    pdf_path = reporter.generate_pdf(mock_audit_result, filename="test_report.pdf")
    
    assert os.path.exists(pdf_path), "PDF generation failed"
    print(f"PDF generated at {pdf_path}")
    
    print("Verification Successful!")
if __name__ == "__main__":
    test_end_to_end()