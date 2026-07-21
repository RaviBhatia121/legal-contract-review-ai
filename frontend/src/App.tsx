import { NavLink, Route, Routes } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { ReviewNew } from "./pages/ReviewNew";
import { ReviewStatus } from "./pages/ReviewStatus";
import { AdminModel } from "./pages/AdminModel";
import { AdminPlaybook } from "./pages/AdminPlaybook";
import { Architecture } from "./pages/Architecture";

function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="brand">
          <img className="brand-mark" src="/favicon.svg" alt="" aria-hidden="true" />
          <span className="product-name">Legal Contract Risk Review</span>
        </span>
        <nav>
          <NavLink to="/" end>
            Dashboard
          </NavLink>
          <NavLink to="/review/new">New review</NavLink>
          <NavLink to="/architecture">Architecture</NavLink>
          <NavLink to="/admin/playbook">Playbook</NavLink>
          <NavLink to="/admin/model">Admin</NavLink>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/review/new" element={<ReviewNew />} />
          <Route path="/architecture" element={<Architecture />} />
          <Route path="/reviews/:reviewId" element={<ReviewStatus />} />
          <Route path="/admin/playbook" element={<AdminPlaybook />} />
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
