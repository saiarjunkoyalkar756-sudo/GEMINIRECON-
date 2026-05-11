import os
import asyncio
from datetime import datetime
from fpdf import FPDF
from core.config import REPORTS_DIR

class ReportGenerator:
    @staticmethod
    async def generate_pdf(target: str, content: str) -> str:
        """
        Saves the AI-generated report as a professional multi-page PDF.
        """
        try:
            class PDF(FPDF):
                def footer(self):
                    self.set_y(-15)
                    self.set_font("Helvetica", "I", 8)
                    self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

            pdf = PDF()
            pdf.alias_nb_pages()
            pdf.add_page()
            pdf.set_margins(15, 20, 15)
            pdf.set_auto_page_break(auto=True, margin=20)
            
            # Title Header
            pdf.set_font("Helvetica", 'B', 16)
            pdf.set_text_color(33, 37, 41)
            pdf.cell(0, 15, f"GEMINIRECON SECURITY REPORT", ln=True, align='L')
            
            pdf.set_font("Helvetica", 'B', 12)
            pdf.set_text_color(108, 117, 125)
            pdf.cell(0, 10, f"Target: {target}", ln=True, align='L')
            
            # Metadata
            pdf.set_font("Helvetica", 'I', 9)
            pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='L')
            pdf.ln(10)
            
            # Divider line
            pdf.set_draw_color(200, 200, 200)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(10)
            
            # Body Content
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(0, 0, 0)
            
            # Clean content for Latin-1 compatibility
            clean_content = content.encode('latin-1', 'replace').decode('latin-1')
            
            # Professional paragraph rendering
            pdf.multi_cell(0, 7, clean_content)
            
            filename = f"{target.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(REPORTS_DIR, filename)
            pdf.output(filepath)
            
            # Upload to cloud storage if enabled
            from storage.cloud import storage as cloud_storage
            cloud_url = await cloud_storage.upload_file(filepath, f"reports/{filename}")
            
            return cloud_url or filepath
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
