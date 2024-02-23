from pydantic import BaseModel
from typing import Dict, Union, List
from pandas import DataFrame
import pandas as pd
from konlpy.tag import Okt
okt = Okt()

def tokenizer(doc):
    return [word for (word, particle) in okt.pos(doc, stem=True) 
                        if particle in ['Verb', 'Adjective']]

class Document(BaseModel):
    metadata: Dict[str, Union[str, List[str]]]=None
    paragraphs: DataFrame=None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, json: Dict):
        super().__init__()
        self.metadata = json['metadata']
        self.paragraphs = DataFrame(json['document'][0]['paragraph'])
        self.paragraphs['tokenized'] = self.paragraphs['form'].apply(tokenizer)

    def search(self, words: List[str]) -> List[str]:
        
        document = self.paragraphs
        word_dict = {}
        for word in words:
            word_dict.update(
                {word: document[document['tokenized'].apply(lambda x: word in x)]})

        return word_dict
    

class ListOfDocuments(BaseModel):
    documents: List[Document]=None
    search_results: Dict[str, DataFrame]=None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, documents: List[Document]):
        super().__init__()
        self.documents = documents

    def search(self, words: List[str]):
        
        search_results = {}
        for doc in self.documents:
            word_dict = doc.search(words)
            # concatenate the results
            for word in word_dict:
                if word in search_results:
                    search_results[word] = pd.concat([search_results[word], word_dict[word]])
                else:
                    search_results[word] = word_dict[word]
        
        self.search_results = search_results
        return search_results
    
    def save_search_results(self, path: str):
        writer = pd.ExcelWriter(path)
        for word in self.search_results:
            df = self.search_results[word]
            df['tokenized'] = df['tokenized'].apply(lambda x: ', '.join(x))
            df = df.drop_duplicates(subset=['id'])
            # save to excel with sheet name as word
            df.to_excel(writer, sheet_name=word, index=False)

        writer.close()