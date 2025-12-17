from fpdf import FPDF
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
class ReportGenerator:
    def __init__(self, output_dir="customer_auditor/data/reports"):
        self.output_dir = output_dir
    def generate_pdf(self, audit_data, filename="audit_report.pdf"):
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Customer Support Audit Report", ln=True, align="C")
        
        # Score
        pdf.set_font("Arial", "B", 14)
        score = audit_data.get("score", "N/A")
        pdf.cell(0, 10, f"Overall Score: {score}/100", ln=True)
        
        # Breakdown
        pdf.set_font("Arial", "", 12)
        breakdown = audit_data.get("breakdown", {})
        for key, val in breakdown.items():
            pdf.cell(0, 10, f"{key.capitalize()}: {val}", ln=True)
            
        # Summary
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Summary:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, audit_data.get("summary", "No summary provided."))
        
        # Violations
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Violations Detected:", ln=True)
        pdf.set_font("Arial", "I", 11)
        pdf.set_text_color(255, 0, 0) # Red
        violations = audit_data.get("violations", [])
        if violations:
            for v in violations:
                pdf.cell(0, 10, f"- {v}", ln=True)
        else:
            pdf.set_text_color(0, 128, 0) # Green
            pdf.cell(0, 10, "None", ln=True)
            
        pdf.set_text_color(0, 0, 0) # Reset color
        
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)
        return filepath
    def send_email_alert(self, recipient_email, report_path, audit_summary):
        # MOCK IMPLEMENTATION - Printing to console as I don't have SMTP creds
        print(f"--- MOCK EMAIL SENDING ---")
        print(f"To: {recipient_email}")
        print(f"Subject: Compliance Alert - Low Score or Violation")
        print(f"Body: An audit flagged an interaction. See attached report.")
        print(f"Attachment: {report_path}")
        print(f"--------------------------")
        
        # Real implementation would be something like:
        # msg = MIMEMultipart()
        # msg['Subject'] = ...
        # ...
        # with smtplib.SMTP('smtp.gmail.com', 587) as server: ...
        
        return True