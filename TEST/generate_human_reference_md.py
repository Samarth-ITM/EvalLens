import json
from pathlib import Path

with open("TEST/human_reference_evaluations.json", "r", encoding="utf-8") as f:
    refs = json.load(f)

lines = [
    "# Independent Human Reference Evaluations (Ground Truth Benchmark)",
    "",
    "This benchmark establishes the independent ground truth evaluation for 12 representative documents across diverse file formats and domains.",
    "**Crucially, this ground truth was produced entirely through direct human inspection and evaluation of each document BEFORE running any automated EvalLens or Gemini evaluations.**",
    "",
    f"**Total Benchmark Documents:** {len(refs)}",
    "**Formats Evaluated:** TXT, MD, PDF, DOCX, PY, CPP, JAVA, TS, HTML, SQL",
    "",
    "---",
    ""
]

for ref in refs:
    lines.append(f"## {ref['document_id']}: {ref['title']}")
    lines.append(f"- **Filename:** `{ref['filename']}`")
    lines.append(f"- **Format:** {ref['format']}")
    lines.append(f"- **Domain:** {ref['domain']}")
    lines.append(f"- **Evaluation Goals:** {ref['evaluation_goals']}")
    lines.append(f"- **Overall Human Score:** {ref['overall_human_score']} / {ref['max_possible_score']} ({ref['percentage']}%)")
    lines.append(f"- **Overall Assessment:** {ref['overall_assessment']}")
    lines.append("")
    lines.append("### Human Reference Criteria & Scoring")
    lines.append("")
    lines.append("| ID | Criterion Name | Max Score | Human Score | Justification & Text Citations |")
    lines.append("|---|---|---|---|---|")
    for c in ref["criteria"]:
        just = c["justification"].replace("|", "\\|")
        lines.append(f"| {c['criterion_id']} | **{c['name']}**<br>*{c['description']}* | {c['max_score']} | **{c['human_score']}** | {just} |")
    lines.append("")
    lines.append("---")
    lines.append("")

with open("TEST/human_reference_evaluations.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Successfully generated TEST/human_reference_evaluations.md")
