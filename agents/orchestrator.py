from agents.planner import PlannerAgent
from agents.recon import ReconAgent
from agents.multi_agents import AnalysisAgent, RiskAgent, ReportAgent, MemoryAgent
from core.utils.normalization import Normalizer
from core.config import REPORTS_DIR
from fpdf import FPDF
import json
import os
from datetime import datetime

class ReconOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.recon = ReconAgent()
        self.analysis = AnalysisAgent()
        self.risk = RiskAgent()
        self.report = ReportAgent()
        self.memory = MemoryAgent()

    async def run_recon_workflow(self, user_input, callback=None):
        """
        Runs the full recon workflow: Plan -> Recon -> Analysis -> Risk -> Report -> Memory
        """
        try:
            # 1. Plan
            if callback: await callback("Planning workflow...")
            plan_resp = await self.planner.chat_async(user_input)
            plan = Normalizer.normalize(plan_resp.text)

            # 2. Recon
            if callback: await callback(f"Executing recon...\nPlan: {plan}")
            recon_resp = await self.recon.chat_async(f"Execute this plan: {plan}")
            recon_data = recon_resp.text 

            # 3. Analysis (High-Stakes Racing)
            if callback: await callback("Analyzing findings with multi-model racing...")
            analysis_agent = AnalysisAgent(use_ultraplinian=True)
            analysis_resp = await analysis_agent.analyze_with_race(recon_data)
            analysis_summary = Normalizer.normalize(analysis_resp.text)

            # 4. Risk Assessment
            if callback: await callback("Assessing risks...")
            risk_resp = await self.risk.chat_async(f"Assess risks for these findings: {analysis_summary}")
            risk_assessment = Normalizer.normalize(risk_resp.text)

            # 5. Generate Professional AI Report
            if callback: await callback("Generating final AI report...")
            report_context = f"Target: {user_input}\nAnalysis: {analysis_summary}\nRisks: {risk_assessment}"
            report_resp = await self.report.chat_async(f"Generate a professional executive report for: {report_context}")
            final_report_text = Normalizer.normalize(report_resp.text)

            # 6. Save as PDF
            target_name = user_input.replace("http://", "").replace("https://", "").split("/")[0].replace(" ", "_")
            pdf_path = self.save_as_pdf(target_name, final_report_text)
            if callback: await callback(f"Report saved to: {pdf_path}")

            # 7. Extract Structured Assets
            if callback: await callback("Extracting structured asset data...")
            asset_prompt = f"Based on this recon data, extract a JSON list of discovered assets. Each asset should have: domain, ip, tech (list), and status (Live/Down). Format as valid JSON only: {recon_data}"
            asset_resp = await self.analysis.chat_async(asset_prompt)
            try:
                text = asset_resp.text
                start = text.find('[')
                end = text.rfind(']') + 1
                if start != -1 and end != 0:
                    assets = json.loads(text[start:end])
                else:
                    assets = []
            except:
                assets = []

            # Final result
            return {
                "plan": plan,
                "recon_data": recon_data,
                "analysis": analysis_summary,
                "risk": risk_assessment,
                "report": final_report_text,
                "pdf_path": pdf_path,
                "assets": assets
            }
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "resource_exhausted" in error_msg:
                friendly_error = "⚠️ Gemini API Quota Exceeded. The free tier has reached its daily or per-minute limit. Please wait a few minutes or check your API usage at https://aistudio.google.com/."
                if callback: await callback(friendly_error)
                raise Exception(friendly_error)
            raise e

    def save_as_pdf(self, target, content):
        """
        Saves the AI-generated report as a professional PDF.
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Title
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"GEMINIRECON SECURITY REPORT: {target}", ln=True, align='C')
            pdf.ln(5)
            
            # Metadata
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='R')
            pdf.ln(10)
            
            # Body Content
            pdf.set_font("Arial", size=12)
            # Replace characters that might cause encoding issues in basic FPDF
            clean_content = content.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, clean_content)
            
            filename = f"{target}.pdf"
            filepath = os.path.join(REPORTS_DIR, filename)
            pdf.output(filepath)
            return filepath
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
