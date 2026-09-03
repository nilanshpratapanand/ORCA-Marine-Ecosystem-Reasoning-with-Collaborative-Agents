# ORCA — Dev Setup (do this once)

Follow top to bottom. **Paste ONE command at a time** and wait for it to finish
(Windows PowerShell does not support `&&`, and if you paste a block it silently
skips lines).

**Do not skip a step. Do not run these in `C:\WINDOWS\system32`** — if your
prompt says `system32`, you forgot the `cd` in step 1.

> **Shortcut:** on Windows you can just clone the repo and double-click
> **`setup.bat`** (then `run.bat`). This page is the manual version + the
> troubleshooting table for when something breaks.

---

## 0. Install these first

| Tool | Version | Link | Note |
|---|---|---|---|
| Git | any | https://git-scm.com/download/win | — |
| **Python 3.12** | **3.12.x — NOT 3.13 / 3.14** | https://www.python.org/downloads/release/python-3129/ | tick **"Add python.exe to PATH"** in the installer |
| Node.js | LTS (20 or 22) | https://nodejs.org | — |
| VS Code | any | https://code.visualstudio.com | optional |

> **Why 3.12 and not newer:** on 3.13/3.14 the `pydantic` install has no
> prebuilt file and tries to compile Rust → fails with `link.exe not found`.
> 3.12 just works. The whole team must be on the same version.

Close and reopen the terminal after installing, then check all three:

```
git --version
```
```
py -3.12 --version
```
```
node --version
```

`py -3.12 --version` must print `Python 3.12.x`. If it says "can't find 3.12",
Python 3.12 isn't installed — go back and install it.

> **Never type bare `python`** on Windows — it can open a "Select an app to open
> python" popup (a broken Store alias). Use **`py -3.12`** outside a venv, and
> plain `python` only *inside* an activated venv (there it's safe).

---

## 1. Clone the repo

```
cd $HOME\Desktop
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

**Create the virtual environment (do NOT skip this line):**

```
py -3.12 -m venv venv
```

That takes ~20 sec and creates a `venv\` folder. Now activate it:

```
venv\Scripts\activate
```

### ✅ CHECKPOINT — stop and look at your prompt

It must now start with **`(venv)`**, like:

```
(venv) PS C:\Users\...\backend>
```

- **No `(venv)`?** Activation didn't work. Everything after this will fail.
  Fix: run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` → press `Y` →
  run `venv\Scripts\activate` again. Still nothing? You skipped
  `py -3.12 -m venv venv` — run it.

Once you see `(venv)`, continue:

```
python -m pip install -r requirements.txt
```

### API key (optional — app runs without it)

```
copy .env.example .env
```

Open `backend\.env` in Notepad, paste a free Groq key after `GROQ_API_KEY=`
(get one: https://console.groq.com/keys), save. No key = templated answers,
still fully works.

### Run it

```
python -m uvicorn app.main:app --reload
```

Wait for `Application startup complete`. Open http://127.0.0.1:8000/docs,
expand `POST /query` → "Try it out" → paste:

```json
{ "question": "Should I go fishing off Kerala today?", "role": "fisherman" }
```

Execute → you get JSON back with an `agent_trace` list = backend works.
**Leave this terminal running.**

---

## 3. Frontend (React) — open a SECOND terminal

```
cd $HOME\Desktop\ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents\frontend
```
```
npm install
```
```
npm run dev
```

Open http://127.0.0.1:5173 — the backend (step 2) must still be running in the
other terminal.

---

## 4. Daily workflow (after the one-time setup above)

**Start of session:**
```
cd $HOME\Desktop\ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents
```
```
git pull
```

**Backend — terminal 1:**
```
cd backend
```
```
venv\Scripts\activate
```
```
python -m uvicorn app.main:app --reload
```
(no `py -3.12 -m venv venv` again — the venv already exists)

**Frontend — terminal 2:**
```
cd frontend
```
```
npm run dev
```

**Save your work:**
```
git add -A
```
```
git commit -m "short note on what you changed"
```
```
git pull
```
```
git push
```

> Each person owns their own file/agent so commits don't clash. If `git pull`
> reports a conflict, tell the group before doing anything drastic.

---

## 5. Common errors

| What you see | Fix |
|---|---|
| Prompt says `PS C:\WINDOWS\system32>` | You didn't `cd` into the project. Do step 1. |
| `The token '&&' is not a valid statement separator` | You pasted 2+ commands on one line. Paste them one at a time. |
| `venv\Scripts\activate` runs but **no `(venv)` appears** | venv wasn't created or policy blocked it. Run `py -3.12 -m venv venv`, then `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` → `Y`, then activate again. |
| "Select an app to open **python**" popup | You typed bare `python` outside a venv. Close the popup. Use `py -3.12`, or activate the venv first. |
| `Could not open requirements file` | Wrong folder — `cd backend` first, and make sure `(venv)` is showing. |
| `Building wheel for pydantic-core ... error` / `link.exe not found` | venv was made with Python 3.13/3.14. Delete the `venv` folder, run `py -3.12 -m venv venv` again. |
| `py -3.12` → "can't find" | Python 3.12 not installed. Step 0. |
| Frontend page: "Backend unreachable" | Backend terminal isn't running or crashed. Restart step 2's run command. |
| `git push` rejected (`fetch first`) | `git pull` first, fix any conflict, then `git push`. |

---

## What's in here

```
backend/app/
  main.py            FastAPI entry — POST /query, GET /llm-status
  schemas.py         request/response shapes
  agents/
    orchestrator.py    runs the agents in order, builds the trace
    language.py        detect query language, translate the answer back
    time_context.py    "today / kal / tomorrow morning" -> forecast day
    data_retrieval.py  resolve region, pull the numbers (7 seeded regions)
    domain_advisory.py fisherman / researcher / disaster_ops framing + evidence
    reasoning.py       turn it into one readable answer (LLM or template)
    llm.py             provider cascade: Groq/Qwen + free-tier fallbacks
  data/sample_marine_data.json   seeded offline data
frontend/src/
  App.jsx            chat UI + agent trace + evidence panel
  api.js             the one file that calls the backend
docs/
  BUILD_GUIDE.md     how a question flows through the system
  contracts.md       original data-shape contract (being updated)
```
