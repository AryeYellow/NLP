"""
# 单字
^[^ ] \d\d [a-z]+\n
# 长词
^[^ ]{11} \d{1,} [a-z]+\n
# 数词
^[\u4e00-\u9fa5]{6,} \d+ m\n
^[\u4e00-\u9fa5]{2} [12] m\n
# 人名
^[\u4e00-\u9fa5]{2,} \d nrfg\n
^[\u4e00-\u9fa5]{1,2} \d\d nrfg\n
^[\u4e00-\u9fa5]{1,} \d nr\n
^[\u4e00-\u9fa5]{2} \d\d nr\n
^[\u4e00-\u9fa5]{2,3} \d nz\n
^[\u4e00-\u9fa5]{1,} \d nrt\n
"""
import pandas as pd, pickle
from os import path
PATH_JIEBA = path.join(path.dirname(__file__), 'dict.txt')
PATH_DISTRICT = path.join(path.dirname(__file__), 'district.txt')  # 中国行政区划
GET_FREQ = lambda x: {1: 2000, 2: 300, 3: 40, 4: 5}.get(x, 2)

# 读


def txt2df(fname=PATH_JIEBA, sep=' ', names=None):
    """默认读取jieba词典"""
    return pd.read_table(fname, sep, names=names, header=None)


def sheet2df(fname, sheet_name=0):
    return pd.read_excel(fname, sheet_name=sheet_name)


def pickle2dt(fname):
    with open(fname, 'rb') as f:
        return pickle.load(f)


def txt2ls(fname=PATH_DISTRICT):
    with open(fname, encoding='utf-8') as f:
        return f.read().strip().split('\n')


def read_district():
    flags = {0: 'nation', 1: 'province', 2: 'city', 3: 'district'}
    code2region = dict()
    for line in txt2ls():
        code, region = line.split(',')
        code2region[code] = region
        level = int(len(code) / 2)
        flag = flags[level]
        if level < 2:
            superior = '中央' if level == 1 else ''
        else:
            superior = code2region[code[:level * 2 - 2]]
        yield code, region, level, flag, superior


# 处理


def df2dt(df):
    assert df.shape[1] == 2
    return dict(df.values)


def ls2df(ls, columns):
    return pd.DataFrame(ls, columns=columns)


def insert_freq(df, column='word'):
    """插入【freq】列"""
    df['freq'] = df[column].str.len().apply(GET_FREQ)  # 字符串长度->分词概率
    return df


def insert_flag(df, flag):
    """插入【flag】列"""
    df['flag'] = flag
    return df


def concat(ls_of_df, freq=False):
    """合并DataFrame，按第0列去重，保留前者"""
    df = pd.concat(ls_of_df)
    if freq:  # 按freq降序
        df.sort_values(by='freq', ascending=False, inplace=True)
    return df.drop_duplicates(subset=df.columns[0])


# 写


def df2sheet(df, fname):
    fname = fname.replace('.xlsx', '') + '.xlsx'
    df.to_excel(fname, index=False)


def df2sheets(ls_of_df, sheet_names, fname):
    fname = fname.replace('.xlsx', '') + '.xlsx'
    excel_writer = pd.ExcelWriter(fname)
    for df, sheet_name in zip(ls_of_df, sheet_names):
        df.to_excel(excel_writer, sheet_name, index=False)
    excel_writer.save()


def dt2pickle(fname, dt):
    fname = fname.replace('.pickle', '') + '.pickle'
    with open(fname, 'wb') as f:
        pickle.dump(dt, f)


def ls2sheet(ls, columns=['word', 'freq'], fname='frequency'):
    if columns == ['word', 'freq']:  # 保存Counter().most_common()
        df2sheet(ls2df(ls, columns)[['freq', 'word']], fname)
    elif columns == ['word', 'flag', 'freq']:
        df2sheet(ls2df(ls, columns)[['freq', 'flag', 'word']], fname)
    else:
        df2sheet(ls2df(ls, columns), fname)


if __name__ == '__main__':
    print(txt2df())
