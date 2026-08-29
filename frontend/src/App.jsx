import { useState } from "react";
import { askOrca } from "./api";

const ROLES = [
  { value: "fisherman", label: "Fisherman" },
  { value: "researcher", label: "Researcher" },
  { value: "disaster_ops", label: "Disaster-Ops" },
];

export default function App() {
  const [role, setRole] = useState("fisherman");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]); // {question, response, error}
  const [loading, setLoading] = useState(false);

  async function handleAsk(e) {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    const q = question;
    setQuestion("");
    try {
      const response = await askOrca(q, role);
      setMessages((m) => [...m, { question: q, response }]);
    } catch (err) {
      setMessages((m) => [...m, { question: q, error: err.message }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <h1 style={styles.h1}>ORCA</h1>
        <p style={styles.sub}>Marine Ecosystem Reasoning with Collaborative Agents — SIH PS #26176</p>
      </header>

      <div style={styles.roleRow}>
        <label style={styles.label}>Viewing as: </label>
        {ROLES.map((r) => (
          <button
            key={r.value}
            onClick={() => setRole(r.value)}
            style={{
              ...styles.roleBtn,
              ...(role === r.value ? styles.roleBtnActive : {}),
            }}
          >
            {r.label}
          </button>
        ))}
      </div>

      <div style={styles.chatWindow}>
        {messages.length === 0 && (
          <div style={styles.placeholder}>
            <p style={{ margin: "0 0 6px" }}>Try:</p>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              <li>"Is it safe to venture into the sea off Odisha tomorrow morning?"</li>
              <li>"Should I go fishing near Visakhapatnam today?"</li>
              <li>"kal mumbai ke paas machli pakadne jaana theek hai?"</li>
              <li>"What's the cyclone risk on the Bay of Bengal?"</li>
            </ul>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={styles.exchange}>
            <div style={styles.userBubble}>{m.question}</div>
            {m.error ? (
              <div style={styles.errorBanner}>⚠ Backend unreachable: {m.error}. Is `uvicorn app.main:app --reload` running?</div>
            ) : (
              <div style={styles.answerBubble}>
                <div style={{ whiteSpace: "pre-wrap" }}>{m.response.answer}</div>

                <div style={styles.chips}>
                  {m.response.detected_language && (
                    <span style={styles.chip}>🗣 {m.response.detected_language}</span>
                  )}
                  {m.response.time_scope && (
                    <span style={styles.chip}>🕑 {m.response.time_scope}</span>
                  )}
                  {m.response.region_used && (
                    <span style={styles.chip}>
                      📍 {m.response.region_used}
                      {m.response.region_match && m.response.region_match !== "named"
                        ? ` (${m.response.region_match})`
                        : ""}
                    </span>
                  )}
                  <span style={styles.chip}>✅ confidence {m.response.confidence}</span>
                </div>

                {m.response.data_freshness_warning && (
                  <div style={styles.warning}>⏱ {m.response.data_freshness_warning}</div>
                )}

                {m.response.evidence && m.response.evidence.length > 0 && (
                  <details style={styles.trace}>
                    <summary>Why — evidence used</summary>
                    <ul>
                      {m.response.evidence.map((e, j) => (
                        <li key={j}>{e}</li>
                      ))}
                    </ul>
                  </details>
                )}

                <details style={styles.trace}>
                  <summary>Agent trace ({m.response.agent_trace.length} agents fired) — click for judge Q&A proof</summary>
                  <ul>
                    {m.response.agent_trace.map((t, j) => (
                      <li key={j}>
                        <strong>{t.agent}</strong>: {t.action}
                        {t.confidence != null && ` (confidence ${t.confidence})`}
                      </li>
                    ))}
                  </ul>
                </details>
              </div>
            )}
          </div>
        ))}
        {loading && <div style={styles.placeholder}>Agents thinking…</div>}
      </div>

      <form onSubmit={handleAsk} style={styles.form}>
        <input
          style={styles.input}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask ORCA a question…"
        />
        <button type="submit" style={styles.sendBtn} disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
}

// Inline styles to keep this a single file for now — swap for CSS modules
// or Tailwind once the team has bandwidth for polish. Function over form first.
const styles = {
  page: { maxWidth: 720, margin: "0 auto", padding: 24, fontFamily: "system-ui, sans-serif" },
  header: { marginBottom: 16 },
  h1: { margin: 0, fontSize: 32 },
  sub: { margin: 0, color: "#666", fontSize: 14 },
  roleRow: { display: "flex", alignItems: "center", gap: 8, marginBottom: 16 },
  label: { fontSize: 14, color: "#444" },
  roleBtn: { padding: "6px 12px", borderRadius: 16, border: "1px solid #ccc", background: "#fff", cursor: "pointer" },
  roleBtnActive: { background: "#1a73e8", color: "#fff", borderColor: "#1a73e8" },
  chatWindow: { border: "1px solid #ddd", borderRadius: 8, minHeight: 320, padding: 16, marginBottom: 16, background: "#fafafa" },
  placeholder: { color: "#999", fontStyle: "italic" },
  exchange: { marginBottom: 16 },
  userBubble: { fontWeight: 600, marginBottom: 6 },
  answerBubble: { background: "#fff", border: "1px solid #e0e0e0", borderRadius: 8, padding: 12 },
  warning: { color: "#a35a00", fontSize: 13, marginTop: 8 },
  chips: { display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 },
  chip: { fontSize: 11, background: "#eef2f7", color: "#334", borderRadius: 10, padding: "2px 8px" },
  trace: { marginTop: 8, fontSize: 12, color: "#555" },
  errorBanner: { color: "#b00020", background: "#fdecea", padding: 8, borderRadius: 6 },
  form: { display: "flex", gap: 8 },
  input: { flex: 1, padding: 10, borderRadius: 6, border: "1px solid #ccc", fontSize: 14 },
  sendBtn: { padding: "10px 20px", borderRadius: 6, border: "none", background: "#1a73e8", color: "#fff", cursor: "pointer" },
};
