# GitHub Actions MCP Server

A Model Context Protocol (MCP) server for GitHub Actions, enabling AI assistants to manage workflows, trigger runs, and inspect CI/CD status.

## Features

*   **Workflows**:
    *   `list_workflows`: List all workflows in a repository.
    *   `trigger_workflow`: Dispatch a workflow (supports `workflow_dispatch`).
*   **Runs**:
    *   `list_workflow_runs`: List recent workflow runs with status filtering.
    *   `get_workflow_run`: Get details of a specific run.

## Setup

1.  **Prerequisites**:
    *   Python 3.10+
    *   A GitHub Personal Access Token (PAT) with `repo` and `workflow` scopes.

2.  **Environment Variables**:
    *   `GITHUB_PERSONAL_ACCESS_TOKEN`: Your GitHub PAT. (Also supports `GITHUB_TOKEN`).

3.  **Installation**:
    ```bash
    cd github
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

## Usage with VS Code (Claude Dev / Roo Code)

Add the following to your MCP settings configuration.

```json
{
  "mcpServers": {
    "github-actions": {
      "command": "/ABSOLUTE/PATH/TO/github/.venv/bin/python",
      "args": [
        "/ABSOLUTE/PATH/TO/github/server.py"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token-here"
      }
    }
  }
}
```
