import jieba
from gensim import models
from gensim import corpora
from gensim import similarities

from setting import MongoDB


# 获取MongoDB中的歌曲等音频数据，并通过机器学习训练出文本相似度模型
content_list = list(MongoDB.contents.find({}))
all_doc_list = []
for doc in content_list:
    doc_list = list(jieba.cut_for_search(doc.get("title")))
    all_doc_list.append(doc_list)
dictionary = corpora.Dictionary(all_doc_list)
corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]
lsi = models.LsiModel(corpus)
index = similarities.SparseMatrixSimilarity(lsi[corpus], num_features=len(dictionary.keys()))


# 通过用户输入查找最相似的信息
def my_xiangsidu(user_text):
    doc_test_list = list(word for word in jieba.cut_for_search(user_text))
    doc_test_vec = dictionary.doc2bow(doc_test_list)
    sim = index[lsi[doc_test_vec]]
    cc = sorted(enumerate(sim), key=lambda item: -item[1])
    result = content_list[cc[0][0]]
    return result
