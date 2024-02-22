import gradio as gr

with gr.Blocks() as demo:
    with gr.Row():
        drop_choices = gr.Dropdown(["love", "hate"], label="Word list", multiselect=True)
    with gr.Row():
        text_output = gr.Text(label="Output text")
        btn_search = gr.Button("Search")
    
    btn_search.click(lambda x: x[0], inputs=[drop_choices], outputs=[text_output])

if __name__ == "__main__":
    demo.launch()