from jieba import cut
from re import fullmatch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from collections import Counter

# 读取语料
with open('x_train.txt', encoding='utf-8') as f:
    x_train = f.read().strip().split("\n")
with open('y_train.txt', encoding='utf-8') as f:
    y_train = f.read().strip().split("\n")
with open('x_test.txt', encoding='utf-8') as f:
    x_test = f.read().strip().split("\n")
with open('y_test.txt', encoding='utf-8') as f:
    y_test = f.read().strip().split("\n")

# 分词器
match = lambda word: fullmatch('[a-zA-Z\u4e00-\u9fa5]+', word)
stopwords = set('的了很买是都还也我就在这那又里哦和')
tokenizer = lambda text: (word for word in cut(text, HMM=False) if match(word) and word not in stopwords)

# 向量化
vectorizer = TfidfVectorizer(tokenizer=tokenizer)
X_train = vectorizer.fit_transform(x_train)
X_test = vectorizer.transform(x_test)

# 分类模型
clf = MultinomialNB()
clf.fit(X_train, y_train)
print(clf.score(X_test, y_test))

# 可视化
yellow = lambda w: '\033[033m{}\033[0m'.format(w)
hot = lambda i: '\033[034m%.2f\033[0m' % i if i < .5 else '\033[031m%.2f\033[0m' % i

# 全监督词分类
words = Counter(word for text in x_train for word in tokenizer(text))
for word, freq in words.most_common():
    pred = clf.predict_proba(vectorizer.transform([word]))[0][1]
    print(word, yellow(freq), hot(pred))

# 半监督词分类
y_pred = clf.predict_proba(X_test)
c1, c2, c3 = Counter(), Counter(), Counter()
for text, pred in zip(x_test, y_pred):
    for word in cut(text):
        if word not in words and match(word) and word not in stopwords:
            c1[word] += 1
            c2[word] += pred[1]
            c3[word] += 0 if pred[0] > pred[1] else 1
for word, freq in c1.most_common():
    print(word, yellow(freq), hot(c2[word] / freq), hot(c3[word] / freq))
