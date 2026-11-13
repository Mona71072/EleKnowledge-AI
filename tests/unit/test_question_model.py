"""質問の文言から機種キーを読み取る（question_model、2026-11-12 itai 決定）。"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('question_model_under_test', ROOT / 'lambda/rag/rag-function/question_model.py')
qm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qm)


@pytest.mark.parametrize('question, expected', [
    ('アクシーズで戸開しない', 'AXIEZ'),
    ('ＡＸＩＥＺ の巻上機', 'AXIEZ'),
    ('アクシーズリンクスの据付', 'AXIEZ-LINKs'),
    ('AXIEZ-LINKs のドア', 'AXIEZ-LINKs'),
    ('AXIEZ LINKs のドア', 'AXIEZ-LINKs'),
    ('リンクスの UCMP', 'AXIEZ-LINKs'),
    ('LINKsでエラー', 'AXIEZ-LINKs'),
    ('ネクスキューブの群管理', 'NEXCUBE'),
    ('Nexcube Limited', 'NEXCUBE'),
    ('MELCITY の照明', 'メルシティ'),
    ('エスカの手すり', 'エスカレーター'),
    ('エスカレーターの手すり', 'エスカレーター'),
])
def test_one_model_is_read(question, expected):
    assert qm.model_from_question(question) == expected


@pytest.mark.parametrize('question', [
    'アクシーズとリンクスの違い',            # two models: do not narrow
    'AXIEZ と NEXCUBE を比べたい',
    'リンクスイッチの交換',                  # part of a katakana word
    'hyperlinks の設定',                     # part of a latin word
    'かごの走行中振動',                       # no model
    '', None, 123,
])
def test_no_single_model(question):
    assert qm.model_from_question(question) is None


def test_mentioned_models_keep_question_order():
    assert qm.mentioned_models('ネクスキューブとアクシーズリンクス') == ['NEXCUBE', 'AXIEZ-LINKs']


def test_notice_names_the_model():
    assert 'AXIEZ' in qm.notice('AXIEZ') and '画面の「機種」' in qm.notice('AXIEZ')
