from agents.intent import IntentAgent
from agents.planner import PlannerAgent
from agents.recon import ReconAgent
from agents.multi_agents import (
    AnalysisAgent, RiskAgent, ReportAgent, 
    MemoryAgent, DecisionAgent, CorrelationAgent, 
    ThreatIntelAgent, ValidationAgent
)
from core.reporting import ReportGenerator
from core.utils.normalization import Normalizer
import json
import logging

logger = logging.getLogger(__name__)

class ReconOrchestrator:
    def __init__(self):
        self.intent = IntentAgent()
        self.planner = PlannerAgent()
        self.recon = ReconAgent()
        self.decision = DecisionAgent()
        self.analysis = AnalysisAgent(use_ultraplinian=True)
        self.correlation = CorrelationAgent()
        self.threat_intel = ThreatIntelAgent()
        self.validation = ValidationAgent()
        self.risk = RiskAgent()
        self.report = ReportAgent()
        self.memory = MemoryAgent()

    async def run_recon_workflow(self, user_input, callback=None):
        """
        Runs the full modular AI-orchestrated recon workflow.
        """
        try:
            # 1. Intent Analysis
            if callback: await callback("Analyzing intent...")
            intent_data = await self.intent.classify_intent(user_input)
            skill_name = intent_data.get("skill", "default")
            target = intent_data.get("target", user_input)
            
            # 2. Planning
            if callback: await callback(f"Planning workflow for {target} using {skill_name}...")
            plan_data = await self.planner.create_plan(skill_name, target)
            tasks = plan_data.get("tasks", [])

            # 3. Execution (Recon + Decision Loop)
            if callback: await callback(f"Executing {len(tasks)} tasks...")
            all_recon_data = []
            for task in tasks:
                if callback: await callback(f"Task: {task.get('description')}")
                recon_resp = await self.recon.chat_async(f"Execute this task: {json.dumps(task)}")
                # Truncate each tool output
                truncated_text = Normalizer.truncate(recon_resp.text, max_chars=5000)
                all_recon_data.append(truncated_text)
                
            combined_recon_data = "\n".join(all_recon_data)
            # Further truncate the combined data if needed
            combined_recon_data = Normalizer.truncate(combined_recon_data, max_chars=20000)

            # 4. Correlation & Enrichment
            if callback: await callback("Correlating findings and enriching with threat intel...")
            # correlation_resp = await self.correlation.chat_async(combined_recon_data)
            # intel_resp = await self.threat_intel.chat_async(combined_recon_data)
            
            # 5. Analysis (High-Stakes Racing)
            if callback: await callback("Analyzing findings with multi-model racing...")
            analysis_resp = await self.analysis.analyze_with_race(combined_recon_data)
            analysis_summary = Normalizer.normalize(analysis_resp.text)

            # 6. Risk Assessment
            if callback: await callback("Assessing risks...")
            risk_resp = await self.risk.chat_async(f"Assess risks for these findings: {analysis_summary}")
            risk_assessment = Normalizer.normalize(risk_resp.text)

            # 7. Reporting
            if callback: await callback("Generating professional security report...")
            report_context = f"Target: {target}\nRecon Data: {combined_recon_data}\nAnalysis: {analysis_summary}\nRisks: {risk_assessment}"
            report_resp = await self.report.chat_async(f"Generate a professional security report for: {report_context}")
            final_report_text = Normalizer.normalize(report_resp.text)

            # Save as PDF
            pdf_path = await ReportGenerator.generate_pdf(target, final_report_text)
            if callback: await callback(f"Report saved to: {pdf_path}")

            # 8. Memory
            # await self.memory.chat_async(f"Store these key findings: {analysis_summary}")

            return {
                "target": target,
                "plan": plan_data,
                "recon_data": combined_recon_data,
                "analysis": analysis_summary,
                "risk": risk_assessment,
                "report": final_report_text,
                "pdf_path": pdf_path
            }
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            raise e
