from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.units import cm
from reportlab.platypus import Image
from datetime import datetime


def add_header_footer(canvas, doc):
    canvas.saveState()

    # Marca d'água elegante com opacidade leve
    canvas.setFillColorRGB(0.96, 0.96, 0.96)
    canvas.setFont('Helvetica-Bold', 42)
    canvas.translate(10 * cm, 15 * cm)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "STOCK MANAGEMENT")
    canvas.restoreState()

    canvas.saveState()

    # Cabeçalho Superior Discreto
    canvas.setFont('Helvetica-Bold', 10)
    canvas.setFillColor(colors.HexColor("#1e293b"))
    canvas.drawString(2 * cm, 28 * cm, "📦 STOCK MANAGEMENT")
    
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(2 * cm, 27.5 * cm, "Sistema de Gestão de Estoque")

    # Linha divisória do cabeçalho
    canvas.setStrokeColor(colors.HexColor("#e2e8f0"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 27.2 * cm, 19 * cm, 27.2 * cm)

    # Rodapé Profissional
    canvas.line(2 * cm, 2 * cm, 19 * cm, 2 * cm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(2 * cm, 1.5 * cm, "Documento gerado automaticamente pelo sistema.")
    canvas.drawRightString(19 * cm, 1.5 * cm, f"Página {doc.page}")
    canvas.restoreState()


def generate_sales_pdf(sales):
    pdf = SimpleDocTemplate(
        "relatorio.pdf",
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=3*cm,
        bottomMargin=2.5*cm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor("#64748b")
    )

    th_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    td_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#334155"),
        alignment=TA_CENTER
    )

    elements = []

    # RESTAURANDO SUA LOGO REAL EM 3D:
    # Ajustando as dimensões para uma proporção retangular correta para a imagem não achatar
    try:
        logo = Image("images/logo.png", width=5.6 * cm, height=3.2 * cm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 0.4 * cm))
    except:
        elements.append(Spacer(1, 1 * cm))

    elements.append(Paragraph("RELATÓRIO DE VENDAS", title_style))
    
    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
    elements.append(Paragraph(f"Emitido em: {data_atual}", meta_style))
    elements.append(Spacer(1, 0.8 * cm))

    data = [
        [
            Paragraph('Produto', th_style),
            Paragraph('Quantidade', th_style),
            Paragraph('Valor (MT)', th_style),
            Paragraph('Data / Hora', th_style)
        ]
    ]

    total = 0

    for sale in sales:
        nome_produto = str(sale[0])   
        qtd_movimento = str(sale[1])  
        
        try:
            valor_venda = float(sale[2]) 
        except (ValueError, TypeError, IndexError):
            valor_venda = 0.0
            
        data_movimento = str(sale[3]) 

        total += valor_venda

        data.append([
            Paragraph(nome_produto, td_style),
            Paragraph(qtd_movimento, td_style),
            Paragraph(f"{valor_venda:,.2f} MT", td_style),
            Paragraph(data_movimento, td_style)
        ])

    table = Table(data, colWidths=[5.5*cm, 2.5*cm, 4*cm, 5*cm])
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")), 
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]), 
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")), 
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.6 * cm))

    total_style = ParagraphStyle(
        'TotalStyle',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor("#0f172a")
    )
    elements.append(Paragraph(f"Valor Total Acumulado: {total:,.2f} MT", total_style))
    elements.append(Spacer(1, 2.0 * cm))

    sig_line_style = ParagraphStyle(
        'SigLine',
        alignment=TA_CENTER,
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#64748b")
    )
    
    sig_data = [
        [Paragraph("_______________________________________", sig_line_style)],
        [Spacer(1, 0.15 * cm)],
        [Paragraph("Assinatura do Responsável", sig_line_style)]
    ]
    
    sig_table = Table(sig_data, colWidths=[17 * cm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    
    elements.append(sig_table)

    pdf.build(
        elements,
        onFirstPage=add_header_footer,
        onLaterPages=add_header_footer
    )

