# AGENTS.md: Operational Protocol for 9F64B3

## 1. Project Overview & Core Mission
Project 9F64B3 is a high-performance, modular framework designed for autonomous agent orchestration. The mission is to provide a deterministic, type-safe environment for executing multi-agent workflows with minimal latency and zero-trust memory management. Agents are expected to maintain strict adherence to the dependency injection patterns defined in `ARCHITECTURE.md`.

## 2. Local PowerShell Commands
All operations must be executed from the project root.

*   **Setup:** `python -m venv .venv && .\.venv\Scripts\Activate.ps1 && pip install -r requirements.txt`
*   **Test:** `pytest tests/ --cov=src --cov-report=term-missing --durations=10`
*   **Run:** `python -m src.main --config ./configs/prod.yaml`
*   **Lint:** `mypy src/ --strict && flake8 src/ --max-line-length=88 && black --check src/`
*   **Clean:** `Get-ChildItem -Path . -Filter "__pycache__" -Recurse | Remove-Item -Force -Recurse`

## 3. Engineering Invariants
*   **Zero-Placeholder Mandate:** No `TODO`, `FIXME`, or `// TODO` comments are permitted in production code. If a feature is incomplete, the code path must raise `NotImplementedError` with a specific tracking ID.
*   **Typing Strictness:** All functions must include PEP 484 type hints. Use `from typing import Any, Dict, List, Optional, Union, Callable`. No `Any` usage allowed in core logic; use `Protocol` or `TypeVar` for generic constraints.
*   **CRLF/LF Preservation:** The repository enforces `LF` line endings. Ensure `.gitattributes` is respected. Agents must not introduce `CRLF` sequences.
*   **Immutability:** Prefer `dataclasses` with `frozen=True` for state objects. Global state is strictly forbidden.
*   **Dependency Injection:** All external services (DB, API, LLM clients) must be injected via constructors.

## 4. Self-Healing & Error Recovery Protocol
When an agent encounters a traceback or runtime failure:

1.  **Traceback Capture:** Extract the full stack trace. Do not truncate.
2.  **Contextual Analysis:** Identify the entry point of the failure. Check `logs/error.log` for the state of the `AgentContext` object at the time of failure.
3.  **Hypothesis Generation:** Formulate a fix based on the `ARCHITECTURE.md` dependency graph.
4.  **Local Reproduction:** Create a minimal reproduction script in `tests/repro_*.py`.
5.  **Verification:** Apply the fix, run the reproduction script, and execute the full test suite.
6.  **Cleanup:** Delete the reproduction script before committing.

*If the error involves a dependency mismatch, verify `requirements.txt` against `pip freeze` and update the lockfile.*

## 5. Definition of Done (DoD) Quality Gate
A task is considered complete only when the following criteria are met:

*   **Functional:** All requirements in `PRD.md` are satisfied.
*   **Test Coverage:** 95%+ line coverage verified by `pytest-cov`.
*   **Static Analysis:** `mypy --strict` returns zero errors.
*   **Documentation:** All public methods and classes have Google-style docstrings.
*   **Performance:** Execution time for core loops does not exceed the budget defined in `ARCHITECTURE.md`.
*   **Integration:** The code passes the CI pipeline simulation (linting, unit tests, and integration tests).
*   **Cleanup:** No temporary files, debug prints, or commented-out code blocks remain.