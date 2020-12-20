from datetime import datetime

from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_COLOR_INDEX

doc = Document()


def doc_header(text):
    header = doc.add_paragraph()
    header.style = 'Title'
    header.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.paragraph_format.space_before = Pt(18)
    header.paragraph_format.space_after = Pt(6)
    header = header.add_run(text)
    header.font.bold = True
    header.font.size = Pt(16)
    header.font.name = 'Arial'
    header.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    return header


def service(text):
    service_text = doc.add_paragraph(text, style='List Bullet')
    service_text.space_after = Pt(0)
    service_text.space_before = Pt(0)
    service_text.runs[0].font.name = 'Calibri'
    return service_text


def compet(text1, text2=None):
    text = doc.add_paragraph()
    text.paragraph_format.space_before = Pt(0)
    text.paragraph_format.space_after = Pt(18)
    text.add_run(text1)
    text.runs[0].font.size = Pt(11)
    text.runs[0].font.name = 'Arial'
    text.runs[0].font.bold = True
    if text2:
        text.add_run(text2)
        text.runs[1].font.size = Pt(11)
        text.runs[1].font.name = 'Arial'
    return text


def offer_crate(order):
    date = datetime.today().strftime("%d.%m.%y")
    total_price = 0

    section = doc.sections[0]
    header = section.header
    htable = header.add_table(rows=1, cols=2, width=Cm(15))
    hcells = htable.rows[0].cells
    text_cell_1 = hcells[0].paragraphs[0].add_run('IT-аутсорсинг «ITech»\n')
    text_cell_1.font.bold = True
    text_cell_1.font.italic = True
    text_cell_1.font.size = Pt(14)
    text_cell_1.font.name = 'Calibri'
    text_cell_2 = hcells[0].paragraphs[0].add_run(
        'Простое решение для Вашего бизнеса\nСистемное администрирование '
        'организаций\nТел: 8-800-555-53-51  E-mail: dir@itekbam.ru')
    text_cell_2.font.italic = True
    text_cell_2.font.size = Pt(9)
    text_cell_2.font.name = 'Calibri'
    text_cell_2.font.color.rgb = RGBColor(0x4f, 0x81, 0xbd)
    hcells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hcells[1].paragraphs[0].add_run().add_picture('Logo.jpg', height=Cm(2.3))
    htable.alignment = WD_TABLE_ALIGNMENT.RIGHT

    title = doc_header(f'Коммерческое предложение от {date}')

    main_text = doc.add_paragraph()
    main_text.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    main_text.paragraph_format.space_before = Pt(0)
    main_text.paragraph_format.space_after = Pt(0)
    main_text_run1 = main_text.add_run('Мы обслуживаем не технику,')
    main_text_run1.font.size = Pt(11)
    main_text_run1.font.name = 'Arial'
    main_text_run2 = main_text.add_run(' мы обслуживаем людей')
    main_text_run2.font.bold = True
    main_text_run2.font.size = Pt(11)
    main_text_run2.font.name = 'Arial'
    main_text = main_text.add_run(
        '. Мы экономим ваше время, обеспечивая комфортное, эффективное и '
        'безопасное использование компьютерных технологий.')
    main_text.font.size = Pt(11)
    main_text.font.name = 'Arial'

    header1 = doc_header('Стоимость оборудования')

    rows = len(order['art_list']) + 2
    cols = 4
    table = doc.add_table(rows=rows, cols=cols)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Наименование товара'
    hdr_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr_cells[0].paragraphs[0].runs[0].font.name = 'Calibri'
    hdr_cells[0].width = Inches(6)
    hdr_cells[1].text = 'Кол-во'
    hdr_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr_cells[1].paragraphs[0].runs[0].font.name = 'Calibri'
    hdr_cells[1].width = Inches(1)
    hdr_cells[2].text = 'Цена за шт.'
    hdr_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr_cells[2].paragraphs[0].runs[0].font.name = 'Calibri'
    hdr_cells[2].width = Inches(1)
    hdr_cells[3].text = 'Сумма'
    hdr_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr_cells[3].paragraphs[0].runs[0].font.name = 'Calibri'
    hdr_cells[3].width = Inches(1)

    for art in order['art_list']:
        row_cells = table.rows[order['art_list'].index(art) + 1].cells
        row_cells[0].text = order[f'title:{art}'].split('\n')[0]
        row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[0].paragraphs[0].runs[0].font.name = 'Calibri'
        row_cells[0].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        row_cells[0].paragraphs[0].runs[0].font.bold = False
        row_cells[1].text = str(order[f'count:{art}'])
        row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[1].paragraphs[0].runs[0].font.name = 'Calibri'
        row_cells[1].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        row_cells[2].text = order[f'price:{art}']
        row_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[2].paragraphs[0].runs[0].font.name = 'Calibri'
        row_cells[2].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        row_cells[2].paragraphs[0].runs[
            0].font.highlight_color = WD_COLOR_INDEX.YELLOW
        row_cells[3].text = str(
            int(order[f'count:{art}']) * int(order[f'price:{art}']))
        total_price += int(row_cells[3].text)
        row_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[3].paragraphs[0].runs[0].font.name = 'Calibri'
        row_cells[3].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        row_cells[3].paragraphs[0].runs[0].font.bold = True
        row_cells[3].paragraphs[0].runs[0].font.color.rgb = RGBColor(0x00,
                                                                     0xb0,
                                                                     0x50)

    total_cells = table.rows[len(order['art_list']) + 1].cells
    total_cells[0].merge(total_cells[1])
    total_cells[0].merge(total_cells[2])
    total_cells[0].text = "ИТОГО:"
    total_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    total_cells[0].paragraphs[0].runs[0].font.name = 'Calibri'
    total_cells[0].paragraphs[0].runs[0].font.bold = True
    total_cells[0].paragraphs[0].runs[0].font.italic = True
    total_cells[3].text = f'{total_price}р.'
    total_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    total_cells[3].paragraphs[0].runs[0].font.name = 'Calibri'
    total_cells[3].paragraphs[0].runs[0].font.bold = True
    total_cells[3].paragraphs[0].runs[0].font.color.rgb = RGBColor(0x00, 0xb0,
                                                                   0x50)

    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style.font.name = 'Calibri'
    table.style = 'Medium Shading 1 Accent 1'
    table.width = Cm(20)

    header2 = doc_header('Услуги, входящие в стоимость')

    service_text_1 = service('Доставка оборудования до заказчика')
    service_text_2 = service(
        'Полная сборка и установка оборудования на рабочем месте.')

    header3 = doc_header('Наши конкурентные преимущества')

    price_text = compet('    Цена\n',
                        '    За счет развитой логистики, расширенной базы '
                        'поставщиков, высокой стандартизации мы предоставляем '
                        'самые конкурентные цены на рынке.')
    quality_text = compet('    Отличное качество обслуживания\n',
                          '    Высокое качество обслуживания – основной '
                          'критерий подхода к решению задач любой сложности.')
    complex_text = compet('    Комплексный подход к задачам IT\n',
                          '    Мы выполняем весь спектр работ по IT.')
    moment_text = compet('    Мгновенное решение возникающих проблем')

    doc.save(f'КП_от_{date}.docx')
