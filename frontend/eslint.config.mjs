import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";

export default defineConfig([
  ...nextVitals,
  {
    // 既存画面の state 更新・イベントハンドラの書き方を変えずに移行する。
    rules: {
      "react-hooks/immutability": "off",
      "react-hooks/set-state-in-effect": "off",
    },
  },
  // .d.mts は型宣言のみ（tsc で検査済み）。ESLint の既定パーサーでは解析できない
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts", "**/*.d.mts"]),
]);
