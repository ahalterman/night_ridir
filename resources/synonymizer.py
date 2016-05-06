from gensim.models import Word2Vec
import re

word2vec_model = "/media/data/GoogleNews-vectors-negative300.bin.gz"

prebuilt = Word2Vec.load_word2vec_format(word2vec_model, binary=True)
vocab_set = set(prebuilt.vocab.keys())

def get_synonyms(word)
    word_upper = word.upper()
    word_title = word[0].capitalize() + word[1:].lower()
    word_lower = word.lower()

    word_combo = [word_upper, word_title, word_lower]
    print word_combo

    results_list = []
    for w in word_combo:
        try:
            results = prebuilt.most_similar(positive=[w], topn=20)
            results_list.extend([i[0].upper() for i in results])
            #print [i[1] for i in results]
        except KeyError:
            pass

    return set(results_list)

def synonymize(word):
    print type(word)
    if len(word) == 1:
        word = word[0]
        word = re.sub(" ", "_", word)
        syns = get_synonyms(word)
    if len(word) > 1:
        word_list = re.sub(" ", "_", word)
        syns = get_synonyms(word)
    # finish here. Handle lists of multiple words by looking up each seperately
    
