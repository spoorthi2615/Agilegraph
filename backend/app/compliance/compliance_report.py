import csv
from io import StringIO
from app.compliance.compliance_models import SynopsisComplianceReport

class ComplianceReportGenerator:
    @staticmethod
    def generate_json(report: SynopsisComplianceReport) -> str:
        return report.model_dump_json(indent=2)
        
    @staticmethod
    def generate_markdown(report: SynopsisComplianceReport) -> str:
        md = "# AgileGraph Synopsis Compliance Report\n\n"
        md += f"## Overall Readiness Score: {report.production_readiness.overall_readiness_score}%\n\n"
        
        md += "### Module Implementation Status\n"
        for mod in report.synopsis_cross_check:
            md += f"- **{mod.name}**: {mod.status}\n"
            
        md += "\n### Scanners\n"
        md += f"- Java: {report.scanner_verification.java_implemented}\n"
        md += f"- Python: {report.scanner_verification.python_implemented}\n"
        md += f"- Go: {report.scanner_verification.go_implemented}\n"
        md += f"- Dependency: {report.scanner_verification.dependency_implemented}\n"
        md += f"- Certificate: {report.scanner_verification.certificate_implemented}\n"
        md += f"- Live TLS: {report.scanner_verification.live_tls_implemented}\n"
        md += f"- Certificate Transparency: {report.scanner_verification.ct_implemented}\n"
        md += f"- Semgrep: {report.scanner_verification.semgrep_implemented}\n"
        md += f"- CBOM: {report.scanner_verification.cbom_implemented}\n"

        return md

    @staticmethod
    def generate_csv(report: SynopsisComplianceReport) -> str:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Module", "Status"])
        for mod in report.synopsis_cross_check:
            writer.writerow([mod.name, mod.status])
        return output.getvalue()
