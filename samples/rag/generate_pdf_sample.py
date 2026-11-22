"""Generate a small synthetic PDF source for the Problem 1 upload demonstration."""
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


path = Path(__file__).with_name("emergency_procedure.pdf")
pdf = canvas.Canvas(str(path), pagesize=letter)
pdf.setTitle("Synthetic emergency procedure")
pdf.setFont("Helvetica-Bold", 16)
pdf.drawString(60, 735, "EMERGENCY PROCEDURE (SYNTHETIC SAMPLE)")
pdf.setFont("Helvetica", 11)
pdf.drawString(60, 690, "Power outage")
pdf.drawString(60, 665, "During staffed hours, report a building power outage to the facilities desk using internal extension 400.")
pdf.drawString(60, 640, "The sample does not provide an after-hours emergency contact number.")
pdf.save()
print(f"created {path.name}")
