import json
import os
import glob
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Label

class VulnerabilityDashboard(App):
    BINDINGS = [("q", "quit", "Quit")]
    CSS = """
    DataTable { height: 80%; }
    Label { padding: 1; text-align: center; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("GEMINIRECON - Vulnerability Dashboard")
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Target", "TemplateID", "Severity", "URL", "MatchedAt")
        self.load_data(table)

    def load_data(self, table):
        # Scan all results directories
        for vuln_file in glob.glob("results/*/vulnerabilities.json"):
            target = vuln_file.split("/")[1]
            try:
                with open(vuln_file, 'r') as f:
                    for line in f:
                        if not line.strip(): continue
                        data = json.loads(line)
                        table.add_row(
                            target,
                            data.get("template-id", "N/A"),
                            data.get("info", {}).get("severity", "N/A"),
                            data.get("matched-at", "N/A"),
                            data.get("timestamp", "N/A")
                        )
            except Exception as e:
                continue

if __name__ == "__main__":
    app = VulnerabilityDashboard()
    app.run()
