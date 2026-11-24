# ScoutBot

ScoutBot is a small AI agent that triages customer support tickets with Claude. For each ticket it looks up the customer, can ask a human to approve an escalation, can check a payment provider's status page, and finally returns a priority, a category and a suggested owner. Its dependencies (the LLM client, the customer data and the approval step) are passed in from `main.py`, so the triage loop can be tested with a fake client and no API key.

## Setup

### 1. Clone the repository

```bash
git clone git@github.com:CarSomma/scoutbot.git
```

---

### 2. Navigate into the folder

```bash
cd scoutbot
```

---

### 3. Install dependencies

```bash
uv sync
```

This creates a `.venv/` folder with Python 3.13 and every package the project needs.

---

### 4. Add your API key

Copy the template and fill in your Anthropic API key:

```bash
cp .env.example .env
```

Open `.env` and replace `your-anthropic-key-here` with your key from the [Claude Console](https://platform.claude.com/).

> [!CAUTION]
> `.env` holds your secret API key. Never commit it. It is already listed in `.gitignore`; only `.env.example`, with placeholder values, belongs in the repository.

> [!TIP]
> ScoutBot uses `claude-haiku-4-5` by default. To try another model, add `ANTHROPIC_MODEL=<model-id>` to `.env`.

---

### 5. Run ScoutBot

Run the command from the repository root, so `.env` is found:

```bash
uv run scoutbot
```

The agent triages each sample ticket and prints the result as JSON. When the model wants to escalate a ticket, it asks you in the terminal:

```text
Model wants to escalate to a human.
Reason: ...
Approve? [y/N]
```

> [!NOTE]
> Every run calls the Anthropic API and uses tokens from your account.

---

### 6. Run the tests

```bash
uv run pytest
```

The tests use a fake client, so they need no API key and cost no tokens.

## References & Further Reading

**Documentation**

- [Tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview): How Claude decides to call tools and how you return results
- [Implement tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use): Tool definitions, `tool_result` blocks and strict schemas
- [Server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools): Tools that run on Anthropic's side, like the web fetch tool ScoutBot uses
- [Web fetch tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool): Allowed domains, usage limits and result blocks
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/): Defining and validating data with `BaseModel`
- [Pydantic settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/): Loading configuration from environment variables and `.env` files
- [pytest: Get started](https://docs.pytest.org/en/stable/getting-started.html): Writing and running your first tests
- [uv projects](https://docs.astral.sh/uv/concepts/projects/): How `pyproject.toml`, `uv.lock` and `uv run` work together

**Design and testing**

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents): Anthropic's guide to agent patterns and when to keep them simple
- [Inversion of Control Containers and the Dependency Injection pattern](https://martinfowler.com/articles/injection.html): Martin Fowler's classic article on passing dependencies in
- [Test Double](https://martinfowler.com/bliki/TestDouble.html): The vocabulary behind fakes, stubs and mocks
- [Code smells catalogue](https://refactoring.guru/refactoring/smells): Common smells and the refactorings that fix them
