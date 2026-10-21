// 先輩チャット用の線画アイコン（16px、currentColor）。装飾なので読み上げ対象外にする。
const base = {
  width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor',
  strokeWidth: 1.75, strokeLinecap: 'round', strokeLinejoin: 'round', 'aria-hidden': true, focusable: false,
} as const;

export const CopyIcon = () => <svg {...base}><rect x="9" y="9" width="11" height="11" rx="2" /><path d="M5 15V6a2 2 0 0 1 2-2h8" /></svg>;
export const SendIcon = () => <svg {...base}><path d="M12 19V5" /><path d="m5 12 7-7 7 7" /></svg>;
export const StopIcon = () => <svg {...base}><rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor" /></svg>;
export const PlusIcon = () => <svg {...base}><path d="M12 5v14M5 12h14" /></svg>;
export const MenuIcon = () => <svg {...base}><path d="M4 7h16M4 12h16M4 17h16" /></svg>;
export const DotsIcon = () => <svg {...base}><circle cx="5" cy="12" r="1" fill="currentColor" /><circle cx="12" cy="12" r="1" fill="currentColor" /><circle cx="19" cy="12" r="1" fill="currentColor" /></svg>;
export const RetryIcon = () => <svg {...base}><path d="M4 12a8 8 0 0 1 14-5.3L20 9" /><path d="M20 4v5h-5" /><path d="M20 12a8 8 0 0 1-14 5.3L4 15" /><path d="M4 20v-5h5" /></svg>;
export const NoteIcon = () => <svg {...base}><path d="M5 4h10l4 4v12H5z" /><path d="M14 4v5h5M8 13h8M8 17h5" /></svg>;

/** 開閉できる見出し（<summary>）の先頭に置く小さな矢印。閉じていると ▸、開くと ▾ に回る（<details class="group"> の中で使う）。 */
export const DisclosureChevron = () => (
  <svg width={12} height={12} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"
    className="shrink-0 transition-transform group-open:rotate-90 motion-reduce:transition-none"><path d="m9 6 6 6-6 6" /></svg>
);
