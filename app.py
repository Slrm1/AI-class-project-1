import gradio as gr
from query import answer


def ask(question):
    if not question.strip():
        return "Please enter a question."
    try:
        response, results = answer(question)
        sources = "\n\n### Retrieved sources\n" + "\n".join(
            f"- `{meta['source_file']}` — distance `{distance:.4f}`"
            for _, meta, distance in results
        )
        return response + sources
    except Exception as exc:
        return f"Error: {exc}"


demo = gr.Interface(
    fn=ask,
    inputs=gr.Textbox(label="Ask about Howard Computer Science", placeholder="What does CSCI 354 cover?"),
    outputs=gr.Markdown(label="Grounded answer"),
    title="The Unofficial Howard CS Guide",
    description="Ask questions about the curated Howard CS knowledge base. Answers are grounded in retrieved source documents.",
    examples=[
        ["How many credits are required for the BS in Computer Science?"],
        ["What does CSCI 354 cover?"],
        ["Who advises Computer Science students with last names L-Z?"],
        ["What internship resources does Howard provide?"],
    ],
)

if __name__ == "__main__":
    demo.launch()
