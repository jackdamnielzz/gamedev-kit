// zod schemas for every content file in data/. One schema per file; `npm run validate`
// (tests/unit/data.test.ts) parses every file listed in DATA_FILES.

import { z } from "zod";

export const I18nSchema = z.record(z.string(), z.string().min(1));

export const DATA_FILES: Record<string, z.ZodType> = {
  "data/i18n/en.json": I18nSchema,
  // "data/feel.json": FeelSchema,   (GAME-FEEL.md, section 1)
};
