import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import test from "node:test";
import { ESLint } from "eslint";

const require = createRequire(import.meta.url);
const pluginRoot = path.dirname(require.resolve("@next/eslint-plugin-next"));
const { getRootDirs } = require(path.join(pluginRoot, "utils/get-root-dirs.js"));

test("Next lint retains page checks with the scoped glob replacement", async () => {
  const root = mkdtempSync(path.join(tmpdir(), "next-lint-glob-"));
  try {
    for (const name of ["app-one", "app-two", "other"]) {
      mkdirSync(path.join(root, name));
      mkdirSync(path.join(root, name, "pages"));
      writeFileSync(path.join(root, name, "pages", "index.js"), "export default function Page() {}");
    }
    writeFileSync(path.join(root, "app-file.txt"), "synthetic fixture");
    const normalized = root.replaceAll("\\", "/");
    const expected = ["app-one", "app-two"].map((name) => `${normalized}/${name}`);
    const context = (rootDir) => ({ cwd: root, settings: { next: { rootDir } } });
    // glob also returns matching files. Next uses only existing pages/app paths.
    const usableRoots = (input) => getRootDirs(context(input))
      .filter((candidate) => existsSync(path.join(candidate, "pages")))
      .map((candidate) => candidate.replaceAll("\\", "/")).sort();
    assert.deepEqual(getRootDirs({ cwd: root, settings: {} }), [root]);
    assert.deepEqual(usableRoots(`${normalized}/app-*`), expected);
    assert.deepEqual(usableRoots(`${normalized}/app-{one,two}`), expected);
    assert.deepEqual(usableRoots([`${normalized}/app-one`, `${normalized}/app-two`, null]), expected);
    assert.deepEqual(getRootDirs(context(`${normalized}/missing-*`)), []);
    assert.deepEqual(usableRoots(`${normalized}/app-*`.replaceAll("/", "\\")), expected);
    const eslint = new ESLint({
      overrideConfigFile: true,
      overrideConfig: [{
        files: ["**/*.jsx"],
        languageOptions: { parserOptions: { ecmaFeatures: { jsx: true } } },
        plugins: { "@next/next": require("@next/eslint-plugin-next") },
        settings: { next: { rootDir: `${normalized}/app-*` } },
        rules: { "@next/next/no-html-link-for-pages": "error" },
      }],
    });
    const [bad] = await eslint.lintText('export default () => <a href="/">Home</a>;', { filePath: "fixture.jsx" });
    assert.equal(bad.messages.filter((m) => m.ruleId === "@next/next/no-html-link-for-pages").length, 1);
    const [good] = await eslint.lintText('export default () => <a href="https://example.com/">External</a>;', { filePath: "fixture.jsx" });
    assert.equal(good.errorCount, 0);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
