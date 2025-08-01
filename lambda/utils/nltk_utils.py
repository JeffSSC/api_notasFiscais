import nltk
nltk.data.path = ["/opt/python/lib/python3.12/site-packages/nltk_data"]
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re

def filter_text(text_list):
    # Unir todas as frases em um único texto
    full_text = " ".join(text_list)
    
    # Tokenizar o texto
    tokens = word_tokenize(full_text)

    # Remover stopwords em português
    stop_words = set(stopwords.words("portuguese"))
    filtered_words = [word for word in tokens if word.lower() not in stop_words]

    return filtered_words

