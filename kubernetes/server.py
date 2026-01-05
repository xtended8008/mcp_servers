from mcp.server.fastmcp import FastMCP
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import List, Optional, Dict, Any
import datetime
import json
import subprocess

# Initialize FastMCP server
mcp = FastMCP("kubernetes-mcp")

# Initialize Kubernetes client
try:
    config.load_kube_config()
except Exception as e:
    print(f"Warning: Could not load kube config: {e}")

# --- Helper Functions ---

def _format_age(creation_timestamp) -> str:
    if not creation_timestamp:
        return "Unknown"
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - creation_timestamp
        if delta.days > 0:
            return f"{delta.days}d"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600}h"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60}m"
        else:
            return f"{delta.seconds}s"
    except:
        return "Unknown"

# --- Core Tools ---

@mcp.tool()
def list_pods(namespace: str = "default") -> str:
    """Lists pods in a namespace with status, restart count, and age."""
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace)
        
        output = []
        output.append(f"{ 'NAME':<30} {'READY':<10} {'STATUS':<15} {'RESTARTS':<10} {'AGE':<10}")
        
        for pod in pods.items:
            name = pod.metadata.name
            
            ready_containers = 0
            total_containers = len(pod.spec.containers)
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.ready:
                        ready_containers += 1
            ready = f"{ready_containers}/{total_containers}"
            
            status = pod.status.phase
            restarts = 0
            if pod.status.container_statuses:
                 for container in pod.status.container_statuses:
                     restarts += container.restart_count
            
            age = _format_age(pod.metadata.creation_timestamp)
            output.append(f"{name:<30} {ready:<10} {status:<15} {restarts:<10} {age:<10}")
            
        return "\n".join(output)
    except ApiException as e:
        return f"Kubernetes API Error: {e.reason} ({e.status})"
    except Exception as e:
        return f"Error listing pods: {e}"

@mcp.tool()
def describe_pod(pod_name: str, namespace: str = "default") -> str:
    """Returns detailed pod configuration and recent events."""
    try:
        v1 = client.CoreV1Api()
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        
        field_selector = f"involvedObject.name={pod_name},involvedObject.namespace={namespace},involvedObject.uid={pod.metadata.uid}"
        events = v1.list_namespaced_event(namespace, field_selector=field_selector)
        
        output = [f"Name: {pod.metadata.name}", f"Namespace: {pod.metadata.namespace}"]
        output.append(f"Status: {pod.status.phase}")
        output.append(f"Node: {pod.spec.node_name}")
        output.append(f"IP: {pod.status.pod_ip}")
        output.append("\n--- Containers ---")
        for c in pod.spec.containers:
            output.append(f"- {c.name} ({c.image})")
        
        output.append("\n--- Events ---")
        if events.items:
            output.append(f"{ 'TYPE':<10} {'REASON':<20} {'AGE':<10} {'MESSAGE'}")
            for event in events.items:
                age = _format_age(event.last_timestamp)
                output.append(f"{event.type:<10} {event.reason:<20} {age:<10} {event.message}")
        else:
            output.append("<none>")

        return "\n".join(output)
    except ApiException as e:
        return f"Kubernetes API Error: {e.reason} ({e.status})"
    except Exception as e:
        return f"Error describing pod: {e}"

@mcp.tool()
def get_pod_logs(pod_name: str, namespace: str = "default", container: Optional[str] = None, tail_lines: int = 100) -> str:
    """Fetches logs from a pod. Optional: specify container name and number of lines."""
    try:
        v1 = client.CoreV1Api()
        kwargs = {"name": pod_name, "namespace": namespace, "tail_lines": tail_lines}
        if container:
            kwargs["container"] = container
        
        logs = v1.read_namespaced_pod_log(**kwargs)
        return logs
    except ApiException as e:
        return f"Kubernetes API Error: {e.reason} ({e.status})"
    except Exception as e:
        return f"Error getting logs: {e}"

@mcp.tool()
def list_namespaces() -> str:
    """Lists all namespaces in the cluster."""
    try:
        v1 = client.CoreV1Api()
        ns_list = v1.list_namespace()
        output = [f"{ 'NAME':<20} {'STATUS':<10} {'AGE':<10}"]
        for ns in ns_list.items:
            age = _format_age(ns.metadata.creation_timestamp)
            output.append(f"{ns.metadata.name:<20} {ns.status.phase:<10} {age:<10}")
        return "\n".join(output)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_nodes() -> str:
    """Lists cluster nodes with status and capacity info."""
    try:
        v1 = client.CoreV1Api()
        nodes = v1.list_node()
        output = [f"{ 'NAME':<30} {'STATUS':<15} {'ROLES':<20} {'AGE':<10} {'VERSION':<10}"]
        for node in nodes.items:
            status = "Unknown"
            for condition in node.status.conditions:
                if condition.type == "Ready":
                    status = "Ready" if condition.status == "True" else "NotReady"
                    break
            
            roles = []
            for label in node.metadata.labels:
                if label.startswith("node-role.kubernetes.io/"):
                    roles.append(label.split("/")[1])
            roles_str = ",".join(roles) if roles else "<none>"
            
            age = _format_age(node.metadata.creation_timestamp)
            version = node.status.node_info.kubelet_version
            output.append(f"{node.metadata.name:<30} {status:<15} {roles_str:<20} {age:<10} {version:<10}")
        return "\n".join(output)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_events(namespace: str = "default") -> str:
    """Lists the most recent events in a namespace."""
    try:
        v1 = client.CoreV1Api()
        events = v1.list_namespaced_event(namespace)
        # Sort by last timestamp, descending
        sorted_events = sorted(events.items, key=lambda x: x.last_timestamp or x.event_time or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc), reverse=True)
        
        output = [f"{ 'TYPE':<10} {'REASON':<20} {'OBJECT':<30} {'AGE':<10} {'MESSAGE'}"]
        for event in sorted_events[:20]: # Limit to top 20
            age = _format_age(event.last_timestamp)
            obj = f"{event.involved_object.kind}/{event.involved_object.name}"
            output.append(f"{event.type:<10} {event.reason:<20} {obj:<30} {age:<10} {event.message}")
        return "\n".join(output)
    except Exception as e:
        return f"Error: {e}"

# --- Apps Tools ---

@mcp.tool()
def list_deployments(namespace: str = "default") -> str:
    """Lists deployments in a namespace."""
    try:
        apps_v1 = client.AppsV1Api()
        deps = apps_v1.list_namespaced_deployment(namespace)
        output = [f"{ 'NAME':<30} {'READY':<10} {'UP-TO-DATE':<12} {'AVAILABLE':<10} {'AGE':<10}"]
        for d in deps.items:
            ready = f"{d.status.ready_replicas or 0}/{d.status.replicas or 0}"
            uptodate = d.status.updated_replicas or 0
            available = d.status.available_replicas or 0
            age = _format_age(d.metadata.creation_timestamp)
            output.append(f"{d.metadata.name:<30} {ready:<10} {uptodate:<12} {available:<10} {age:<10}")
        return "\n".join(output)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def scale_deployment(name: str, replicas: int, namespace: str = "default") -> str:
    """Scales a deployment to a specific number of replicas."""
    try:
        apps_v1 = client.AppsV1Api()
        body = {"spec": {"replicas": replicas}}
        apps_v1.patch_namespaced_deployment_scale(name, namespace, body)
        return f"Deployment '{name}' in namespace '{namespace}' scaled to {replicas} replicas."
    except ApiException as e:
        return f"Kubernetes API Error: {e.reason} ({e.status})"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def restart_deployment(name: str, namespace: str = "default") -> str:
    """Restarts a deployment by updating its annotation (simulates kubectl rollout restart)."""
    try:
        apps_v1 = client.AppsV1Api()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": now
                        }
                    }
                }
            }
        }
        apps_v1.patch_namespaced_deployment(name, namespace, body)
        return f"Deployment '{name}' in namespace '{namespace}' restarted."
    except ApiException as e:
        return f"Kubernetes API Error: {e.reason} ({e.status})"
    except Exception as e:
        return f"Error: {e}"

# --- Network Tools ---

@mcp.tool()
def list_services(namespace: str = "default") -> str:
    """Lists services in a namespace."""
    try:
        v1 = client.CoreV1Api()
        svcs = v1.list_namespaced_service(namespace)
        output = [f"{ 'NAME':<30} {'TYPE':<15} {'CLUSTER-IP':<15} {'EXTERNAL-IP':<15} {'PORTS'}"]
        for svc in svcs.items:
            ports = ",".join([f"{p.port}/{p.protocol}" for p in svc.spec.ports]) if svc.spec.ports else ""
            ext_ip = "<none>"
            if svc.status.load_balancer.ingress:
                ext_ip = svc.status.load_balancer.ingress[0].ip or svc.status.load_balancer.ingress[0].hostname
            elif svc.spec.external_i_ps:
                 ext_ip = ",".join(svc.spec.external_i_ps)
            
            output.append(f"{svc.metadata.name:<30} {svc.spec.type:<15} {svc.spec.cluster_ip:<15} {ext_ip:<15} {ports}")
        return "\n".join(output)
    except Exception as e:
        return f"Error: {e}"

# --- Helm Tools ---

@mcp.tool()
def list_helm_releases(namespace: str = "default") -> str:
    """Lists Helm releases in a namespace."""
    try:
        cmd = ["helm", "list", "-n", namespace, "--output", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        releases = json.loads(result.stdout)
        
        output = [f"{'NAME':<30} {'NAMESPACE':<15} {'REVISION':<10} {'STATUS':<15} {'CHART':<30} {'APP VERSION'}"]
        for r in releases:
            output.append(f"{r['name']:<30} {r['namespace']:<15} {r['revision']:<10} {r['status']:<15} {r['chart']:<30} {r['app_version']}")
        
        return "\n".join(output)
    except subprocess.CalledProcessError as e:
        return f"Helm Error: {e.stderr}"
    except Exception as e:
        return f"Error listing helm releases: {e}"

@mcp.tool()
def get_helm_release(name: str, namespace: str = "default") -> str:
    """Gets detailed status of a Helm release."""
    try:
        cmd = ["helm", "status", name, "-n", namespace, "--output", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        status = json.loads(result.stdout)
        
        output = [f"Name: {status['name']}", f"Namespace: {status['namespace']}", f"Status: {status['info']['status']}"]
        output.append(f"First Deployed: {status['info']['first_deployed']}")
        output.append(f"Last Deployed: {status['info']['last_deployed']}")
        output.append(f"Notes:\n{status['info'].get('notes', 'No notes')}")
        
        return "\n".join(output)
    except subprocess.CalledProcessError as e:
        return f"Helm Error: {e.stderr}"
    except Exception as e:
        return f"Error getting helm release: {e}"

@mcp.tool()
def uninstall_helm_release(name: str, namespace: str = "default") -> str:
    """Uninstalls a Helm release."""
    try:
        cmd = ["helm", "uninstall", name, "-n", namespace]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Helm Error: {e.stderr}"
    except Exception as e:
        return f"Error uninstalling helm release: {e}"

if __name__ == "__main__":
    mcp.run()