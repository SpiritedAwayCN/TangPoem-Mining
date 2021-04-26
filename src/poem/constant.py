import pandas as pd
import numpy as np
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import Binarizer

from src.poem.Poem import TangPoem
import config as c

print('正在读取数据...')
table = pd.read_excel('data/poem_v2.xlsx')
word_list_df = pd.read_excel('data/wordlist_v2.xlsx')

max_length = word_list_df.word.str.len().max()

def cut(string, word_list, max_length, regen=False):
    words = []
    index = 0
    max_l = len(string)
    while index < max_l:
        for i in range(max_length, 0, -1):
            if string[index: index + i] in word_list:
                words.append(string[index: index + i])
                index += i
                break
        else:
            index += 1
    if regen and string[:2] == '##':
        words = words * 3
    return words

word_list = set(word_list_df.simple.values)
table['words'] = table['simple'].apply(lambda x: ' '.join(cut(x, word_list, max_length)))

split_words = table[table['line_number']!=-1]['words'].str.split(' ', expand=True).stack().rename('word').reset_index()
split_words = split_words[split_words['word'] != '']
new_data = pd.merge(table['Poem_id'], split_words, left_index=True, right_on='level_0')

df = pd.DataFrame(new_data.groupby('word').apply(lambda x: x.shape[0])).reset_index()
sym_set = set(df[df[0] > 10].word.values)
sym_set.remove('一作')

word_dictr = sorted(new_data.word.drop_duplicates().values)
word_dict = {}
for i, word in enumerate(word_dictr):
    word_dict[word] = i

poemid_dict = {}
poems = []
i = 0
for row in table.itertuples():
    if not row.Poem_id in poemid_dict.keys():
        poemid_dict[row.Poem_id] = i
        poems.append(TangPoem(row.Poem_id))
        i += 1
    poems[-1].update_data(row.line_number, row.simple, row.words)

def load_sym_matrix(path=c.sym_matrix_path):
    try:
        sym_tfidf = sparse.load_npz(path)
    except Exception:
        print('读取近义词tf-idf矩阵失败，尝试重新生成...', end='')
    
        x_indexes = []
        y_indexes = []

        for row in table.itertuples():
            if row.line_number == -1:
                continue
            sentence = row.words.split(' ')
            n = len(sentence)
            for i in range(n):
                if not sentence[i] in sym_set:
                    continue
                for j in range(n):
                    if i == j:
                        continue
                    x_indexes.append(word_dict[sentence[i]])
                    y_indexes.append(word_dict[sentence[j]])
        N = len(word_dict)
                    
        vals = [1] * len(x_indexes)
        sym_tf = sparse.coo_matrix((vals, (x_indexes, y_indexes)), shape=(N, N)).tocsr()

        sym_idf = np.zeros((N,))
        for i in sym_tf.nonzero()[1]:
            sym_idf[i] += 1
        sym_idf = np.log(len(sym_set) / (sym_idf + 1))

        sym_tfidf = sym_tf * sparse.diags(sym_idf, shape=(N, N))
        try:
            sparse.save_npz(path, sym_tfidf)
            print('完成')
        except Exception as e:
            print('生成完成，但保存失败')
            print(e.args)
    
    return cosine_similarity(sym_tfidf, dense_output=False)

def load_poem_tfidf(path=c.poem_matrix_path):
    try:
        return sparse.load_npz(path)
    except Exception:
        print('读取诗歌tf-idf矩阵失败，尝试重新生成...', end='')

    word_list = set(word_list_df.simple.values)
    table['words'] = table['simple'].apply(lambda x: ' '.join(cut(x, word_list, max_length, True)))

    split_words = table[table['line_number']!=-1]['words'].str.split(' ', expand=True).stack().rename('word').reset_index()
    split_words = split_words[split_words['word'] != '']
    new_data = pd.merge(table['Poem_id'], split_words, left_index=True, right_on='level_0')

    temp_df = new_data[['Poem_id', 'word']].drop_duplicates()
    df_series = temp_df.groupby('word')['Poem_id'].apply(lambda x: x.shape[0]).rename('idf')
    N = new_data['Poem_id'].value_counts().shape[0]
    idf = pd.DataFrame(df_series)
    idf['idf'] = np.log(N / idf)
    idf = idf['idf'].values

    tf_att = new_data.groupby(['Poem_id', 'word']).apply(lambda x: x.shape[0]).rename('tf')
    d_index = []
    t_index = []
    tfidf_v = []

    for (pid, word), value in tf_att.items():
        tid = word_dict[word]
        d_index.append(poemid_dict[pid])
        t_index.append(tid)
        tfidf_v.append(value * idf[tid])

    poem_tfidf = sparse.coo_matrix((tfidf_v, (d_index, t_index)), shape=(len(poemid_dict), len(word_dict))).tocsr()
    try:
        sparse.save_npz(path, poem_tfidf)
        print('完成')
    except Exception as e:
        print('生成完成，但保存失败')
        print(e.args)

    return poem_tfidf

print('数据读取完成')
sim = load_sym_matrix()
poem_tfidf = load_poem_tfidf()

poem_tfidf_ev = poem_tfidf.copy().tolil()
poem_tfidf_ev[:, word_dict['一作']] = 0
poem_tfidf_ev = poem_tfidf_ev.tocsr()

poem_sim = cosine_similarity(poem_tfidf_ev, dense_output=False)
thresed = poem_sim.copy()
thresed = Binarizer(threshold=0.08).transform(thresed)