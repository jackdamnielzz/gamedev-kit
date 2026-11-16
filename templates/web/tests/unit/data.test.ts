// `npm run validate`: every content file parses against its zod schema.

import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { DATA_FILES } from "../../src/data/schemas";

describe("data files", () => {
  for (const [path, schema] of Object.entries(DATA_FILES)) {
    it(`${path} matches its schema`, () => {
      const result = schema.safeParse(JSON.parse(readFileSync(path, "utf8")));
      expect(result.success ? [] : result.error.issues).toEqual([]);
    });
  }
});
