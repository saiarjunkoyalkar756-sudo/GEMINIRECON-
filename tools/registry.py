from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Callable
import asyncio
import os

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]
    command_template: str
    output_parser: Optional[str] = None # Name of a parser function or strategy
    category: str = "recon"
    
    def get_openai_schema(self) -> Dict:
        properties = {}
        required = []
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self.tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self.tools.values())

    def get_all_openai_schemas(self) -> List[Dict]:
        return [tool.get_openai_schema() for tool in self.tools.values()]

# Global registry instance
registry = ToolRegistry()

# Register default tools
registry.register(ToolDefinition(
    name="subfinder",
    description="Discover subdomains for a given target domain.",
    parameters=[
        ToolParameter(name="domain", type="string", description="The target domain to scan (e.g., example.com)")
    ],
    command_template="subfinder -d {domain} -silent",
    category="recon"
))

registry.register(ToolDefinition(
    name="nuclei",
    description="Scan a target for vulnerabilities using templates.",
    parameters=[
        ToolParameter(name="target", type="string", description="The target URL or IP to scan"),
        ToolParameter(name="templates", type="string", description="Comma-separated list of templates or tags (e.g., cves,exposures)", required=False, default="cves,exposures")
    ],
    command_template="nuclei -u {target} -t {templates} -silent -jsonl",
    category="vuln"
))

registry.register(ToolDefinition(
    name="nmap",
    description="Scan ports and identify services on a target.",
    parameters=[
        ToolParameter(name="target", type="string", description="The target IP or domain"),
        ToolParameter(name="args", type="string", description="Additional nmap arguments", required=False, default="-sV -Pn")
    ],
    command_template="nmap {args} {target}",
    category="recon"
))
