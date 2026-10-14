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

pdfmetrics.registerFont(TTFont('JP', 'C:/Windows/Fonts/YuGothR.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('JPBold', 'C:/Windows/Fonts/YuGothB.ttc', subfontIndex=0))
NAVY = colors.HexColor('#163347')
TEAL = colors.HexColor('#147d88')
MUTED = colors.HexColor('#526673')
styles = {
    'title': ParagraphStyle('title', fontName='JPBold', fontSize=23, leading=32, textColor=NAVY, spaceAfter=9),
    'sub': ParagraphStyle('sub', fontName='JP', fontSize=10, leading=17, textColor=MUTED, spaceAfter=9),
    'body': ParagraphStyle('body', fontName='JP', fontSize=9, leading=15, textColor=NAVY, wordWrap='CJK', spaceAfter=7),
    'small': ParagraphStyle('small', fontName='JP', fontSize=7.7, leading=12, textColor=MUTED, wordWrap='CJK', spaceAfter=5),
    'heading': ParagraphStyle('heading', fontName='JPBold', fontSize=13, leading=20, textColor=TEAL, spaceBefore=12, spaceAfter=7),
    'cell': ParagraphStyle('cell', fontName='JP', fontSize=8.6, leading=13, textColor=NAVY, wordWrap='CJK'),
    'headcell': ParagraphStyle('headcell', fontName='JPBold', fontSize=8, leading=12, textColor=colors.white),
}

def p(text, style='body'):
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
        data.append([p(str(number), 'cell'), p(f'<link href="{escape(source["本文URL"])}" color="#163347">{escape(name)}</link>', 'cell'), p(date, 'cell')])
    table = Table(data, colWidths=[12 * mm, 130 * mm, 32 * mm], repeatRows=1, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0f5f7'), colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 0.7, TEAL),
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
story += [p('条件付き対象の見方', 'heading'),
          p('高圧ガス保安法はボンベ等の高圧ガスを扱う場合、作業環境測定法は法令上の作業環境測定が必要となる場合の参照候補です。各法令の適用条件を原文で確認してください。'),
          p('この一覧に含まれない資料', 'heading'),
          p('自治体条例、告示・通知・通達、JIS、業界標準、メーカー資料は、この53件に含みません。未施行版・過去版も本一覧の対象外です。すべての関連法令・資料を網羅する一覧ではありません。'),
          p('利用時の確認', 'heading'),
          p('法令名をクリックすると、参照元カタログに対応するe-Gov原文を開けます。「収録版の施行日」は一覧に掲載した版の日付であり、資料作成日時点の最新改正を保証する日付ではありません。業務判断の前に原文・施行日・作業条件を確認してください。'),
          p('作成根拠・版情報', 'heading'),
          p('参照：プロジェクトの「法令RAG 対象法令フォルダ一覧」（一覧基準日2026-10-01、選定説明の検証日2026-10-09）、e-Gov一括ダウンロード付属の法令一覧CSV。53件の法令名・版識別子・未施行欄を照合して作成しました。稼働中の検索基盤と最新改正の照合は実施していません。', 'small'),
          p('<link href="https://laws.e-gov.go.jp/" color="#147d88">公式原文：e-Gov法令検索</link>　｜　文書版：2026-10-15 / 1.0', 'small')]

def footer(canvas, doc):
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(0.6)
    canvas.line(18 * mm, 18 * mm, 192 * mm, 18 * mm)
    canvas.setFont('JP', 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 13 * mm, 'Ele-Knowledge  |  法令RAG 取扱法令一覧  |  基準日 2026-10-01')
    canvas.drawRightString(192 * mm, 13 * mm, str(doc.page))

target = OUT / '法令RAG_取扱法令一覧_2026-10-15.pdf'
doc = SimpleDocTemplate(str(target), pagesize=(210 * mm, 297 * mm), rightMargin=18 * mm,
                        leftMargin=18 * mm, topMargin=17 * mm, bottomMargin=23 * mm,
                        title='Ele-Knowledge 法令RAG 取扱法令一覧', author='Ele-Knowledge',
                        subject='dev環境向け・53法令・一覧基準日2026-10-01')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f'Created {target.name}; verified {number} laws against CSV ({len(rows)} rows).')
