from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Log, TabbedContent, TabPane
from textual.containers import Container, Horizontal, Vertical
from agents.orchestrator import ReconOrchestrator
import asyncio

class ReconApp(App):
    CSS = """
    Screen {
        background: #121212;
    }
    #sidebar {
        width: 30;
        background: #1e1e1e;
        border-right: solid #333;
    }
    #main_content {
        padding: 1;
    }
    Log {
        background: #000;
        color: #0f0;
        border: solid #333;
        height: 1fr;
    }
    Input {
        dock: bottom;
        margin-top: 1;
    }
    .sidebar-header {
        background: #333;
        color: #fff;
        padding: 1;
        text-align: center;
        text-style: bold;
    }
    """

    TITLE = "GEMINIRECON"
    SUB_TITLE = "AI-Powered Reconnaissance Platform"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Static("Targets", classes="sidebar-header")
            with Vertical(id="main_content"):
                with TabbedContent(initial="live_scan"):
                    with TabPane("Live Scan", id="live_scan"):
                        yield Log(id="scan_log")
                    with TabPane("Assets", id="assets"):
                        yield Static("Asset Inventory", id="assets_view")
                    with TabPane("Findings", id="findings"):
                        yield Static("Security Findings", id="findings_view")
                    with TabPane("Reports", id="reports"):
                        yield Static("Generated Reports", id="reports_view")
                yield Input(placeholder="Enter target (e.g., example.com) and press Enter...", id="target_input")
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        target = event.value
        if not target:
            return
        
        event.input.value = ""
        log = self.query_one("#scan_log", Log)
        log.write(f"[bold cyan]>>> Starting recon for: {target}[/bold cyan]")
        
        orchestrator = ReconOrchestrator()
        
        async def log_callback(msg):
            log.write(f"[yellow]INFO:[/yellow] {msg}")

        try:
            results = await orchestrator.run_recon_workflow(target, callback=log_callback)
            log.write("[bold green]SUCCESS: Recon workflow completed.[/bold green]")
            # Update other views with results...
            self.query_one("#findings_view", Static).update(results["risk"])
        except Exception as e:
            log.write(f"[bold red]ERROR: {str(e)}[/bold red]")

if __name__ == "__main__":
    app = ReconApp()
    app.run()
