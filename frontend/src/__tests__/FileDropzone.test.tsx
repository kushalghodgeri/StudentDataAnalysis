import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { FileDropzone } from "../components/ui/FileDropzone";

describe("FileDropzone Component", () => {
  it("renders drag & drop instructions", () => {
    const onSelect = vi.fn();
    render(<FileDropzone onFileSelect={onSelect} />);

    expect(screen.getByText(/Drag & drop file here/i)).toBeInTheDocument();
    expect(screen.getByText(/Supports CSV, Excel/i)).toBeInTheDocument();
  });

  it("displays upload progress indicator when isUploading is true", () => {
    const onSelect = vi.fn();
    render(
      <FileDropzone
        onFileSelect={onSelect}
        isUploading={true}
        uploadProgress={45}
      />
    );

    expect(screen.getByText(/Importing and cleaning data pipeline/i)).toBeInTheDocument();
    expect(screen.getByText("45%")).toBeInTheDocument();
  });
});
