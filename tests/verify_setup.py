import sys
from unittest.mock import MagicMock
# MOCKING HEAVY DEPENDENCIES BEFORE IMPORTS
sys.modules["langchain"] = MagicMock()
sys.modules["langchain.text_splitter"] = MagicMock()
sys.modules["langchain_community"] = MagicMock()
sys.modules["langchain_community.vectorstores"] = MagicMock()
sys.modules["langchain_community.embeddings"] = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["whisper"] = MagicMock()
sys.modules["senko"] = MagicMock()
sys.modules["faiss"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["fpdf"] = MagicMock()
sys.modules["pandas"] = MagicMock()
# Now import project modules
import os
import json
sys.path.append(os.getcwd())
from src.chat_normalizer import ChatNormalizer
from src.database_manager import DatabaseManager
from src.reporting import ReportGenerator
# We can't easily import RagEngine or Auditor because they inherit from mocks or use them in __init__
# So we mock them for the flow test, or we instantiated them carefully.
# Let's test the independent components and the DB/Reporting integration.
def test_mocked_flow():
    print("Starting Mocked Verification...")
    
    # 1. Chat Normalizer (Pure Python, no heavy deps)
    print("Testing Chat Normalizer...")
    chat_log = """
    PersonA: Hello
    PersonB: Hi there
    """
    normalizer = ChatNormalizer()
    norm = normalizer.normalize_content(chat_log)
    assert len(norm) == 2
    print("Chat Normalizer passed.")
    
    # 2. Database Manager (SQLite)
    print("Testing Database Manager...")
    test_db_path = "test_audits.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        
    db = DatabaseManager(test_db_path) # Use file for persistence test
    mock_result = {
        "score": 80, 
        "violations": ["Test Violation"], 
        "summary": "Test Summary"
    }
    status = db.log_audit("test_file.txt", "chat", mock_result)
    rows = db.get_all_audits()
    assert len(rows) == 1
    assert rows[0]['status'] == "Flagged"
    print("Database Manager passed.")
    
    # Clean up DB
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # 3. Report Generator (FPDF)
    # FPDF is lightweight, assume it's installed or we mocked it?
    # Actually FPDF might not be installed if the big install is still running.
    # We will try to import it, if fail, we mock it too just to verify the class logic structure?
    # No, ReportGenerator uses    print("Testing Report Generator...")
    reporter = ReportGenerator(output_dir=".")
    # If FPDF is mocked, this won't actually write a file, but runs the code path.
    path = reporter.generate_pdf(mock_result, "test_mock.pdf")
    print(f"Report Generation path: {path}")
    
    print("Mocked Verification Successful!")
if __name__ == "__main__":
    test_mocked_flow()