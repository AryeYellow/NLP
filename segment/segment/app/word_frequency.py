from collections import Counter
from re import fullmatch
from pandas import DataFrame
from segment.clean import ngram
from segment.hmm import tk as tk0
from segment.hmm import tk as tk1
from segment.hmm_flag import tk as tk2

_dict = set(tk1.word2flag)
_pattern = '[a-zA-Z0-9\u4e00-\u9fa5]*[a-zA-Z\u4e00-\u9fa5][a-zA-Z0-9\u4e00-\u9fa5]*'


def new_word(texts, dictionary=_dict, fname='new_word.xlsx'):
    """探索新词"""
    c = Counter(
        w for t in texts for s in ngram(t) for w in tk1.cut(s)
        if w not in dictionary and fullmatch(_pattern, w)).most_common()
    DataFrame(c, columns=['word', 'freq']).to_excel(fname, index=False)


def new_word_flag(texts, dictionary=_dict, fname='new_word_flag.xlsx'):
    """探索新词极其词性"""
    c = Counter(
        (w.word, w.flag) for t in texts for s in ngram(t) for w in tk2.cut(s)
        if w.word not in dictionary and fullmatch(_pattern, w.word)).most_common()
    DataFrame([(i[0], i[1], j) for i, j in c], columns=['word', 'flag', 'freq']).to_excel(fname, index=False)


def frequency(texts, fname='frequency.xlsx'):
    """词频统计"""
    c = Counter(w for t in texts for s in ngram(t) for w in tk0.cut(s) if fullmatch(_pattern, w)).most_common()
    DataFrame([(w, tk0.get_flag(w), f) for w, f in c], columns=['word', 'flag', 'freq']).to_excel(fname, index=False)
