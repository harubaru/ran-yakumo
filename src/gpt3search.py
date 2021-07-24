import os
import json
import openai

class SearchService:
    def __init__(self, api_key=None):
        if api_key == None:
            openai.api_key = os.getenv('OPENAI_API_KEY')
        else:
            openai.api_key = api_key
        
    def classify_sequence(self, query, terms):
        result = openai.Engine("ada").search(
            search_model="ada",
            documents=terms,
            query=query,
            max_rerank=1
        )

        document = 0
        score = 0.0
        for i in result.data:
            if i.score > score:
                score = i.score
                document = i.document
            
        return document
