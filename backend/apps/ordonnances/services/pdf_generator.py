import qrcode
import os
import math
from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Circle, String, Line, Group
from reportlab.graphics import renderPDF
from django.conf import settings


NAVY = colors.HexColor('#1a237e')
BLUE = colors.HexColor('#1565c0')
CYAN = colors.HexColor('#0097a7')
GRAY = colors.HexColor('#666666')
LIGHT_GRAY = colors.HexColor('#f5f7fa')
BORDER = colors.HexColor('#e0e0e0')
WHITE = colors.white


def generer_cachet_medecin(medecin):
    """Génère un cachet circulaire avec les infos du médecin"""
    size = 160
    d = Drawing(size, size)
    cx, cy = size / 2, size / 2
    r = 72

    # Cercle extérieur double
    d.add(Circle(cx, cy, r, strokeColor=NAVY, strokeWidth=2.5, fillColor=None))
    d.add(Circle(cx, cy, r - 4, strokeColor=NAVY, strokeWidth=0.8, fillColor=None))

    # Petites croix décoratives en haut et en bas
    for angle in [90, 270]:
        x = cx + (r - 2) * math.cos(math.radians(angle))
        y = cy + (r - 2) * math.sin(math.radians(angle))
        d.add(Line(x - 4, y, x + 4, y, strokeColor=NAVY, strokeWidth=1.5))
        d.add(Line(x, y - 4, x, y + 4, strokeColor=NAVY, strokeWidth=1.5))

    # Ligne horizontale au milieu
    d.add(Line(cx - r + 15, cy, cx + r - 15, cy, strokeColor=NAVY, strokeWidth=0.5))

    # Texte en haut : "Dr. Prénom Nom"
    nom_complet = f"Dr. {medecin.prenom} {medecin.nom}"
    font_size_nom = 9 if len(nom_complet) <= 20 else 7.5
    d.add(String(cx, cy + 22, nom_complet, fontSize=font_size_nom,
                 fontName='Helvetica-Bold', fillColor=NAVY, textAnchor='middle'))

    # Texte au milieu : Spécialité
    spec = medecin.specialite or 'Médecine générale'
    font_size_spec = 7.5 if len(spec) <= 22 else 6.5
    d.add(String(cx, cy + 8, spec, fontSize=font_size_spec,
                 fontName='Helvetica', fillColor=NAVY, textAnchor='middle'))

    # Texte en bas : "MEDIGO"
    d.add(String(cx, cy - 18, "MEDIGO", fontSize=10,
                 fontName='Helvetica-Bold', fillColor=CYAN, textAnchor='middle'))

    # Texte tout en bas : "Téléconsultation"
    d.add(String(cx, cy - 30, "Téléconsultation", fontSize=6.5,
                 fontName='Helvetica', fillColor=NAVY, textAnchor='middle'))

    return d


def generer_pdf_ordonnance(ordonnance):
    consultation = ordonnance.consultation
    patient = consultation.patient
    medecin = consultation.medecin

    filename = f"ordonnance_{ordonnance.id}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, 'ordonnances', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # ===== HEADER AVEC LOGO =====
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    header_items = []

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2 * cm, height=2 * cm)
        logo.hAlign = 'LEFT'
        header_left = logo
    else:
        header_left = Paragraph("MEDIGO", ParagraphStyle(
            'LogoText', fontSize=22, fontName='Helvetica-Bold',
            textColor=NAVY
        ))

    header_right_text = f"""
    <font size="9" color="#666666">Date: {ordonnance.creee_le.strftime('%d/%m/%Y')}</font><br/>
    <font size="8" color="#999999">Réf: {str(ordonnance.id)[:8].upper()}</font>
    """
    header_right = Paragraph(header_right_text, ParagraphStyle(
        'HeaderRight', fontSize=9, fontName='Helvetica',
        alignment=TA_RIGHT, leading=14
    ))

    header_table = Table(
        [[header_left, header_right]],
        colWidths=[9 * cm, 8 * cm]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.3 * cm))

    # Ligne de séparation header
    elements.append(Table(
        [['']],
        colWidths=[17 * cm],
        style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, NAVY),
        ])
    ))
    elements.append(Spacer(1, 0.6 * cm))

    # ===== TITRE ORDONNANCE =====
    elements.append(Paragraph("ORDONNANCE MÉDICALE", ParagraphStyle(
        'OrdTitle', fontSize=18, fontName='Helvetica-Bold',
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=20
    )))

    # ===== INFOS PATIENT =====
    patient_header = Paragraph(
        '<font color="#1565c0"><b>PATIENT</b></font>',
        ParagraphStyle('PatH', fontSize=10, fontName='Helvetica-Bold', spaceAfter=6)
    )
    elements.append(patient_header)

    age = patient.age if hasattr(patient, 'age') else ''
    sexe = patient.get_sexe_display() if hasattr(patient, 'get_sexe_display') else ''

    patient_info = [
        ['Nom complet', f"{patient.prenom} {patient.nom}"],
        ['Date de naissance', f"{patient.date_naissance.strftime('%d/%m/%Y')} ({age} ans)"],
        ['Téléphone', patient.telephone or '—'],
    ]

    patient_table = Table(patient_info, colWidths=[4.5 * cm, 12.5 * cm])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), GRAY),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.6 * cm))

    # ===== PRESCRIPTION =====
    presc_header = Paragraph(
        '<font color="#1565c0"><b>PRESCRIPTION</b></font>',
        ParagraphStyle('PrescH', fontSize=10, fontName='Helvetica-Bold', spaceAfter=6)
    )
    elements.append(presc_header)

    # Formatter le contenu de la prescription
    contenu = ordonnance.contenu.replace('\n', '<br/>')
    prescription_box = Table(
        [[Paragraph(contenu, ParagraphStyle(
            'PrescContent', fontSize=11, fontName='Helvetica',
            spaceAfter=4, leading=18, textColor=colors.HexColor('#222222')
        ))]],
        colWidths=[17 * cm]
    )
    prescription_box.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, BLUE),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9ff')),
        ('PADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
    ]))
    elements.append(prescription_box)
    elements.append(Spacer(1, 1.5 * cm))

    # ===== FOOTER : MEDECIN + CACHET =====
    # Infos médecin à gauche
    medecin_info = f"""
    <font size="11"><b>Dr. {medecin.prenom} {medecin.nom}</b></font><br/>
    <font size="9" color="#666666">{medecin.specialite or 'Médecine générale'}</font><br/>
    <font size="9" color="#666666">{medecin.user.email}</font>
    """
    medecin_para = Paragraph(medecin_info, ParagraphStyle(
        'MedInfo', fontSize=10, fontName='Helvetica', leading=16
    ))

    # Cachet auto-généré à droite
    cachet_drawing = generer_cachet_medecin(medecin)

    footer_table = Table(
        [[medecin_para, cachet_drawing]],
        colWidths=[10 * cm, 7 * cm]
    )
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(footer_table)

    # ===== BUILD =====
    doc.build(elements)

    ordonnance.storage_key = f'ordonnances/{filename}'
    ordonnance.save()

    return filepath


def generer_qr_code(ordonnance, base_url):
    qr_filename = f"qr_{ordonnance.id}.png"
    qr_filepath = os.path.join(settings.MEDIA_ROOT, 'qrcodes', qr_filename)
    os.makedirs(os.path.dirname(qr_filepath), exist_ok=True)

    url = f"{base_url}/patient/ordonnance/{ordonnance.id}/"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_filepath)

    ordonnance.qr_code_key = f'qrcodes/{qr_filename}'
    ordonnance.save()

    return qr_filepath
