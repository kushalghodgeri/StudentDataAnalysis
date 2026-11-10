import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FilterBar } from "../components/ui/FilterBar";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

describe("FilterBar Component", () => {
  it("renders semester and department selector controls", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/"]}>
          <FilterBar />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByLabelText(/filter by semester/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/filter by department/i)).toBeInTheDocument();
    expect(screen.getByText("All Semesters")).toBeInTheDocument();
    expect(screen.getByText("All Departments")).toBeInTheDocument();
  });

  it("shows active filter badge and clear button when query params are present", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/?semester=2&department=Computer+Science"]}>
          <FilterBar />
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText(/Sem 2/i)).toBeInTheDocument();
    expect(screen.getAllByText("Computer Science").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByLabelText("Clear department filter")).toBeInTheDocument();
    expect(screen.getByLabelText("Clear semester filter")).toBeInTheDocument();
    expect(screen.getByText(/Clear filters/i)).toBeInTheDocument();
  });
});
