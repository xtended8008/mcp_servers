# MCP Servers

A collection of Model Context Protocol (MCP) servers that extend AI assistants with specialized capabilities for various domains and tools.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that enables AI assistants to securely access external tools and data sources. MCP servers act as bridges between AI models and external systems, allowing assistants to perform actions like querying databases, managing infrastructure, or interacting with APIs.

## Available Servers

### Kubernetes MCP Server

Located in the `kubernetes/` directory, this server provides comprehensive Kubernetes cluster management capabilities for AI assistants.

**Features:**
- **Workloads**: List, describe, and manage pods and deployments
- **Cluster Infrastructure**: View nodes, namespaces, and services
- **Networking**: Inspect services and networking configuration
- **Helm Integration**: Manage Helm releases
- **Observability**: Access cluster events and logs

**Setup:**
- Requires Python 3.10+ and a valid `~/.kube/config`
- Install dependencies: `pip install -r kubernetes/requirements.txt`
- Configure in your MCP client (Claude Desktop, VS Code extensions, etc.)

For detailed setup instructions, see [kubernetes/README.md](kubernetes/README.md).

## Contributing

This repository welcomes contributions of new MCP servers for various domains:

1. Create a new directory for your server
2. Implement the MCP server using the FastMCP framework
3. Add a comprehensive README with setup instructions
4. Update this main README to include your server

## Requirements

- Python 3.10+
- MCP-compatible client (Claude Desktop, VS Code with MCP extensions, etc.)

## License

[Add your license here]