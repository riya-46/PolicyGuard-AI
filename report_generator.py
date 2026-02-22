from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import io


def generate_pdf_report(df: pd.DataFrame):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]

    # Title
    elements.append(Paragraph("PolicyGuard AI - High Risk Transactions Report", title_style))
    elements.append(Spacer(1, 0.5 * inch))

    # Summary Section
    total_rows = len(df)
    total_violations = (df["Violated_Rule"] != "").sum()
    total_anomalies = df["Anomaly_Flag"].sum()

    summary_text = f"""
    Total Transactions: {total_rows} <br/>
    Total Rule Violations: {total_violations} <br/>
    Total Anomalies Detected: {total_anomalies}
    """

    elements.append(Paragraph(summary_text, styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    # Table Data (Top 50 rows for PDF readability)
    table_df = df.head(50)

    table_data = [table_df.columns.tolist()] + table_df.values.tolist()

    table = Table(table_data)

    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 6)
    ])

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)
    return buffer