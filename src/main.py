import gradio as gr
import yaml
from data.document import ListOfDocuments, Document
import os
import json
import pandas as pd

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

    most_common_words = LISTOFDOCUMENTS.get_most_freq_words(20)
    most_common_words = most_common_words.reset_index()
    most_common_words.columns = ['word', 'count']

    return files, most_common_words

def clear_files(files):
    global LISTOFDOCUMENTS
    LISTOFDOCUMENTS = None
    return files

def save():
    global LISTOFDOCUMENTS
    # Incremental path
    # get the last number of the .xlsx file
    xls_files = [f for f in os.listdir(config['save_path']) if f.endswith(".xlsx")]
    if len(xls_files) > 0:
        last_file = sorted(xls_files, reverse=True)[0]
        last_number = int(last_file.split(".")[0].split("-")[-1])
    else:
        last_number = 0
    file_path = os.path.join(config['save_path'], f"test-{last_number+1}.xlsx")
    LISTOFDOCUMENTS.save_search_results(file_path)
    gr.Warning(f"Save files {file_path} successfully.")
   
def search(wordlist):

    # documents = []
    # for path in gr.Progress().tqdm(files, desc="Loading files"):
    #     with open(os.path.join(path), 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #         documents.append(Document(data))

    global LISTOFDOCUMENTS
    search_results = LISTOFDOCUMENTS.search(wordlist)
    
    # Report the search results
    text_results = ""
    for word in search_results:
        text_results += f"{word}: {search_results[word].shape[0]} texts,\n"
    # concat the results into a dataframe with only 5 rows
    search_results = pd.concat([search_results[word].head(5) for word in search_results], axis=0)
   
    return search_results, gr.update(choices=wordlist, value=None), text_results


with gr.Blocks() as demo:
    demo.title = "Search documents"
    gr.Markdown("# Searching documents using word list")
    
    with gr.Row():
        drop_files = gr.File(label="Upload files", file_types=[".json"], file_count='multiple')
        with gr.Column():
            with gr.Row():
                drop_choices = gr.Dropdown(config['wordlist'], label="Word list", multiselect=True, allow_custom_value=True)
            with gr.Row():
                btn_search = gr.Button("Search")
                btn_save = gr.Button("Save")
            text_results = gr.Label(label="Search results")
    
            with gr.Column():
                plot = gr.BarPlot(label="Most common words", interactive=True, x="word", y="count")
            with gr.Column():
                drop_results = gr.Dropdown(label="Search results", choices=[], interactive=True, allow_custom_value=True)
                df = gr.Dataframe(label="Dataframe")
        
    drop_files.upload(load_files, inputs=[drop_files], outputs=[drop_files, plot])
    drop_files.clear(clear_files, inputs=[drop_files], outputs=[drop_files])
    btn_search.click(search, inputs=[drop_choices], outputs=[df, drop_results, text_results])
    btn_save.click(save, inputs=[], outputs=[])
    drop_results.select(lambda x: LISTOFDOCUMENTS.get_search_results(x), inputs=[drop_results], outputs=[df])


if __name__ == "__main__":

    demo.launch()