import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Badge, getGradeBadgeVariant } from "../components/ui/Badge";

describe("Badge Component", () => {
  it("renders children content correctly", () => {
    render(<Badge>Test Badge</Badge>);
    expect(screen.getByText("Test Badge")).toBeInTheDocument();
  });

  it("applies grade variants correctly", () => {
    expect(getGradeBadgeVariant("A")).toBe("grade-A");
    expect(getGradeBadgeVariant("B")).toBe("grade-B");
    expect(getGradeBadgeVariant("C")).toBe("grade-C");
    expect(getGradeBadgeVariant("D")).toBe("grade-D");
    expect(getGradeBadgeVariant("F")).toBe("grade-F");
    expect(getGradeBadgeVariant("Z")).toBe("default");
  });

  it("renders with custom className", () => {
    render(<Badge className="custom-class">Custom</Badge>);
    const badge = screen.getByText("Custom");
    expect(badge).toHaveClass("custom-class");
  });
});
