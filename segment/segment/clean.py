import re


def replace_tag(html):
    """替换HTML标签"""
    # 独立元素
    html = re.sub('<br/?>|<hr/?>', '\n', html)  # 换行、水平线
    html = re.sub('(&nbsp|&e[mn]sp;|&thinsp;|&zwn?j);', ' ', html)  # 空格
    html = re.sub('<img[^>]*>', '', html)  # 图片
    html = re.sub('<!--[\s\S]*?-->', '', html)  # 注释
    html = re.sub('<style[^>]*>[\s\S]*?</style>', '', html)  # 样式
    html = re.sub('<script[^>]*>[\s\S]*?</script>', '', html)  # JavaScript
    html = html.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')  # 转义字符
    # 行内元素
    html = re.sub('<b>([\s\S]*?)</b>', lambda x: x.group(1), html)  # 粗体 bold
    html = re.sub('<u>([\s\S]*?)</u>', lambda x: x.group(1), html)  # 下划线 underline
    html = re.sub('<strong>([\s\S]*?)</strong>', lambda x: x.group(1), html)  # 粗体
    html = re.sub('<i>([\s\S]*?)</i>', lambda x: x.group(1), html)  # 斜体 italic
    html = re.sub('<mark[^>]*>([\s\S]*?)</mark>', lambda x: x.group(1), html)  # 背景填充
    html = re.sub('<em>([\s\S]*?)</em>', lambda x: x.group(1), html)  # 强调 emphasize
    html = re.sub('<font[^>]*>([\s\S]*?)</font>', lambda x: x.group(1), html)  # 字体
    html = re.sub('<a[^>]*>([\s\S]*?)</a>', lambda x: x.group(1), html)  # a：超链接
    html = re.sub('<span[^>]*>([\s\S]*?)</span>', lambda x: x.group(1), html)  # span
    # 块级元素
    html = re.sub('<p[^>]*>([\s\S]*?)</p>', lambda x: '\n%s\n' % x.group(1), html)  # 段落
    html = re.sub('<h[1-6][^>]*>([\s\S]*?)</h[1-6]>', lambda x: '\n%s\n' % x.group(1), html)  # 标题
    html = re.sub('<td[^>]*>([\s\S]*?)</td>', lambda x: ' %s ' % x.group(1), html)  # 表格
    html = re.sub('<tr[^>]*>([\s\S]*?)</tr>', lambda x: '\n%s\n' % x.group(1), html)  # 表格
    html = re.sub('<th[^>]*>([\s\S]*?)</th>', lambda x: '\n%s\n' % x.group(1), html)  # 表格
    html = re.sub('<tbody[^>]*>([\s\S]*?)</tbody>', lambda x: '\n%s\n' % x.group(1), html)  # 表格
    html = re.sub('<table[^>]*>([\s\S]*?)</table>', lambda x: '\n%s\n' % x.group(1), html)  # 表格
    html = re.sub('<li[^>]*>([\s\S]*?)</li>', lambda x: '\n%s\n' % x.group(1), html)  # 列表
    html = re.sub('<[ou]l[^>]*>([\s\S]*?)</[ou]l>', lambda x: '\n%s\n' % x.group(1), html)  # 列表
    html = re.sub('<pre[^>]*>([\s\S]*?)</pre>', lambda x: '\n%s\n' % x.group(1), html)  # 预格化，可保留连续空白符
    html = re.sub('<div[^>]*>([\s\S]*?)</div>', lambda x: '\n%s\n' % x.group(1), html)  # 分割 division
    html = re.sub('<section[^>]*>([\s\S]*?)</section>', lambda x: '\n%s\n' % x.group(1), html)  # 章节
    # 剩余标签
    html = re.sub('<[^>]*>', '', html)
    return html


def replace_punctuation(text):
    """替换标点（英→中）"""
    text = text.replace('(', '（').replace(')', '）')  # 括号
    text = re.sub('[;；]+', '；', text)  # 分号
    text = re.sub('[!！]+', '！', text)  # 叹号
    text = re.sub('[?？]+', '？', text)  # 问号
    text = re.sub('[.]{3,}|。{3,}|…+', '…', text)  # 省略号
    text = text.replace("'", '"')  # 引号
    text = re.sub('(?<=[\u4e00-\u9fa5]),(?=[\u4e00-\u9fa5])', '，', text)  # 逗号
    text = re.sub('(?<=[\u4e00-\u9fa5])[.](?=[\u4e00-\u9fa5])', '。', text)  # 句号
    return text.strip().lower()  # 转小写


def replace_space(text):
    """清除连续空白"""
    text = re.sub('\s*\n\s*', '\n', text.strip())
    return re.sub('[ \f\r\t　]+', ' ', text)


def replace_space_resolutely(text, substitution=' '):
    return re.sub('\s+', substitution, text.strip())


def replace_space_side(text):
    """根据空白两边中英文情况来清除空白"""
    def f(r):
        if re.fullmatch('[\u4e00-\u9fa5]', r.group(1)) and re.fullmatch('[\u4e00-\u9fa5]', r.group(2)):
            return r.group(1) + ' ' + r.group(2)
        elif re.fullmatch('[a-zA-Z]', r.group(1)) and re.fullmatch('[a-zA-Z]', r.group(2)):
            return r.group(1) + ' ' + r.group(2)
        else:
            return r.group(1) + r.group(2)
    return re.sub('(\S)\s+(\S)', f, text.strip())


sep1 = re.compile('[\n。…；;]+|(?<=[\u4e00-\u9fa5])[.]+(?=[\u4e00-\u9fa5])').split
sep2 = re.compile('[!！?？]+').split
sep3 = re.compile('[,，:：]+').split
sep4 = re.compile('[^a-zA-Z0-9\u4e00-\u9fa5]+').split


def text2sentence(text):
    for i in sep1(text.strip()):
        if i.strip():
            yield i.strip()


def sentence2clause(sentence):
    for i in sep2(sentence.strip()):
        if i.strip():
            yield i.strip()


def clause2phrase(clause):
    for i in sep3(clause.strip()):
        if i.strip():
            yield i.strip()


def ngram(text):
    for i in sep4(text.strip()):
        if i.strip():
            yield i.strip()


def text2phrase(text):
    for sentence in text2sentence(text):
        for clause in sentence2clause(sentence):
            for phrase in clause2phrase(clause):
                yield phrase


re_ymd = re.compile(
    '((19|20)[0-9]{2}年(0?[1-9]|1[012])月(0?[1-9]|[12][0-9]|3[01])日)|'
    '((19|20)[0-9]{2}-(0?[1-9]|1[012])-(0?[1-9]|[12][0-9]|3[01]))|'
    '((19|20)[0-9]{2}/(0?[1-9]|1[012])/(0?[1-9]|[12][0-9]|3[01]))')
re_md = re.compile('(0?[1-9]|1[012])月(0?[1-9]|[12][0-9]|3[01])日')
re_ym = re.compile('(19|20)[0-9]{2}年(0?[1-9]|1[012])月')


if __name__ == '__main__':
    text = '方式（一）申报时间：自2018年 10月 17日起至2018年 10月24日，逾期不受理'
    a = replace_space_side(text)
    print(a)
