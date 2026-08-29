// api.js — the ONLY file that talks to the backend.
// Keeping every fetch() call in one place means when the API contract
// changes, you edit one file, not every component.

const API_BASE = "http://127.0.0.1:8000";

export async function askOrca(question, role, region = null) {
  const res = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, role, region }),
  });

  if (!res.ok) {
    throw new Error(`Backend returned ${res.status}`);
  }
  return res.json();
}
