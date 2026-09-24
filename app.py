"""Gradio interface for The Unofficial Howard CS Guide."""

import gradio as gr

from query import answer

FILTERS = {
    "All sources": None,
    "Reddit threads only": "reddit",
    "Rate My Professors only": "rmp",
}


def ask(question, source_filter):
    if not question or not question.strip():
        return "Please enter a question.", ""
    try:
        result = answer(question, source_type=FILTERS.get(source_filter))
    except Exception as exc:
        return f"Error: {exc}", ""

    source_lines = []
    for doc, meta, distance in result["results"]:
        preview = " ".join(doc.split())
        if len(preview) > 220:
            preview = preview[:220] + "..."
        source_lines.append(
            f"• {meta['source_file']} ({meta.get('source_type', '')}, distance {distance:.3f})\n  {preview}"
        )
    return result["answer"], "\n\n".join(source_lines)


with gr.Blocks(title="The Unofficial Howard CS Guide") as demo:
    gr.Markdown(
        """# The Unofficial Howard CS Guide
Ask a plain-language question about Howard CS courses, professors, registration, or internships.
Answers use only the retrieved student posts and Rate My Professors reviews."""
    )
    question = gr.Textbox(
        label="Your question",
        placeholder="What do students say CSCI-136 covers?",
        lines=2,
    )
    source_filter = gr.Dropdown(
        label="Limit sources (optional)",
        choices=list(FILTERS),
        value="All sources",
    )
    button = gr.Button("Ask")
    answer_box = gr.Textbox(label="Answer", lines=10)
    sources_box = gr.Textbox(label="Retrieved from", lines=12)
    button.click(ask, inputs=[question, source_filter], outputs=[answer_box, sources_box])
    question.submit(ask, inputs=[question, source_filter], outputs=[answer_box, sources_box])
    gr.Examples(
        examples=[
            ["What do students say CSCI-136 covers, and which languages might it use?", "All sources"],
            ["What do reviews say about Jeremy Blackstone's CSCI 135 class?", "Rate My Professors only"],
            ["How do students register for classes in BisonHub?", "Reddit threads only"],
            ["What is the weather in Washington, DC tomorrow?", "All sources"],
        ],
        inputs=[question, source_filter],
    )

if __name__ == "__main__":
    demo.launch()
