import json

from pathlib import Path

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from risk_assessor import RiskAssessor


class ReportGenerator:

    FONT_CANDIDATES = [
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]

    def __init__(self):

        self.font_name = self._register_font()

    def _register_font(self):

        for path in self.FONT_CANDIDATES:

            if Path(path).exists():

                try:
                    pdfmetrics.registerFont(TTFont("ReportFont", path))
                    return "ReportFont"

                except Exception:
                    continue

        return "Helvetica"

    def generate(self, reports, output_file="expert_report.pdf"):

        doc = SimpleDocTemplate(output_file)

        styles = getSampleStyleSheet()

        for style_name in styles.byName:
            styles[style_name].fontName = self.font_name

        wrap_style = ParagraphStyle(
            "Wrap",
            parent=styles["Normal"],
            fontName=self.font_name,
            wordWrap="CJK"
        )

        content = []

        content.append(
            Paragraph(
                "Отчёт системы поддержки специалиста по компьютерной экспертизе",
                styles["Title"]
            )
        )

        content.append(Spacer(1, 20))

        for report in reports:

            content.append(
                Paragraph(
                    f"Файл: {report['file_name']}",
                    styles["Heading2"]
                )
            )

            content.append(
                Paragraph(
                    f"Путь: {report.get('file_path', '')}",
                    wrap_style
                )
            )

            content.append(
                Paragraph(
                    f"Уровень риска: {report['risk_level']}",
                    styles["Normal"]
                )
            )

            content.append(
                Paragraph(
                    f"Баллы риска: {report['risk_score']}",
                    styles["Normal"]
                )
            )

            content.append(
                Paragraph(
                    f"Оценка ИИ (важность): "
                    f"{report.get('ai_importance') or 'не определена'}",
                    styles["Normal"]
                )
            )

            content.append(Spacer(1, 10))

            content.append(
                Paragraph(
                    "Найденные артефакты",
                    styles["Heading3"]
                )
            )

            artifacts = report["artifacts"]

            for art_key in RiskAssessor.WEIGHTS:

                art_label = RiskAssessor.LABELS[art_key]
                values = artifacts.get(art_key, [])

                content.append(
                    Paragraph(
                        f"{art_label}: {', '.join(values) or 'Не найдено'}",
                        wrap_style
                    )
                )

            content.append(Spacer(1, 10))

            content.append(
                Paragraph(
                    "ИИ-анализ",
                    styles["Heading3"]
                )
            )

            analysis_text = report["analysis"]

            analysis_text = analysis_text.replace("\n", "<br/>")

            content.append(
                Paragraph(
                    analysis_text,
                    styles["Normal"]
                )
            )

            content.append(Spacer(1, 20))

            content.append(PageBreak())

        doc.build(content)

        return output_file