import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { ReviewNew } from "../src/pages/ReviewNew";

describe("ReviewNew upload screen", () => {
  it("renders the playbook summary card with real playbook facts", () => {
    render(
      <MemoryRouter>
        <ReviewNew />
      </MemoryRouter>,
    );

    const card = screen.getByRole("region", { name: /active playbook summary/i });
    expect(card).toHaveTextContent("defense-services-v1");
    expect(card).toHaveTextContent("1.0-draft");
    expect(card).toHaveTextContent("27");
    expect(card).toHaveTextContent(/confidentiality/i);
    expect(card).toHaveTextContent(/security incident response/i);
    expect(card).toHaveTextContent(/missing-clause findings/i);
  });

  it("renders the five-stage workflow strip", () => {
    render(
      <MemoryRouter>
        <ReviewNew />
      </MemoryRouter>,
    );

    expect(screen.getByText("Upload")).toBeInTheDocument();
    expect(screen.getByText("Parse")).toBeInTheDocument();
    expect(screen.getByText("Extract clauses")).toBeInTheDocument();
    expect(screen.getByText("Apply playbook")).toBeInTheDocument();
    expect(screen.getByText("Structured findings")).toBeInTheDocument();
  });

  it("uses honest, hosting-neutral processing language", () => {
    render(
      <MemoryRouter>
        <ReviewNew />
      </MemoryRouter>,
    );

    expect(screen.getByText(/processed on this server and never sent to a public ai service/i)).toBeInTheDocument();
    expect(screen.queryByText(/on-premises/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/on-prem\b/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/air-gapped/i)).not.toBeInTheDocument();
  });

  it("does not introduce fake metrics or ROI claims", () => {
    render(
      <MemoryRouter>
        <ReviewNew />
      </MemoryRouter>,
    );

    expect(screen.queryByText(/roi/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/hours saved/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/money saved/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/risks? prevented/i)).not.toBeInTheDocument();
  });

  it("preserves the upload form's drag-and-drop label and submit button", () => {
    render(
      <MemoryRouter>
        <ReviewNew />
      </MemoryRouter>,
    );

    expect(screen.getByLabelText(/drag and drop/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /review contract/i })).toBeInTheDocument();
  });
});
