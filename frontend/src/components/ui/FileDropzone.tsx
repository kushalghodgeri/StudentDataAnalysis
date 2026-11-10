import React, { useCallback, useState } from "react";
import { useDropzone, FileRejection } from "react-dropzone";
import { UploadCloud, FileSpreadsheet, AlertCircle, CheckCircle2, X } from "lucide-react";
import { cn } from "../../lib/utils";

export interface FileDropzoneProps {
  onFileSelect: (file: File) => void;
  isUploading?: boolean;
  uploadProgress?: number;
  maxSizeBytes?: number; // default 15MB
  className?: string;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFileSelect,
  isUploading = false,
  uploadProgress = 0,
  maxSizeBytes = 15 * 1024 * 1024, // 15MB
  className,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], fileRejections: FileRejection[]) => {
      setErrorMessage(null);

      if (fileRejections.length > 0) {
        const rejection = fileRejections[0];
        if (rejection.errors.some((e) => e.code === "file-too-large")) {
          setErrorMessage(
            `File exceeds the ${(maxSizeBytes / (1024 * 1024)).toFixed(0)}MB maximum limit.`
          );
        } else if (rejection.errors.some((e) => e.code === "file-invalid-type")) {
          setErrorMessage("Invalid file format. Please upload a .csv or .xlsx file.");
        } else {
          setErrorMessage(rejection.errors[0]?.message || "Failed to accept file.");
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setSelectedFile(file);
        onFileSelect(file);
      }
    },
    [maxSizeBytes, onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    multiple: false,
    maxSize: maxSizeBytes,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/vnd.ms-excel": [".xls"],
    },
    disabled: isUploading,
  });

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFile(null);
    setErrorMessage(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className={cn("w-full space-y-3", className)}>
      <div
        {...getRootProps()}
        className={cn(
          "relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900",
          isDragActive && !isDragReject
            ? "border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/20 scale-[1.01]"
            : "border-slate-300 dark:border-slate-700 bg-slate-50/40 dark:bg-slate-800/20 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-slate-50 dark:hover:bg-slate-800/40",
          isDragReject && "border-rose-500 bg-rose-50/50 dark:bg-rose-950/20",
          isUploading && "pointer-events-none opacity-80"
        )}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center justify-center space-y-3">
          <div
            className={cn(
              "w-14 h-14 rounded-2xl flex items-center justify-center transition-colors shadow-sm",
              isDragActive
                ? "bg-indigo-600 text-white"
                : "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400"
            )}
          >
            <UploadCloud className="w-7 h-7" />
          </div>

          <div className="space-y-1">
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              {isDragActive ? (
                <span>Drop your student dataset here...</span>
              ) : (
                <span>
                  Drag & drop file here, or{" "}
                  <span className="text-indigo-600 dark:text-indigo-400 underline underline-offset-2">
                    browse
                  </span>
                </span>
              )}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Supports CSV, Excel (.xlsx, .xls) up to {Math.round(maxSizeBytes / (1024 * 1024))}MB
            </p>
          </div>
        </div>

        {/* Selected file card inside dropzone */}
        {selectedFile && !errorMessage && (
          <div
            onClick={(e) => e.stopPropagation()}
            className="mt-6 mx-auto max-w-md p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center justify-between text-left"
          >
            <div className="flex items-center gap-3 min-w-0">
              <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 shrink-0">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-slate-800 dark:text-slate-200 truncate">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
            </div>

            {!isUploading ? (
              <button
                type="button"
                onClick={removeFile}
                className="p-1 rounded-md text-slate-400 hover:text-rose-500 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                aria-label="Remove selected file"
              >
                <X className="w-4 h-4" />
              </button>
            ) : (
              <CheckCircle2 className="w-5 h-5 text-indigo-500 shrink-0 animate-pulse" />
            )}
          </div>
        )}
      </div>

      {/* Upload Progress Bar */}
      {isUploading && (
        <div className="space-y-1.5 p-3 bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/50 rounded-xl">
          <div className="flex justify-between text-xs font-medium text-indigo-700 dark:text-indigo-300">
            <span>Importing and cleaning data pipeline...</span>
            <span>{Math.round(uploadProgress)}%</span>
          </div>
          <div className="h-2 w-full bg-indigo-100 dark:bg-indigo-950 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-600 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${Math.max(5, Math.min(100, uploadProgress))}%` }}
            />
          </div>
        </div>
      )}

      {/* Error Message */}
      {errorMessage && (
        <div className="flex items-center gap-2 p-3 text-xs text-rose-700 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 rounded-xl">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};
