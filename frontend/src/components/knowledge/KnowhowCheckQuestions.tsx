import { Button } from '@/components/ui/Button';
import {
  CHECK_KIND_LABELS,
  MAX_CHECK_QUESTIONS,
  countCheckCalls,
  createManualQuestion,
  type CheckQuestion,
  type CheckTarget,
} from '@/lib/knowhow-card-check.mjs';

const MAX_QUESTIONS = MAX_CHECK_QUESTIONS * 2;
const MAX_QUERY_LENGTH = 2000;
export const CHECK_TARGET_LABELS: Record<CheckTarget, string> = { normal: '技術KB', law: '法令KB' };
const targets = ['normal', 'law'] as const;

function isInvalidQuestion({ selected, text, targets: lanes }: CheckQuestion) {
  const query = text.trim();
  return selected && (!query || !lanes.length || Array.from(query).length > MAX_QUERY_LENGTH);
}

type Props = {
  questions: CheckQuestion[];
  onChange: (questions: CheckQuestion[]) => void;
  onStart: () => void;
  busy?: boolean;
};

function QuestionEditor({ question, number, onChange, onRemove }: {
  question: CheckQuestion;
  number: number;
  onChange: (question: CheckQuestion) => void;
  onRemove: () => void;
}) {
  const label = `質問 ${number}`;
  const invalid = isInvalidQuestion(question);
  return (
    <fieldset className="min-w-0 space-y-2 rounded-lg border border-gray-200 px-3 pb-3">
      <legend className="px-1 text-sm font-semibold text-gray-900">{label} · {CHECK_KIND_LABELS[question.kind]}</legend>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <label className="flex items-center gap-2 text-sm text-gray-800">
          <input type="checkbox" checked={question.selected} onChange={(event) => onChange({ ...question, selected: event.target.checked })} />
          この質問を照合する
        </label>
        <Button type="button" variant="ghost" size="sm" aria-label={`${label}を削除`} onClick={onRemove}>削除</Button>
      </div>
      <textarea
        aria-label={label}
        aria-invalid={invalid}
        value={question.text}
        onChange={(event) => onChange({ ...question, text: event.target.value })}
        rows={2}
        className="block w-full resize-y rounded-lg border border-gray-300 px-3 py-2 text-sm leading-6 text-gray-900 focus-visible:outline-2 focus-visible:outline-blue-600"
      />
      <div className="flex flex-wrap gap-x-5 gap-y-2">
        {targets.map((target) => (
          <label className="flex items-center gap-2 text-sm text-gray-800" key={target}>
            <input type="checkbox" checked={question.targets.includes(target)} onChange={(event) => onChange({
              ...question,
              targets: event.target.checked
                ? [...question.targets, target]
                : question.targets.filter((current) => current !== target),
            })} />
            {CHECK_TARGET_LABELS[target]}
          </label>
        ))}
      </div>
      {question.sourceText && (
        <details className="break-words text-xs leading-5 text-gray-700">
          <summary className="cursor-pointer">カード内の参照箇所{question.sourceSection && ` · ${question.sourceSection}`}</summary>
          <p className="mt-1 whitespace-pre-wrap">{question.sourceText}</p>
        </details>
      )}
    </fieldset>
  );
}

export function KnowhowCheckQuestions({ questions, onChange, onStart, busy }: Props) {
  const counts = countCheckCalls(questions);
  const invalid = questions.some(({ selected, text, targets: lanes }) => selected
    && (!text.trim() || Array.from(text.trim()).length > MAX_QUERY_LENGTH || !lanes.length));
  return (
    <div className="space-y-4">
      <h3 className="text-base font-semibold text-gray-950">照合する質問を確認</h3>
      {questions.length === 0 && <p className="text-sm text-gray-700">照合したい質問を追加してください。</p>}
      <div className="space-y-3">
        {questions.map((question, index) => (
          <QuestionEditor key={question.id} question={question} number={index + 1}
            onChange={(updated) => onChange(questions.map((current) => current.id === question.id ? updated : current))}
            onRemove={() => onChange(questions.filter((current) => current.id !== question.id))} />
        ))}
      </div>
      <Button type="button" variant="outline" size="sm" disabled={questions.length >= MAX_QUESTIONS}
        onClick={() => onChange([...questions, createManualQuestion(questions, '')])}>
        質問を追加
      </Button>
      <div className="space-y-2 rounded-lg bg-blue-50 p-3">
        <p className="text-sm font-semibold text-gray-900">{counts.questions}問 · 技術KB {counts.normal}回・法令KB {counts.law}回</p>
        <p className="text-xs leading-5 text-gray-700">選んだ質問文が検索APIに送信され、チャット履歴に保存される場合があります。検索ごとに利用料が発生します。</p>
        {invalid && <p className="text-sm text-red-800">選んだ質問を2,000文字以内で入力し、照合先を選んでください。</p>}
        <Button type="button" disabled={busy || invalid || counts.total === 0} onClick={onStart}>照合する</Button>
      </div>
    </div>
  );
}
