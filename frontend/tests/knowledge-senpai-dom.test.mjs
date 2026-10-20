import assert from 'node:assert/strict';
import test from 'node:test';
import { openAncestorDetails, shouldRestoreComposerFocus } from '../src/lib/knowledge-senpai-dom.mjs';
import { attachMenuDismissal } from '../src/lib/knowledge-senpai-menu.mjs';

test('the composer gets focus back only after it was disabled and focus fell to the page', () => {
  const body = {};
  assert.equal(shouldRestoreComposerFocus({ wasDisabled: true, disabled: false, activeElement: body, body }), true);
  assert.equal(shouldRestoreComposerFocus({ wasDisabled: true, disabled: false, activeElement: null, body }), true);
  assert.equal(shouldRestoreComposerFocus({ wasDisabled: true, disabled: false, activeElement: {}, body }), false, 'focus the user moved elsewhere is kept');
  assert.equal(shouldRestoreComposerFocus({ wasDisabled: false, disabled: false, activeElement: body, body }), false);
  assert.equal(shouldRestoreComposerFocus({ wasDisabled: true, disabled: true, activeElement: body, body }), false);
});

test('openAncestorDetails opens every closed <details> around an anchor target', () => {
  const outer = { open: false };
  const inner = { open: false, parentElement: { closest: () => outer } };
  const target = { parentElement: { closest: () => inner } };
  assert.equal(openAncestorDetails(target), 2);
  assert.equal(outer.open && inner.open, true);
  assert.equal(openAncestorDetails(target), 0, 'already open: nothing to do');
  assert.equal(openAncestorDetails({ parentElement: { closest: () => null } }), 0);
  assert.equal(openAncestorDetails(null), 0);
});

function fakeTarget() {
  const handlers = new Map();
  return {
    handlers,
    addEventListener: (type, fn) => handlers.set(type, fn),
    removeEventListener: (type, fn) => { if (handlers.get(type) === fn) handlers.delete(type); },
  };
}
const inside = { closest: (selector) => (selector === '[data-senpai-menu]' ? {} : null) };
const outside = { closest: () => null };

test('the menu closes on outside press, focus leaving it and Escape, and says why', () => {
  const target = fakeTarget();
  const reasons = [];
  const detach = attachMenuDismissal(target, (reason) => reasons.push(reason));
  target.handlers.get('pointerdown')({ target: outside });
  target.handlers.get('pointerdown')({ target: inside });
  target.handlers.get('focusin')({ target: inside });
  target.handlers.get('focusin')({ target: outside });
  target.handlers.get('keydown')({ key: 'Enter' });
  target.handlers.get('keydown')({ key: 'Escape' });
  assert.deepEqual(reasons, ['outside', 'focus', 'escape']);
  detach();
  assert.equal(target.handlers.size, 0);
});
