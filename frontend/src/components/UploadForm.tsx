import { useState } from "react";
import type { FormEvent } from "react";

interface Props {
  onSubmit: (file: File) => void;
  submitting: boolean;
  errorMessage: string | null;
}

const ALLOWED_EXTENSIONS = [".pdf", ".docx"];
const MAX_BYTES = 15 * 1024 * 1024;

export function UploadForm({ onSubmit, submitting, errorMessage }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  function validate(candidate: File): string | null {
    const lowerName = candidate.name.toLowerCase();
    if (!ALLOWED_EXTENSIONS.some((ext) => lowerName.endsWith(ext))) {
      return "Upload a PDF or DOCX file.";
    }
    if (candidate.size > MAX_BYTES) {
      return "The file exceeds the 15 MB upload limit.";
    }
    return null;
  }

  function handleFileChange(candidate: File | null) {
    if (!candidate) {
      setFile(null);
      return;
    }
    const validationError = validate(candidate);
    if (validationError) {
      setLocalError(validationError);
      setFile(null);
      return;
    }
    setLocalError(null);
    setFile(candidate);
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!file) {
      setLocalError("Select a PDF or DOCX file to review.");
      return;
    }
    onSubmit(file);
  }

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <div
        className="dropzone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleFileChange(e.dataTransfer.files?.[0] ?? null);
        }}
      >
        <label htmlFor="file-input">
          Drag and drop a contract here, or browse to select a file.
        </label>
        <input
          id="file-input"
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
        />
        <p className="hint">Allowed: PDF or DOCX. Maximum 15 MB and 100 pages.</p>
      </div>

      {file && (
        <p className="selected-file">
          Selected: {file.name} ({Math.ceil(file.size / 1024)} KB)
        </p>
      )}

      {(localError || errorMessage) && (
        <p className="form-error" role="alert">
          {localError ?? errorMessage}
        </p>
      )}

      <button type="submit" disabled={submitting} className="primary-action">
        {submitting ? "Starting review..." : "Review contract"}
      </button>
    </form>
  );
}
