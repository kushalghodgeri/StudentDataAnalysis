import { describe, it, expect } from "vitest";
import {
  formatMarks,
  formatPercent,
  formatInteger,
  formatDate,
  formatDateTime,
} from "../lib/formatters";

describe("Formatting Utilities", () => {
  it("formats marks correctly with 1 decimal", () => {
    expect(formatMarks(85.456)).toBe("85.5");
    expect(formatMarks(70)).toBe("70.0");
    expect(formatMarks(null)).toBe("N/A");
    expect(formatMarks(undefined)).toBe("N/A");
    expect(formatMarks(NaN)).toBe("N/A");
  });

  it("formats percentages with % sign", () => {
    expect(formatPercent(92.34)).toBe("92.3%");
    expect(formatPercent(100)).toBe("100.0%");
    expect(formatPercent(null)).toBe("N/A");
    expect(formatPercent(undefined)).toBe("N/A");
  });

  it("formats integers with locale grouping", () => {
    expect(formatInteger(1250)).toBe("1,250");
    expect(formatInteger(0)).toBe("0");
    expect(formatInteger(null)).toBe("0");
  });

  it("formats date strings safely", () => {
    expect(formatDate(null)).toBe("N/A");
    expect(formatDate("2024-05-15")).toContain("2024");
  });

  it("formats datetime strings safely", () => {
    expect(formatDateTime(null)).toBe("N/A");
    expect(formatDateTime("2024-05-15T10:30:00Z")).toContain("2024");
  });
});
