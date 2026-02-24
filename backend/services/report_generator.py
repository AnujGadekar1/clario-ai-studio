# Path: intelligent_summarizer/backend/services/report_generator.py

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import datetime
import os


def generate_pdf_report(data: dict, filename="analysis_report.pdf"):

    file_path = os.path.join("generated_reports", filename)
    os.makedirs("generated_reports", exist_ok=True)

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    # Title
    elements.append(Paragraph("AI Document Intelligence Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Generated on: {timestamp}", normal_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Summary
    elements.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(data.get("summary", "N/A"), normal_style))
    elements.append(Spacer(1, 0.5 * inch))

    analysis = data.get("analysis", {})

    # Keywords
    if "keywords" in analysis:
        elements.append(Paragraph("<b>Keywords</b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(", ".join(analysis["keywords"]), normal_style))
        elements.append(Spacer(1, 0.5 * inch))

    # Sentiment
    if "sentiment" in analysis:
        elements.append(Paragraph("<b>Sentiment Analysis</b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(str(analysis["sentiment"]), normal_style))
        elements.append(Spacer(1, 0.5 * inch))

    # Emotion
    if "emotion" in analysis:
        elements.append(Paragraph("<b>Emotion Analysis</b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))
        emotion_text = f"Emotion: {analysis['emotion']['emotion']} | Confidence: {analysis['emotion']['confidence']}"
        elements.append(Paragraph(emotion_text, normal_style))
        elements.append(Spacer(1, 0.5 * inch))

    # Subjectivity
    if "subjectivity" in analysis:
        elements.append(Paragraph("<b>Subjectivity Analysis</b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))
        subj_text = f"Type: {analysis['subjectivity']['type']} | Score: {analysis['subjectivity']['subjectivity_score']}"
        elements.append(Paragraph(subj_text, normal_style))
        elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)

    return file_path