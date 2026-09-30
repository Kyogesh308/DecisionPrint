from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        # Fix parameter names
        self.cell(190, 10, 'DecisionPrint - Intelligence Engine Blog', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

pdf = PDF()
pdf.add_page()
pdf.set_font("helvetica", size=12)

content = """Welcome to the latest update for DecisionPrint!

In this branch (feat/p2-intelligence), we have successfully completed the massive milestone of building the Intelligence Engine (Phases 0 through 6).

Key Highlights of this Branch:
1. Intelligence Module Foundation: We have implemented the core intelligence pipelines including context extraction, decision extraction, and causal linking.
2. Drift Detection: A robust drift detection mechanism (`drift.py`) has been added to identify when past decisions conflict with new context.
3. Caching Layer: We introduced an LLM caching layer (`llm_cache.py`) which significantly speeds up testing and prevents unnecessary redundant API calls.
4. Evaluation Framework: An entire evaluation framework (`eval/`) has been created, encompassing baselines, metrics, and a pipeline runner to measure the quality of our intelligence extractions reliably.
5. Extensibility: Prompts are securely managed and versioned under the `prompts/` directory to allow easy switching between different structured outputs.
6. Robust Testing: Over 7,000 lines of robust tests and mock data were added to ensure that our extractors and evaluations run deterministically and catch edge cases!

The foundation for transforming unstructured documentation into precise, traceable decisions is now a reality. This opens the door for real-time organizational memory querying.
"""

for line in content.strip().split('\n'):
    if line.strip():
        pdf.multi_cell(190, 10, text=line)
    else:
        pdf.ln(5)
    
pdf.output("intelligence_blog.pdf")
