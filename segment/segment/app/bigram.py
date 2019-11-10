from collections import Counter
from pandas import DataFrame
from segment import tk
from segment.clean import ngram
N = 999999
STOP_WORDS = set('''
了 是 在 和 有 他 的 也 为 就 这 都 等 着 来 与 要 又 而 一个 之 以 她 去 那 但 把 我们 可 他们 并 自己 或 由 其 给 使 却
这个 它 已经 及 这样 这些 此 们 这种 如果 因为 即 其中 现在 一些 以及 同时 由于 所以 这里 因 曾 呢 但是 该 每 其他 应 吧 虽然
因此 而且 啊 应该 当时 那么 这么 仍 还有 如此 既 或者 然后 有些 那个 关于 于是 不仅 只要 且 另外 而是 还是 此外 这次 如今 就是
并且 从而 其它 尽管 还要 即使 总是 只有 只是 而言 每次 这是 就会 那是'''.strip().split())


def trigram(texts, n=2, stop_words=STOP_WORDS):
    """统计语言模型"""
    c = Counter()
    for text in texts:
        for sentence in ngram(text):
            words = [w for w in tk.cut(sentence) if w not in stop_words]
            for i in range(len(words) + 1 - n):
                c[' '.join(words[i: i + n])] += 1
    c = c.most_common(N)
    DataFrame(c, columns=['word', 'freq'])[['freq', 'word']].to_excel('%dgram.xlsx' % n, index=False)


def trigram_flag(texts, n=2, stop_words=STOP_WORDS):
    """统计语言模型（带词性）"""
    c = Counter()
    for text in texts:
        for sentence in ngram(text):
            words = [w for w in tk.cut(sentence) if w not in stop_words]
            for i in range(len(words) + 1 - n):
                word = ' '.join(words[i: i + n])
                flag = ' '.join(tk.get_flag(w) for w in words[i: i + n])
                c[(word, flag)] += 1
    c = [(k, j, i) for (i, j), k in c.most_common(N)]
    DataFrame(c, columns=['freq', 'flag', 'word']).to_excel('%dgram_flag.xlsx' % n, index=False)


def trigram_flag_sort(texts, n=2, stop_words=STOP_WORDS):
    """统计语言模型（带词性+排序）"""
    c = Counter()
    for text in texts:
        for sentence in ngram(text):
            words = [w for w in tk.cut(sentence) if w not in stop_words]
            for i in range(len(words) + 1 - n):
                wf = sorted([(tk.get_flag(w), w) for w in words[i: i + n]])
                word = ' '.join(j[1] for j in wf)
                flag = ' '.join(j[0] for j in wf)
                c[(word, flag)] += 1
    c = [(k, j, i) for (i, j), k in c.most_common(N)]
    DataFrame(c, columns=['freq', 'flag', 'word']).to_excel('%dgram_flag_sort.xlsx' % n, index=False)
