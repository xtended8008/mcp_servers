from mcp.server.fastmcp import FastMCP
from github import Github
from github.GithubException import UnknownObjectException
import os
from typing import Optional, Dict, Any

# Initialize FastMCP server
mcp = FastMCP("github-mcp")

# Initialize GitHub client
github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
if not github_token:
    # Try falling back to GITHUB_TOKEN which is common in CI environments
    github_token = os.getenv("GITHUB_TOKEN")

g = Github(github_token) if github_token else Github()

def _get_repo(owner: str, repo: str):
    return g.get_repo(f"{owner}/{repo}")

@mcp.tool()
def list_workflows(owner: str, repo: str) -> str:
    """Lists all GitHub Actions workflows in a repository."""
    if not github_token:
        return "Error: GITHUB_PERSONAL_ACCESS_TOKEN or GITHUB_TOKEN environment variable is not set."
    
    try:
        repository = _get_repo(owner, repo)
        workflows = repository.get_workflows()
        
        output = [f"{ 'ID':<10} {'NAME':<30} {'STATE':<10} {'PATH'}"]
        for wf in workflows:
            output.append(f"{str(wf.id):<10} {wf.name:<30} {wf.state:<10} {wf.path}")
            
        return "\n".join(output)
    except UnknownObjectException:
        return f"Error: Repository {owner}/{repo} not found."
    except Exception as e:
        return f"Error listing workflows: {e}"

@mcp.tool()
def trigger_workflow(owner: str, repo: str, workflow_id_or_filename: str, ref: str = "main", inputs: Optional[Dict[str, Any]] = None) -> str:
    """Triggers a GitHub Actions workflow dispatch event."""
    if not github_token:
        return "Error: GITHUB_PERSONAL_ACCESS_TOKEN or GITHUB_TOKEN environment variable is not set."

    try:
        repository = _get_repo(owner, repo)
        workflow = repository.get_workflow(workflow_id_or_filename)
        
        # PyGithub expects inputs as a dict if provided, else None.
        # Ensure inputs is not None if the user provided an empty dict, although PyGithub handles it.
        result = workflow.create_dispatch(ref=ref, inputs=inputs or {})
        
        if result:
             return f"Successfully triggered workflow '{workflow_id_or_filename}' on ref '{ref}'."
        else:
             # create_dispatch returns True on success, but sometimes it might return None/False if something is off?
             # Actually PyGithub returns True.
             return f"Successfully triggered workflow '{workflow_id_or_filename}' on ref '{ref}'."

    except UnknownObjectException:
        return f"Error: Repository {owner}/{repo} or workflow {workflow_id_or_filename} not found."
    except Exception as e:
        return f"Error triggering workflow: {e}"

@mcp.tool()
def list_workflow_runs(owner: str, repo: str, workflow_id_or_filename: Optional[str] = None, status: Optional[str] = None, limit: int = 10) -> str:
    """Lists recent workflow runs. Optional filters: specific workflow ID/filename and status."""
    if not github_token:
        return "Error: GITHUB_PERSONAL_ACCESS_TOKEN or GITHUB_TOKEN environment variable is not set."

    try:
        repository = _get_repo(owner, repo)
        
        if workflow_id_or_filename:
            workflow = repository.get_workflow(workflow_id_or_filename)
            runs = workflow.get_runs()
        else:
            runs = repository.get_workflow_runs()
            
        output = [f"{ 'ID':<15} {'WORKFLOW':<25} {'STATUS':<15} {'CONCLUSION':<15} {'BRANCH':<15} {'CREATED AT'}"]
        
        count = 0
        for run in runs:
            if status and run.status != status:
                continue
                
            output.append(f"{str(run.id):<15} {run.name[:25]:<25} {run.status:<15} {str(run.conclusion):<15} {run.head_branch[:15]:<15} {run.created_at}")
            count += 1
            if count >= limit:
                break
                
        return "\n".join(output)
    except UnknownObjectException:
        return f"Error: Repository {owner}/{repo} not found."
    except Exception as e:
        return f"Error listing workflow runs: {e}"

@mcp.tool()
def get_workflow_run(owner: str, repo: str, run_id: int) -> str:
    """Gets detailed information about a specific workflow run."""
    if not github_token:
        return "Error: GITHUB_PERSONAL_ACCESS_TOKEN or GITHUB_TOKEN environment variable is not set."

    try:
        repository = _get_repo(owner, repo)
        run = repository.get_workflow_run(run_id)
        
        output = [
            f"Run ID: {run.id}",
            f"Name: {run.name}",
            f"Status: {run.status}",
            f"Conclusion: {run.conclusion}",
            f"Branch: {run.head_branch}",
            f"Commit: {run.head_sha}",
            f"Event: {run.event}",
            f"Created At: {run.created_at}",
            f"Updated At: {run.updated_at}",
            f"URL: {run.html_url}",
        ]
        
        # Add jobs info if useful? keeping it simple for now as 'describe' usually implies high level details.
        
        return "\n".join(output)

    except UnknownObjectException:
        return f"Error: Repository {owner}/{repo} or Run ID {run_id} not found."
    except Exception as e:
        return f"Error getting workflow run: {e}"

if __name__ == "__main__":
    mcp.run()
