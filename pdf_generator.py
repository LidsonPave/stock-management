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

def generate_general_pdf(
    total_products,
    total_stock,
    total_investment,
    total_sales,
    total_withdrawals
):

    pdf = SimpleDocTemplate(
        "relatorio_geral.pdf",
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
        fontSize=10,
        textColor=colors.HexColor("#334155"),
        alignment=TA_CENTER
    )

    elements = []

    try:
        logo = Image("images/logo.png", width=5.6*cm, height=3.2*cm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 0.4*cm))
    except:
        elements.append(Spacer(1, 1*cm))

    elements.append(Paragraph("RELATÓRIO GERAL", title_style))

    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
    elements.append(Paragraph(f"Emitido em: {data_atual}", meta_style))
    elements.append(Spacer(1, 0.8*cm))

    saldo = total_sales - total_withdrawals

    data = [
        [
            Paragraph('Descrição', th_style),
            Paragraph('Valor', th_style)
        ],

        [
            Paragraph('Produtos cadastrados', td_style),
            Paragraph(str(total_products), td_style)
        ],

        [
            Paragraph('Itens em estoque', td_style),
            Paragraph(str(total_stock), td_style)
        ],

        [
            Paragraph('Investimento', td_style),
            Paragraph(f'{total_investment:,.2f} MT', td_style)
        ],

        [
            Paragraph('Total de vendas', td_style),
            Paragraph(f'{total_sales:,.2f} MT', td_style)
        ],

        [
            Paragraph('Saídas do caixa', td_style),
            Paragraph(f'{total_withdrawals:,.2f} MT', td_style)
        ],

        [
            Paragraph('Saldo', td_style),
            Paragraph(f'{saldo:,.2f} MT', td_style)
        ]
    ]

    tabela = Table(data, colWidths=[8*cm, 8*cm])

    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [colors.white, colors.HexColor("#f8fafc")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('TOPPADDING', (0,1), (-1,-1), 6),
    ]))

    elements.append(tabela)
    elements.append(Spacer(1, 2*cm))

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
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    elements.append(sig_table)

    pdf.build(
        elements,
        onFirstPage=add_header_footer,
        onLaterPages=add_header_footer
    )


def generate_entries_pdf(entries):

    pdf = SimpleDocTemplate(
        "relatorio_entradas.pdf",
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
        textColor=colors.HexColor("#1e293b")
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        alignment=TA_CENTER,
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
        alignment=TA_CENTER
    )

    elements = []

    try:
        logo = Image("images/logo.png", width=5.6*cm, height=3.2*cm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
    except:
        pass

    elements.append(Paragraph("RELATÓRIO DE ENTRADAS", title_style))

    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")

    elements.append(
        Paragraph(
            f"Emitido em: {data_atual}",
            meta_style
        )
    )

    elements.append(Spacer(1,0.8*cm))

    data = [[
        Paragraph("Produto", th_style),
        Paragraph("Quantidade", th_style),
        Paragraph("Data", th_style)
    ]]

    for entry in entries:

        data.append([

            Paragraph(str(entry[0]), td_style),

            Paragraph(str(entry[1]), td_style),

            Paragraph(str(entry[2]), td_style)

        ])

    tabela = Table(
        data,
        colWidths=[7*cm,3*cm,6*cm]
    )

    tabela.setStyle(TableStyle([

        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#1e293b")),

        ('TEXTCOLOR',(0,0),(-1,0),colors.white),

        ('ALIGN',(0,0),(-1,-1),'CENTER'),

        ('ROWBACKGROUNDS',(0,1),(-1,-1),
         [colors.white, colors.HexColor("#f8fafc")]),

        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#cbd5e1"))

    ]))

    elements.append(tabela)

    pdf.build(
        elements,
        onFirstPage=add_header_footer,
        onLaterPages=add_header_footer
    )


def generate_low_stock_pdf(products):

    pdf = SimpleDocTemplate(
        "relatorio_estoque_baixo.pdf",
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=3*cm,
        bottomMargin=2.5*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    try:
        logo = Image("images/logo.png", width=5.6*cm, height=3.2*cm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1,0.4*cm))
    except:
        pass

    elements.append(Paragraph("RELATÓRIO DE ESTOQUE BAIXO", styles['Heading1']))
    elements.append(
        Paragraph(
            f"Emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            styles['Normal']
        )
    )

    elements.append(Spacer(1,0.8*cm))

    data = [
        ['Produto', 'Quantidade', 'Mínimo']
    ]

    for product in products:
        data.append([
            product[0],
            str(product[1]),
            str(product[2])
        ])

    tabela = Table(data, colWidths=[8*cm,4*cm,4*cm])

    tabela.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#1e293b")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),
            [colors.white, colors.HexColor("#f8fafc")]),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('PADDING',(0,0),(-1,-1),8)
    ]))

    elements.append(tabela)

    pdf.build(
        elements,
        onFirstPage=add_header_footer,
        onLaterPages=add_header_footer
    )


def generate_cashflow_pdf(withdrawals, total_sales, total_withdrawals, balance):

    pdf = SimpleDocTemplate(
        "relatorio_fluxo_caixa.pdf",
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=3*cm,
        bottomMargin=2.5*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    try:
        logo = Image("images/logo.png", width=5.6*cm, height=3.2*cm)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1,0.4*cm))
    except:
        pass

    elements.append(
        Paragraph(
            "RELATÓRIO DE FLUXO DE CAIXA",
            styles['Heading1']
        )
    )

    elements.append(
        Paragraph(
            f"Emitido em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            styles['Normal']
        )
    )

    elements.append(Spacer(1,0.8*cm))

    resumo = [
        ['Total de Vendas', f'{total_sales:.2f} MT'],
        ['Saídas do Caixa', f'{total_withdrawals:.2f} MT'],
        ['Saldo', f'{balance:.2f} MT']
    ]

    tabela_resumo = Table(resumo, colWidths=[8*cm,8*cm])

    tabela_resumo.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('PADDING',(0,0),(-1,-1),8),
        ('ALIGN',(0,0),(-1,-1),'CENTER')
    ]))

    elements.append(tabela_resumo)
    elements.append(Spacer(1,1*cm))

    data = [
        ['Descrição', 'Valor']
    ]

    for withdrawal in withdrawals:
        data.append([
            withdrawal[1],
            f'{withdrawal[2]:.2f} MT'
        ])

    tabela = Table(data, colWidths=[10*cm,6*cm])

    tabela.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#1e293b")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),
            [colors.white, colors.HexColor("#f8fafc")]),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('PADDING',(0,0),(-1,-1),8)
    ]))

    elements.append(tabela)

    pdf.build(
        elements,
        onFirstPage=add_header_footer,
        onLaterPages=add_header_footer
    )
