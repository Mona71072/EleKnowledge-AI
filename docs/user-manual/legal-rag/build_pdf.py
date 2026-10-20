"""Build a user-facing catalog from the existing law catalog; no scope changes."""
import csv
import hashlib
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CATALOG = ROOT / 'docs/features/development/legal-rag-target-laws.md'
CSV = ROOT / 'legal/all_xml/all_law_list.csv'
EXPECTED_HASH = '78a9bdfd2dd7df7b83b64af69b40bf12255e7fe8beb222f83ac29532247fd65c'
assert hashlib.sha256(CSV.read_bytes().replace(b'\r\n', b'\n')).hexdigest() == EXPECTED_HASH
rows = list(csv.DictReader(CSV.open(encoding='utf-8-sig', newline='')))
by_folder = {}
for row in rows:
    match = re.search(r'/law/([^/]+)/([^/]+)', row['本文URL'])
    if match:
        by_folder[match[1] + '_' + match[2]] = row

groups = {key: [] for key in range(3, 8)}
section = None
for line in CATALOG.read_text(encoding='utf-8').splitlines():
    heading = re.match(r'## ([3-7])\.', line)
    if heading:
        section = int(heading[1])
    match = re.search(r'`(\d{3}[A-Z0-9]+_\d{8}_[A-Z0-9]+)`', line)
    if section and line.startswith('|') and match:
        folder = match[1]
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        name = cells[-2]
        source = by_folder[folder]
        assert source['法令名'] == name, (name, source['法令名'])
        assert source['未施行'].strip() == ''
        groups[section].append((name, folder, source))
assert [len(groups[k]) for k in range(3, 8)] == [10, 12, 7, 16, 8]
assert len({x[1] for group in groups.values() for x in group}) == 53

# Match the distributed manual's CSS; preserve this catalog's four-page structure.
pdfmetrics.registerFont(TTFont('JP', 'C:/Windows/Fonts/BIZ-UDGothicR.ttc', subfontIndex=1))
pdfmetrics.registerFont(TTFont('JPBold', 'C:/Windows/Fonts/BIZ-UDGothicB.ttc', subfontIndex=1))
TEXT = colors.HexColor('#1a1a1a')
BLUE = colors.HexColor('#1d4ed8')
LIGHT_BLUE = colors.HexColor('#eff6ff')
RULE = colors.HexColor('#93c5fd')
GRID = colors.HexColor('#cbd5e1')
MUTED = colors.HexColor('#475569')
styles = {
    'title': ParagraphStyle('title', fontName='JPBold', fontSize=18, leading=26, textColor=TEXT, wordWrap='CJK'),
    'sub': ParagraphStyle('sub', fontName='JP', fontSize=10.5, leading=17.85, textColor=MUTED, spaceAfter=9),
    'body': ParagraphStyle('body', fontName='JP', fontSize=10.5, leading=17.85, textColor=TEXT, wordWrap='CJK', spaceAfter=7),
    'small': ParagraphStyle('small', fontName='JP', fontSize=9, leading=15.3, textColor=MUTED, wordWrap='CJK', spaceAfter=5),
    'heading': ParagraphStyle('heading', fontName='JPBold', fontSize=13.5, leading=23, textColor=TEXT, spaceBefore=16, spaceAfter=8, keepWithNext=True),
    'noteheading': ParagraphStyle('noteheading', fontName='JPBold', fontSize=11.5, leading=19.55, textColor=colors.HexColor('#1e3a8a'), spaceBefore=14, spaceAfter=6, keepWithNext=True),
    'cell': ParagraphStyle('cell', fontName='JP', fontSize=9.8, leading=16.66, textColor=TEXT, wordWrap='CJK'),
    'headcell': ParagraphStyle('headcell', fontName='JPBold', fontSize=9.8, leading=16.66, textColor=TEXT),
}


class SectionHeading(Paragraph):
    """Draw the manual's light-blue rule underneath a subsection heading."""

    def draw(self):
        super().draw()
        self.canv.setStrokeColor(RULE)
        self.canv.setLineWidth(1.5)
        self.canv.line(0, -2, self.width, -2)


def p(text, style='body'):
    if style == 'title':
        title = Table([[Paragraph(text, styles[style])]], colWidths=[178 * mm])
        title.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE),
            ('LINEBEFORE', (0, 0), (0, -1), 4.5, BLUE),
            ('LEFTPADDING', (0, 0), (-1, -1), 4 * mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2 * mm),
            ('TOPPADDING', (0, 0), (-1, -1), 2 * mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2 * mm),
        ]))
        title.spaceAfter = 6 * mm
        return title
    if style == 'heading':
        return SectionHeading(text, styles[style])
    return Paragraph(text, styles[style])

story = []
number = 0

def law_table(title, entries):
    global number
    data = [[p('No.', 'headcell'), p('法令名（クリックでe-Gov原文へ）', 'headcell'), p('収録版の施行日', 'headcell')]]
    for name, folder, source in entries:
        number += 1
        stamp = folder.split('_')[1]
        date = f'{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}'
        data.append([p(str(number), 'cell'), p(f'<link href="{escape(source["本文URL"])}" color="#1a1a1a">{escape(name)}</link>', 'cell'), p(date, 'cell')])
    table = Table(data, colWidths=[12 * mm, 132 * mm, 34 * mm], repeatRows=1, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_BLUE),
        ('GRID', (0, 0), (-1, -1), 0.75, GRID),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2.5 * mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2.5 * mm),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5 * mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5 * mm),
    ]))
    story.extend([p(title + f'　／ {len(entries)}件', 'heading'), table])

story += [p('Ele-Knowledge  |  法令チャット', 'sub'), p('法令RAG 取扱法令一覧', 'title'),
          p('dev環境・プレリリース向け利用者資料<br/>一覧基準日：2026年10月1日　｜　資料作成日：2026年10月15日', 'sub'),
          p('昇降機の設置・建築、据付作業、電気工事、改修・撤去、搬入に関する法令を調べるための一覧です。対象カタログの53法令を分野別に掲載しています。'),
          p('<b>掲載範囲：6分野・53法令（通常候補51件＋条件付き候補2件）</b><br/>法律だけでなく、施行令・施行規則・技術基準省令等もそれぞれ1件と数えています。'),
          p('本資料はdev環境のプレリリース向け一覧です。初期候補の根拠には確認記録がありますが、正式な対象部門の承認や本番利用の承認とは区別します。業務上の適用条件と稼働環境の最新の収録・検索状態は別途確認してください。', 'small')]
law_table('01　建築・消防・バリアフリー', groups[3])
story.append(PageBreak())
story += [p('据付作業・電気工事に関する法令', 'title'),
          p('使用する設備・物質や作業内容によって、確認すべき法令・条文が異なります。', 'sub')]
law_table('02　労働安全・労務', groups[4])
law_table('03　電気設備・電気工事', groups[5])
story.append(PageBreak())
story += [p('建設・改修・撤去に関する法令', 'title'),
          p('対象工事・資材・地域などの条件に応じて、適用要件を確認してください。', 'sub')]
law_table('04　建設・廃棄物・環境', groups[6])
story.append(PageBreak())
story += [p('搬入・条件付き対象と利用案内', 'title')]
law_table('05　道路・搬入', groups[7][:6])
law_table('06　条件付き対象', groups[7][6:])
story += [p('条件付き対象の見方', 'noteheading'),
          p('高圧ガス保安法はボンベ等の高圧ガスを扱う場合、作業環境測定法は法令上の作業環境測定が必要となる場合の参照候補です。各法令の適用条件を原文で確認してください。', 'small'),
          p('この一覧に含まれない資料', 'noteheading'),
          p('自治体条例、告示・通知・通達、JIS、業界標準、メーカー資料は、この53件に含みません。未施行版・過去版も本一覧の対象外です。すべての関連法令・資料を網羅する一覧ではありません。', 'small'),
          p('利用時の確認', 'noteheading'),
          p('法令名をクリックすると、参照元カタログに対応するe-Gov原文を開けます。「収録版の施行日」は一覧に掲載した版の日付であり、資料作成日時点の最新改正を保証する日付ではありません。業務判断の前に原文・施行日・作業条件を確認してください。', 'small'),
          p('作成根拠・版情報', 'noteheading'),
          p('参照：プロジェクトの「法令RAG 対象法令フォルダ一覧」（一覧基準日2026-10-01、選定説明の検証日2026-10-09）、e-Gov一括ダウンロード付属の法令一覧CSV。53件の法令名・版識別子・未施行欄を照合して作成しました。稼働中の検索基盤と最新改正の照合は実施していません。', 'small'),
          p('<link href="https://laws.e-gov.go.jp/" color="#1d4ed8">公式原文：e-Gov法令検索</link>　｜　文書版：2026-10-15 / 1.0', 'small')]

def footer(canvas, doc):
    canvas.setFont('JP', 6)
    canvas.setFillColor(colors.HexColor('#64748b'))
    canvas.drawString(16 * mm, 290 * mm, 'EleKnowledge 法令RAG 取扱法令一覧')
    canvas.drawRightString(194 * mm, 290 * mm, '第1版 2026-10-15')


class NumberedCanvas(pdfcanvas.Canvas):
    """Use the manual's centered page / total-pages footer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_states = []

    def showPage(self):
        self.page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        count = len(self.page_states)
        for state in self.page_states:
            self.__dict__.update(state)
            self.setFont('JP', 6)
            self.setFillColor(colors.HexColor('#64748b'))
            self.drawCentredString(105 * mm, 5 * mm, f'{self._pageNumber} / {count}')
            super().showPage()
        super().save()

target = OUT / '法令RAG_取扱法令一覧_2026-10-15.pdf'
doc = SimpleDocTemplate(str(target), pagesize=(210 * mm, 297 * mm), rightMargin=16 * mm,
                        leftMargin=16 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                        title='Ele-Knowledge 法令RAG 取扱法令一覧', author='Ele-Knowledge',
                        subject='dev環境向け・53法令・一覧基準日2026-10-01')
doc.build(story, onFirstPage=footer, onLaterPages=footer, canvasmaker=NumberedCanvas)
print(f'Created {target.name}; verified {number} laws against CSV ({len(rows)} rows).')
