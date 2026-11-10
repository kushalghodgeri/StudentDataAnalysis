import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatCard } from "../components/ui/StatCard";

describe("StatCard Component", () => {
  it("renders title and value accurately", () => {
    render(
      <StatCard
        title="Average Marks"
        value="78.5"
        subtitle="Across all departments"
      />
    );
    expect(screen.getByText("Average Marks")).toBeInTheDocument();
    expect(screen.getByText("78.5")).toBeInTheDocument();
    expect(screen.getByText("Across all departments")).toBeInTheDocument();
  });

  it("renders loading skeleton when isLoading is true", () => {
    const { container } = render(
      <StatCard title="Total Students" value="500" isLoading={true} />
    );
    // Should render animated pulse skeleton
    const skeleton = container.querySelector(".animate-pulse");
    expect(skeleton).toBeInTheDocument();
  });

  it("renders badge and accent variant style", () => {
    render(
      <StatCard
        title="Pass Rate"
        value="91.2%"
        badge={<span data-testid="test-badge">High</span>}
        variant="emerald"
      />
    );
    expect(screen.getByTestId("test-badge")).toBeInTheDocument();
  });
});
