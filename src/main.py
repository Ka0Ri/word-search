import gradio as gr
import yaml
from data.document import ListOfDocuments, Document
import os
import json

LISTOFDOCUMENTS = None

with open("src/configs/configs.yml", "r") as f:
    config = yaml.safe_load(f)

def load_files(files):
    documents = []
    for path in gr.Progress().tqdm(files, desc="Loading files"):
        with open(os.path.join(path), 'r', encoding='utf-8') as f:
            data = json.load(f)
            documents.append(Document(data))

    global LISTOFDOCUMENTS 
    LISTOFDOCUMENTS = ListOfDocuments(documents)

    return files

def clear_files(files):
    global LISTOFDOCUMENTS
    LISTOFDOCUMENTS = None
    return files

def save():
    global LISTOFDOCUMENTS
    LISTOFDOCUMENTS.save_search_results(config['save_path'])
    gr.Warning(f"Save files in {config['save_path']} successfully.")
   
def search(wordlist, files):

    # documents = []
    # for path in gr.Progress().tqdm(files, desc="Loading files"):
    #     with open(os.path.join(path), 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         documents.append(Document(data))

    global LISTOFDOCUMENTS
    return LISTOFDOCUMENTS.search(wordlist)[wordlist[0]]



with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            drop_files = gr.File(label="Upload files", file_types=[".json"], file_count='multiple')
        with gr.Column():
            with gr.Row():
                drop_choices = gr.Dropdown(config['wordlist'], label="Word list", multiselect=True, allow_custom_value=True)
            with gr.Row():
                with gr.Column():
                    btn_search = gr.Button("Search")
                with gr.Column():
                    btn_save = gr.Button("Save")

    with gr.Row():
        
        df = gr.Dataframe(label="Search results")
        plot = gr.Plot(label="Plot")
        
    drop_files.upload(load_files, inputs=[drop_files], outputs=[drop_files])
    drop_files.clear(clear_files, inputs=[drop_files], outputs=[drop_files])
    btn_search.click(search, inputs=[drop_choices, drop_files], outputs=[df])
    btn_save.click(save, inputs=[], outputs=[])


if __name__ == "__main__":

    demo.launch()