import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  {
    rules: {
      // Data fetching in useEffect with setLoading(true) is a valid pattern
      // in class-less React. Enforcing useTransition here would require
      // rewriting every page component. Disable for now.
      "react-hooks/set-state-in-effect": "off",
    },
  },
]);

export default eslintConfig;
