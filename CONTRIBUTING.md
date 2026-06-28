# Contributing

Contributions are welcome. This is an open-source framework for running a cloud-GPU orchestrator
and humanoid RL training lifecycle manager as an agentic, human-in-the-loop workflow on UiPath
Maestro BPMN.

## Where to start

1. [`README.md`](./README.md) — what the project is and how it's built.
2. [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) — UiPath-core BPMN architecture.
3. [`samples/triggers/incident_report.schema.json`](./samples/triggers/incident_report.schema.json) — the canonical data model everything consumes.

## Working agreement

- **Day-to-day chat:** the project **Discord**.
- **All decisions land as GitHub issues; PRs reference the issue.** One commit = one logical change. Squash on merge.
- **Default branch:** `main`. Open a PR; no direct pushes.
- **Commit messages:** prefix with scope (`docs(readme):`, `samples(triggers):`, `bpmn:`, `agents:`, etc.).

## Setting up locally

The orchestration layer runs on **UiPath Automation Cloud** (Maestro BPMN is the mandatory core).
To work on the BPMN/agents you'll need:

1. **UiPath Automation Cloud** access + **UiPath Studio**.
2. **Coding agents** — Claude Code / Cursor / Gemini CLI via *UiPath for Coding Agents* are supported.

For local sample validation (no UiPath access needed):

```bash
python -m venv .venv
source .venv/bin/activate
pip install jsonschema
python -c "import jsonschema, json, glob; \
  schema = json.load(open('samples/triggers/incident_report.schema.json')); \
  [jsonschema.validate(json.load(open(f)), schema) for f in glob.glob('samples/triggers/*.json') if 'schema' not in f]"
```

## Stack constraint

UiPath Automation Cloud is the **mandatory orchestration layer**. External frameworks (LangChain,
CrewAI, AutoGen, custom Python agents) are welcome **as task nodes invoked from the UiPath BPMN flow** —
not as standalone replacements for the orchestration core.

## Reproducibility expectations

The project should be reproducible end-to-end from this repository. BPMN diagrams, agent definitions,
and API Workflow configurations are exported and committed under `artifacts/`. Never commit secrets,
`.env` files, or tenant URLs.

## License

[Apache License 2.0](./LICENSE). By contributing, you agree your contributions are licensed under the same terms.
