# Kubernetes MCP Server

A Model Context Protocol (MCP) server for Kubernetes, allowing AI assistants to inspect and troubleshoot clusters directly.

## Features

This server provides a comprehensive set of tools for DevOps and SRE workflows:

*   **Workloads**:
    *   `list_pods`: View pod status, restarts, and age.
    *   `describe_pod`: Get detailed configuration and events for a specific pod.
    *   `get_pod_logs`: Fetch logs for troubleshooting.
    *   `list_deployments`: View deployment status (replicas, available, etc.).
    *   `scale_deployment`: Scale replicas up or down.
    *   `restart_deployment`: Trigger a rollout restart.
*   **Cluster & Infrastructure**:
    *   `list_nodes`: Check node health and roles.
    *   `list_namespaces`: View cluster namespaces.
*   **Networking**:
    *   `list_services`: Inspect services, ports, and IPs.
*   **Helm**:
    *   `list_helm_releases`: List Helm releases in a namespace.
    *   `get_helm_release`: Get detailed status and notes for a release.
    *   `uninstall_helm_release`: Uninstall a Helm release.
*   **Observability**:
    *   `list_events`: View recent cluster events for root cause analysis.

## Setup

1.  **Prerequisites**:
    *   Python 3.10+
    *   `uv` (recommended) or `pip`
    *   A valid `~/.kube/config` file.

2.  **Installation**:
    ```bash
    git clone <repository_url>
    cd k8s
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

## Usage with VS Code (Claude Dev / Roo Code)

To use this server with MCP-enabled VS Code extensions (like Claude Dev, Roo Code, or the official Claude extension), add the following configuration to your settings.

**1. Locate your config file:**
*   **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json`
*   **VS Code Extensions**: Check the extension settings for "MCP Servers" or "Config Path".

**2. Add the server configuration:**

Replace `/ABSOLUTE/PATH/TO/` with the actual path to this directory.

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "/ABSOLUTE/PATH/TO/k8s/.venv/bin/python",
      "args": [
        "/ABSOLUTE/PATH/TO/k8s/server.py"
      ]
    }
  }
}
```

**Example (MacOS/Linux):**

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "/Users/dutnallb/Documents/github/mcp_servers/k8s/.venv/bin/python",
      "args": [
        "/Users/dutnallb/Documents/github/mcp_servers/k8s/server.py"
      ]
    }
  }
}
```

## Running Manually

You can test the server manually using the MCP CLI or by running the script directly (it uses FastMCP).

```bash
.venv/bin/python server.py
```
