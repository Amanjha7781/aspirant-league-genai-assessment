"""Generate the clearly synthetic invoice PDF fixtures used for evaluation."""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


ROOT = Path(__file__).parent
SAMPLES = [
    {"file":"invoice_01.pdf","layout":"classic", "vendor":"Northstar Labs", "invoice_id":"NS-1042", "date":"2026-01-14", "currency":"USD", "subtotal":"240.00", "tax":"19.20", "total":"259.20"},
    {"file":"invoice_02.pdf","layout":"compact", "vendor":"Blue Oak Studio", "invoice_id":"BO-008", "date":"14/02/2026", "currency":"USD", "subtotal":"1,250.00", "tax":"100.00", "total":"1,350.00"},
    {"file":"invoice_03.pdf","layout":"euro", "vendor":"Atelier Lumiere", "invoice_id":"AL/77", "date":"03 Mar 2026", "currency":"EUR", "subtotal":"150.00", "tax":"24.60", "total":"174.60"},
    {"file":"invoice_04.pdf","layout":"simple", "vendor":"Cedar Works", "invoice_id":"CW-502", "date":"2026-04-05", "currency":"USD", "subtotal":"80.00", "tax":None, "total":"80.00"},
    {"file":"invoice_05.pdf","layout":"ambiguous_date", "vendor":"Maple Consulting", "invoice_id":"MC-19", "date":None, "currency":"USD", "subtotal":"500.00", "tax":"40.00", "total":"540.00"},
    {"file":"invoice_06.pdf","layout":"address", "vendor":None, "invoice_id":"RIVER-3001", "date":"2026-06-21", "currency":"CAD", "subtotal":"90.00", "tax":"11.70", "total":"101.70"},
    {"file":"invoice_07.pdf","layout":"amount_due", "vendor":"Sunrise Print Shop", "invoice_id":"SP-771", "date":"July 9, 2026", "currency":"USD", "subtotal":"320.00", "tax":"25.60", "total":"345.60"},
    {"file":"invoice_08.pdf","layout":"multiline", "vendor":"Juniper Data Services", "invoice_id":"JDS-8802", "date":"2026-08-12", "currency":"USD", "subtotal":"2,000.00", "tax":"160.00", "total":"2,160.00"},
    {"file":"invoice_09.pdf","layout":"table", "vendor":"Silverline Office Co.", "invoice_id":"SO-915", "date":"09/10/2026", "currency":"INR", "subtotal":"INR 7,500.00", "tax":"INR 1,350.00", "total":"INR 8,850.00"},
    {"file":"invoice_10.pdf","layout":"incomplete", "vendor":"Orchid Events", "invoice_id":"OE-410", "date":"2026-11-02", "currency":"USD", "subtotal":"700.00", "tax":"56.00", "total":None},
]


def invoice_lines(sample: dict) -> list[str]:
    vendor = sample["vendor"]
    vendor_line = vendor or "[Vendor name omitted]"
    def label(name: str, value: str | None) -> str:
        return f"{name}: {value}" if value is not None else f"{name}: [not stated]"
    layout = sample["layout"]
    if layout == "classic":
        return ["SYNTHETIC INVOICE", vendor_line, label("Invoice Number", sample['invoice_id']), label("Invoice Date", sample['date']), label("Currency", sample['currency']), label("Subtotal", sample['subtotal']), label("Tax", sample['tax']), label("Total", sample['total'])]
    if layout == "compact":
        return ["SYNTHETIC BILLING STATEMENT", f"{vendor_line}       INV {sample['invoice_id']}", f"Issued {sample['date']}       Currency {sample['currency']}", f"Net amount {sample['subtotal']}", f"Tax amount {sample['tax']}", f"Amount due {sample['total']}"]
    if layout == "euro":
        return ["FACTURE - SYNTHETIC", vendor_line, f"Reference {sample['invoice_id']}", f"Date de facture {sample['date']}", f"Devise {sample['currency']}", f"Net {sample['subtotal']}", f"Tax {sample['tax']}", f"Total {sample['total']}"]
    if layout == "simple":
        return ["INVOICE (SYNTHETIC)", vendor_line, f"No. {sample['invoice_id']}    Date {sample['date']}", f"{sample['currency']} {sample['subtotal']} before tax", "Tax not listed", f"Balance due {sample['total']}"]
    if layout == "ambiguous_date":
        return ["SYNTHETIC INVOICE", vendor_line, f"Invoice ID {sample['invoice_id']}", "Date: 03/04/2026", "Printed: 04/03/2026", f"Currency {sample['currency']}", f"Subtotal {sample['subtotal']}", f"Tax {sample['tax']}", f"Total {sample['total']}"]
    if layout == "address":
        return ["INVOICE / SYNTHETIC SAMPLE", "Bill-to: Example Customer", "100 Fictional Road", "Invoice ref", sample['invoice_id'], "Date issued", sample['date'], f"Currency: {sample['currency']}", f"Subtotal: {sample['subtotal']}", f"Tax: {sample['tax']}", f"Invoice total: {sample['total']}"]
    if layout == "amount_due":
        return ["SYNTHETIC SALES INVOICE", vendor_line, f"Invoice {sample['invoice_id']}", f"Date {sample['date']}", f"Currency {sample['currency']}", f"Subtotal {sample['subtotal']}", f"Tax {sample['tax']}", f"AMOUNT DUE: {sample['total']}"]
    if layout == "multiline":
        return ["SYNTHETIC INVOICE", vendor_line, "Service period: August 2026", f"Invoice identifier: {sample['invoice_id']}", f"Invoice date: {sample['date']}", f"Currency: {sample['currency']}", "Description                 Amount", "Data support services       2,000.00", f"Subtotal                    {sample['subtotal']}", f"Tax                         {sample['tax']}", f"Total payable               {sample['total']}"]
    if layout == "table":
        return ["SYNTHETIC TAX INVOICE", vendor_line, f"Invoice No. {sample['invoice_id']}", f"Date {sample['date']}", "Currency INR", "Description | Qty | Line value", "Office supplies | 3 | INR 7,500.00", f"Subtotal | {sample['subtotal']}", f"GST | {sample['tax']}", f"Grand Total | {sample['total']}"]
    return ["SYNTHETIC INVOICE", vendor_line, f"Invoice {sample['invoice_id']}", f"Date {sample['date']}", f"Currency {sample['currency']}", f"Subtotal {sample['subtotal']}", f"Tax {sample['tax']}", "Total: [not stated]"]


def generate() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for sample in SAMPLES:
        path = ROOT / sample["file"]
        pdf = canvas.Canvas(str(path), pagesize=letter)
        pdf.setTitle("Synthetic invoice fixture")
        pdf.setFont("Helvetica", 11)
        y = 740
        for line in invoice_lines(sample):
            pdf.drawString(60, y, line)
            y -= 28
        pdf.save()
        print(f"created {path.name}")


if __name__ == "__main__":
    generate()
