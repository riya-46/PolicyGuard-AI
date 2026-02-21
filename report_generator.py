from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

def generate_pdf(df, filename="high_risk_report.pdf"):

    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("High Risk Transactions Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    data = [df.columns.tolist()] + df.head(500).values.tolist()

    table = Table(data)
    table.setStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black)
    ])

    elements.append(table)
    doc.build(elements)