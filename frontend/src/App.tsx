import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { useEffect, useState } from "react";
import { ReviewNew } from "./pages/ReviewNew";
import { ReviewStatus } from "./pages/ReviewStatus";
import { AdminModel } from "./pages/AdminModel";
import { DemoModeBadge, DemoModeBanner } from "./components/DemoModeBadge";
import { getConfig } from "./api/client";
import type { RuntimeConfig } from "./api/types";

function App() {
  const [config, setConfig] = useState<RuntimeConfig | null>(null);

  useEffect(() => {
    getConfig()
      .then(setConfig)
      .catch(() => setConfig(null));
  }, []);

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="product-name">Legal Contract Risk Review</span>
        {config && <DemoModeBadge mode={config.deployment_mode} />}
        <nav>
          <NavLink to="/review/new">New review</NavLink>
          {/* P7: hidden in hosted demo mode — there is nothing to configure
              there (deterministic-only, D-05 stays open), and PUT /config
              is backend-locked in demo mode regardless of this UI hiding. */}
          {config?.deployment_mode !== "demo" && <NavLink to="/admin/model">Admin</NavLink>}
        </nav>
      </header>

      {config && <DemoModeBanner mode={config.deployment_mode} />}

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/review/new" replace />} />
          <Route path="/review/new" element={<ReviewNew />} />
          <Route path="/reviews/:reviewId" element={<ReviewStatus />} />
          <Route path="/admin/model" element={<AdminModel />} />
        </Routes>
      </main>

      <footer className="app-footer">
        <p>Decision support only, not legal advice. Prototype for Part 2 case study.</p>
      </footer>
    </div>
  );
}

export default App;
