import asyncio
import json
import networkx as nx

class ExploitOrchestrator:
    """
    A DAG-based orchestrator that chains offensive tasks.
    Example: Subdomain -> Path Fuzzing -> Parameter Extraction -> Vulnerability Testing
    """
    def __init__(self):
        self.dag = nx.DiGraph()

    def add_task(self, task_name, func, dependencies=[]):
        self.dag.add_node(task_name, func=func)
        for dep in dependencies:
            self.dag.add_edge(dep, task_name)

    async def execute(self, target, scan_job_id):
        # Sort topologically for execution order
        execution_order = list(nx.topological_sort(self.dag))
        results = {}
        
        for task_name in execution_order:
            node = self.dag.nodes[task_name]
            # Context-aware task execution: pass previous results as arguments
            func = node['func']
            results[task_name] = await func(target, scan_job_id, results)
        
        return results
