# Path: intelligent_summarizer/backend/services/summarizer.py

import nltk
import re
import math
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
import heapq

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

stop_words = set(stopwords.words("english"))

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text

def compute_tf_idf(sentences):
    word_doc_freq = Counter()

    for sentence in sentences:
        words = set(word_tokenize(sentence.lower()))
        for word in words:
            if word.isalpha() and word not in stop_words:
                word_doc_freq[word] += 1

    tf_idf_scores = []

    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        sentence_score = 0
        word_count = 0

        for word in words:
            if word.isalpha() and word not in stop_words:
                tf = words.count(word)
                idf = math.log(len(sentences) / (1 + word_doc_freq[word]))
                sentence_score += tf * idf
                word_count += 1

        if word_count > 0:
            sentence_score /= word_count

        tf_idf_scores.append(sentence_score)

    return tf_idf_scores

def generate_summary(text, summary_ratio=0.3):
    text = clean_text(text)
    sentences = sent_tokenize(text)

    tf_idf_scores = compute_tf_idf(sentences)

    sentence_ranking = {
        sentences[i]: tf_idf_scores[i] + (1 / (i + 1))  # position boost
        for i in range(len(sentences))
    }

    summary_length = max(1, int(len(sentences) * summary_ratio))
    best_sentences = heapq.nlargest(summary_length, sentence_ranking, key=sentence_ranking.get)

    best_sentences.sort(key=lambda s: sentences.index(s))

    return " ".join(best_sentences)
