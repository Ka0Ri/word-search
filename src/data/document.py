from pydantic import BaseModel
from typing import Dict, Union, List
from pandas import DataFrame
import pandas as pd
from konlpy.tag import Okt, Kkma
import collections

okt = Okt()
kkma = Kkma()

def okt_tokenizer(doc):
    return list(set([word for (word, particle) in okt.pos(doc, stem=True) 
                        if particle in ['Verb', 'Adjective', 'Noun']]))

def kkma_tokenizer(doc):
    result = []
    try:
        result = list(set([word for (word, particle) in kkma.pos(doc)
                        if particle in ['VV', 'VA', 'NNG']]))
    except UnicodeEncodeError:
        result = []
    finally:
        return result


def CountFrequency(arr):
    return collections.Counter(arr)

class Document(BaseModel):
    metadata: Dict[str, Union[str, List[str]]]=None
    paragraphs: DataFrame=None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, json: Dict):
        super().__init__()
        self.metadata = json['metadata']
        self.paragraphs = DataFrame(json['document'][0]['paragraph'])
        self.paragraphs['tokenized'] = self.paragraphs['form'].apply(okt_tokenizer)

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
        
        words = [okt.morphs(word)[0] for word in words]
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

    def get_most_freq_words(self, n: int):
        word_list = []
        for doc in self.documents:
            tokenized = doc.paragraphs['tokenized'].to_list()
            flat_list = [
                        x
                        for xs in tokenized
                        for x in xs
                    ]
            word_list += flat_list
        
        freq = CountFrequency(word_list)
        word_freq = pd.DataFrame(freq, index=['count']).T
        return word_freq.head(n)

    def get_search_results(self, key):
        return self.search_results[key]