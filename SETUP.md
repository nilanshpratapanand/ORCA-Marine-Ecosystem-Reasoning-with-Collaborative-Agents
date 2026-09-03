# ORCA — Dev Setup (do this once)

Follow top to bottom. Every command is its own line — **paste one at a time**
(Windows PowerShell does not support `&&`).

---

## 0. Install these first

| Tool | Version | Link | Note |
|---|---|---|---|
| Git | any | https://git-scm.com/download/win | — |
| **Python 3.12** | **3.12.x, NOT 3.13/3.14** | https://www.python.org/downloads/release/python-3129/ | tick **"Add python.exe to PATH"** in the installer |
| Node.js | LTS (20 or 22) | https://nodejs.org | — |
| VS Code | any | https://code.visualstudio.com | optional |

> Python 3.13+ breaks `pydantic` install (tries to compile Rust). Use **3.12**.
> If `python` opens the Microsoft Store, use `py -3.12` everywhere instead.

Close and reopen the terminal after installing. Check:

```
git --version
```
```
py -3.12 --version
```
```
node --version
```

---

## 1. Clone the repo

```
cd C:\Users\%USERNAME%\Desktop
```
```
git clone https://github.com/nilanshpratapanand/ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents.git
```
```
cd ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents
```

---

## 2. Backend (FastAPI)

```
cd backend
```
```
py -3.12 -m venv venv
```
```
venv\Scripts\activate
```

Your prompt should now start with `(venv)`. If activation errors in red:

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Press `Y`, then run `venv\Scripts\activate` again.

```
python -m pip install -r requirements.txt
```

### API key (optional but do it)

```
copy .env.example .env
```

Open `backend\.env` in Notepad, put a free Groq key after `GROQ_API_KEY=`
(get one at https://console.groq.com/keys), save.
Without a key the app still runs — it just uses templated answers.

### Run it

```
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs — try the `/query` endpoint with:

```json
{ "question": "Should I go fishing off Kerala today?", "role": "fisherman" }
```

You should get JSON back with an `agent_trace`. **Leave this terminal running.**

---

## 3. Frontend (React) — new terminal

```
cd C:\Users\%USERNAME%\Desktop\ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents\frontend
```
```
npm install
```
```
npm run dev
```

Open http://127.0.0.1:5173 — the backend (step 2) must be running.

---

## 4. Daily workflow (after setup)

Start work:
```
git pull
```

Backend (terminal 1):
```
cd backend
```
```
venv\Scripts\activate
```
```
python -m uvicorn app.main:app --reload
```

Frontend (terminal 2):
```
cd frontend
```
```
npm run dev
```

Save your work:
```
git add -A
```
```
git commit -m "what you changed"
```
```
git pull
```
```
git push
```

> Work on your own file/agent so commits don't clash. If `git pull` shows a
> conflict, ping the group before force-anything.

---

## 5. Common errors

| Error | Fix |
|---|---|
| `The token '&&' is not a valid statement separator` | You pasted two commands on one line. Paste them separately. |
| `Could not open requirements file` | You're in the wrong folder. `cd` into `backend` first. |
| `python` opens Microsoft Store | Use `py -3.12` instead of `python`, or turn off the alias: Settings → "Manage app execution aliases" → python.exe OFF |
| `Building wheel for pydantic-core ... error` / `link.exe not found` | Wrong Python version. Delete `venv`, recreate with `py -3.12 -m venv venv` |
| `venv\Scripts\activate` red error | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` → `Y` |
| Frontend shows "Backend unreachable" | Backend terminal isn't running / crashed. Restart step 2. |
| `git push` rejected | Run `git pull` first, resolve, then push. |

---

## What's in here

```
backend/app/
  main.py            FastAPI entry — POST /query, GET /llm-status
  schemas.py         request/response shapes
  agents/
    orchestrator.py  runs the agents in order, builds the trace
    language.py      detect query language, translate the answer back
    time_context.py  "today / kal / tomorrow morning" -> forecast day
    data_retrieval.py resolve region, pull the numbers (7 seeded regions)
    domain_advisory.py fisherman / researcher / disaster_ops framing + evidence
    reasoning.py     turn it into one readable answer (LLM or template)
    llm.py           provider cascade: Groq/Qwen + free-tier fallbacks
  data/sample_marine_data.json   seeded offline data
frontend/src/
  App.jsx            chat UI + agent trace + evidence panel
  api.js             the one file that calls the backend
docs/
  BUILD_GUIDE.md     how a question flows through the system
  contracts.md       original data-shape contract (being updated)
```
