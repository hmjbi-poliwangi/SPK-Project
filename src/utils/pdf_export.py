"""
PDF Export module untuk mendukung export laporan ke format PDF.
Menggunakan reportlab. Bisa digunakan oleh Desktop app maupun Web app.
"""

from io import BytesIO
from datetime import datetime


def export_rankings_to_pdf(
    department_name: str,
    rankings: list,
    criteria_list: list = None
) -> BytesIO:
    """
    Export hasil ranking ke PDF.
    Mengembalikan BytesIO object yang berisi PDF.

    Args:
        department_name: Nama departemen.
        rankings: List of dict dengan keys: name, ncf, nsf, total (atau id, alternative_name, ...).
        criteria_list: (Opsional) List of criteria names untuk ditampilkan.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        raise ImportError(
            "reportlab belum terinstall. Jalankan: pip install reportlab"
        )

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=20*mm,
        bottomMargin=15*mm,
        leftMargin=20*mm,
        rightMargin=20*mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"),
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=20,
        textColor=colors.HexColor("#555555"),
    )

    elements = []

    # Judul
    elements.append(Paragraph("Laporan Hasil Ranking", title_style))
    elements.append(
        Paragraph(
            f"Departemen: {department_name}<br/>"
            f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            subtitle_style
        )
    )
    elements.append(Spacer(1, 10*mm))

    # Header tabel
    table_data = [["Rank", "Nama Alternatif", "Total Skor"]]

    for i, r in enumerate(rankings, start=1):
        name = r.get("name") or r.get("alternative_name", "-")
        total = f"{r.get('total', 0):.3f}"
        table_data.append([str(i), name, total])

    # Style tabel
    col_widths = [50, 200, 100]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ecec13")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1d1d1d")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f5f5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    # Footer
    elements.append(Spacer(1, 15*mm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor("#999999"),
        alignment=1,  # center
    )
    elements.append(
        Paragraph(
            f"Dicetak dari SPK Profile Matching - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            footer_style
        )
    )

    doc.build(elements)
    buf.seek(0)
    return buf


def export_report_without_rankings(
    criteria: list,
    departments: list,
    alternatives: list,
    department_profiles: list = None,
    aspects: list = None
) -> BytesIO:
    """
    Export laporan lengkap TANPA perangkingan.
    Berisi: Aspects, Criteria, Departments, Alternatives.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        raise ImportError("reportlab belum terinstall.")

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=20*mm, bottomMargin=15*mm,
        leftMargin=20*mm, rightMargin=20*mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=18, spaceAfter=6)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'], fontSize=11, spaceAfter=15)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, spaceAfter=8, spaceBefore=12)

    elements = []
    elements.append(Paragraph("Laporan Data SPK Profile Matching", title_style))
    elements.append(Paragraph(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 8*mm))

    # --- Aspects ---
    if aspects:
        elements.append(Paragraph("A. Daftar Aspek", h2_style))
        asp_data = [["ID", "Nama Aspek", "Bobot"]]
        for a in aspects:
            asp_data.append([str(a.get("id", "-")), a.get("name", "-"), str(a.get("weight", "-"))])
        t_asp = Table(asp_data, colWidths=[40, 300, 100], repeatRows=1)
        t_asp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ecec13")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1d1d1d")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f5f5f5")]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_asp)
        elements.append(Spacer(1, 5*mm))

    # --- Criteria ---
    elements.append(Paragraph("B. Daftar Kriteria", h2_style))
    crit_data = [["ID", "Nama Kriteria", "Deskripsi"]]
    for c in criteria:
        crit_data.append([str(c.get("id", "-")), c.get("name", "-"), c.get("description", "-") or "-"])
    t1 = Table(crit_data, colWidths=[40, 150, 250], repeatRows=1)
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ecec13")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1d1d1d")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f5f5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 5*mm))

    # --- Departments ---
    elements.append(Paragraph("C. Daftar Departemen", h2_style))
    dept_data = [["ID", "Nama Departemen"]]
    for d in departments:
        dept_data.append([str(d.get("id", "-")), d.get("name", "-")])
    t2 = Table(dept_data, colWidths=[40, 400], repeatRows=1)
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ecec13")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1d1d1d")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f5f5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 5*mm))

    # --- Alternatives ---
    elements.append(Paragraph("D. Daftar Alternatif (Kandidat)", h2_style))
    alt_data = [["ID", "Nama", "NIM", "Prodi", "Kelas"]]
    for a in alternatives:
        alt_data.append([
            str(a.get("id", "-")), a.get("name", "-"),
            a.get("nim", "-"), a.get("prodi", "-"),
            a.get("kelas", "-")
        ])
    t3 = Table(alt_data, colWidths=[30, 100, 100, 120, 90], repeatRows=1)
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ecec13")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1d1d1d")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f5f5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t3)

    # Footer
    elements.append(Spacer(1, 15*mm))
    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'], fontSize=8,
        textColor=colors.HexColor("#999999"), alignment=1,
    )
    elements.append(
        Paragraph(
            f"Dicetak dari SPK Profile Matching - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            footer_style
        )
    )

    doc.build(elements)
    buf.seek(0)
    return buf


def export_all_data_to_pdf(
    criteria: list,
    departments: list,
    alternatives: list,
    rankings_per_department: dict = None,
    aspects: list = None
) -> BytesIO:
    """
    Export seluruh data + perangkingan ke PDF (laporan lengkap dengan ranking).
    Fungsi ini dipertahankan untuk kompatibilitas dengan kode lama.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        raise ImportError("reportlab belum terinstall.")

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=20*mm, bottomMargin=15*mm,
        leftMargin=20*mm, rightMargin=20*mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=18, spaceAfter=6)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'], fontSize=11, spaceAfter=15)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, spaceAfter=8, spaceBefore=12)

    elements = []
    elements.append(Paragraph("Laporan Lengkap SPK Profile Matching", title_style))
    elements.append(Paragraph(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 8*mm))

    # --- Aspects ---
    if aspects:
        elements.append(Paragraph("A. Daftar Aspek", h2_style))
        asp_data = [["ID", "Nama Aspek", "Bobot"]]
        for a in aspects:
            asp_data.append([str(a.get("id", "-")), a.get("name", "-"), str(a.get("weight", "-"))])
        t_asp = Table(asp_data, colWidths=[40, 300, 100], repeatRows=1)
        t_asp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ecec13")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1d1d1d")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f5f5f5")]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_asp)
        elements.append(Spacer(1, 5*mm))

    # --- Criteria ---
    elements.append(Paragraph("B. Daftar Kriteria", h2_style))
    crit_data = [["ID", "Nama Kriteria", "Deskripsi"]]
    for c in criteria:
        crit_data.append([str(c.get("id", "-")), c.get("name", "-"), c.get("description", "-") or "-"])
    t1 = Table(crit_data, colWidths=[40, 150, 250], repeatRows=1)
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ecec13")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1d1d1d")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f5f5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 5*mm))

    # --- Departments ---
    elements.append(Paragraph("C. Daftar Departemen", h2_style))
    dept_data = [["ID", "Nama Departemen"]]
    for d in departments:
        dept_data.append([str(d.get("id", "-")), d.get("name", "-")])
    t2 = Table(dept_data, colWidths=[40, 400], repeatRows=1)
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ecec13")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1d1d1d")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f5f5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 5*mm))

    # --- Alternatives ---
    elements.append(Paragraph("D. Daftar Alternatif (Kandidat)", h2_style))
    alt_data = [["ID", "Nama", "NIM", "Prodi", "Kelas"]]
    for a in alternatives:
        alt_data.append([
            str(a.get("id", "-")), a.get("name", "-"),
            a.get("nim", "-"), a.get("prodi", "-"),
            a.get("kelas", "-")
        ])
    t3 = Table(alt_data, colWidths=[30, 100, 100, 120, 90], repeatRows=1)
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ecec13")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1d1d1d")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f5f5f5")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t3)

    # --- Rankings per department ---
    if rankings_per_department:
        elements.append(PageBreak())
        elements.append(Paragraph("E. Hasil Ranking per Departemen", h2_style))
        for dept_name, rankings in rankings_per_department.items():
            elements.append(Spacer(1, 4*mm))
            elements.append(Paragraph(f"Departemen: {dept_name}", subtitle_style))
            rank_data = [["Peringkat", "Nama Alternatif", "Total"]]
            for i, r in enumerate(rankings, 1):
                name = r.get("name") or r.get("alternative_name", "-")
                rank_data.append([
                    str(i), name,
                    f"{r.get('total', 0):.3f}"
                ])
            t4 = Table(rank_data, colWidths=[50, 180, 70], repeatRows=1)
            t4.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#9b59b6")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f5f5f5")]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t4)

    doc.build(elements)
    buf.seek(0)
    return buf
