
import streamlit as st
import json
from io import StringIO
from tokenizer import tokenize, detokenize
from islenska import Bin
from collections import Counter
from tokenizer import split_into_sentences
from reynir import Greynir
import random
import re
from islenska import Bin



def syns_in_ofl(orð,ofl):
    syns = combined[orð]
    syn2ofl = {x:[] for x in syns}
    for word in syns:
        for x in b.lookup(word)[1]:
            if x.ofl in ['kk','kvk', 'hk']:
                syn2ofl[word] += ['no']
            syn2ofl[word] += [x.ofl]
    syn2ofl = {k:list(set(v)) for k,v in syn2ofl.items()}

    return [k for k,v in syn2ofl.items() if ofl in v]


def get_repeated_words(text):
    ''' FINDS LEMMAS FOR ALL (PARSEABLE) WORDS'''
    all_words = []

    g = split_into_sentences(text)

    ### Find the sentences with the word:
    texts = []
    true_replacements = []
    for sent in g:
        texts += [sent]

    i = 0
    for text in texts:
        ### Check if we can parse it
        g = Greynir()
        sent = g.parse_single(text)

        sent_ok = True
        try:

          zzz = sent.tokens
          zzz = sent.tree.leaves

          while len(list(sent.tokens)) > len(list(sent.tree.leaves)):
            # stundum eyðir tree út tókum, eyðum þeim þá úr tetanum
            # fyrst eyða út þegar textinn stemmir ekki

            # let's parse only the leaves:
            text = [x for x in [y.text for y in sent.tree.leaves]]
            sent = g.parse_single(text)

        except:
          # prófum að taka burt það sem er í sviga, virkar stundum þá
          try:
            text = re.sub(r'\([^)]*\)', '', text)

            if word not in text:
              sent_ok = False
            sent = g.parse_single(text)
            zzz = sent.tokens
            zzz = sent.tree.leaves

            if len(list(sent.tokens)) > len(list(sent.tree.leaves)):

              # stundum eyðir tree út tókum, eyðum þeim þá úr tetanum
              # fyrst eyða út þegar textinn stemmir ekki
              text = [x for x in [y.text for y in sent.tree.leaves]]

              if word not in text:
                sent_ok = False

              sent = g.parse_single(text)

            if word not in text:
              sent_ok = False

          except:
            try:
              ### ef setningin er löng, skoðum þá bara það sem er á milli komma
                    ## Prófum að velja bara nærumhverfi orðsins (milli kommu og kommu td)
              for s in text.split(','):
                if word in s:

                  text = s
                  sent = g.parse_single(s)
                  sent.tokens
                  sent.tree.leaves

                  #else:
                  # print('yoooaaaa')
            except:
              print('sentence unparsable')
              #print(text)
              sent_ok = False

        if type(text) == list:
          text = str(sent)

        if sent_ok:
            ### Find the inflection and plurality of the word
            for x,y in zip(sent.tokens, sent.tree.leaves):

                for z in b.lookup(x.txt)[1]:
                    # finna staðalform
                    if z.ofl == y.cat:

                        all_words += [[x.txt, z.ord, y.tcat, '_'.join(y.variants)]]

                        break

        i+=1
    return all_words


with open('bad_synonyms.json', encoding='utf8') as f:
    bad_syns = json.load(f)
with open('synonym_dictionary.json', encoding='utf8') as f:
    combined = json.load(f)
combined = {k:list(set(v)) for k,v in combined.items()}

# remove junk and bad synonyms:
for x in [(k,v) for k,v in combined.items() if any(['valid' in x for x in v])]:
    val2 = [y for y in x[1] if 'valid' not in y]
    combined[x[0]] = val2

for x in [(k,v) for k,v in combined.items() if any(['<' in x for x in v])]:
    val2 = [y for y in x[1] if '<' not in y]
    combined[x[0]] = val2

for key,v in combined.items():
    if key in bad_syns.keys():
        badvals = bad_syns[key]
    else:
        badvals = []
    combined[key] = [x for x in v if x not in badvals]

b = Bin()


st.title("Skoðaðu hvaða orð eru oftast endurtekin í handritinu þínu til að gera það fjölbreytilegra")

uploaded = st.file_uploader("Settu inn .txt skjal með textanum hér")

### Read the file to a ilst of paragraphs
if uploaded is not None:
    text = []
    f =  stringio = StringIO(uploaded.getvalue().decode("utf-8"))

    for l in f.readlines():
        text += [l.strip().strip("'„").strip("“'")]

    text = [x for x in text if x]
    text = ' \n '.join(text)

    size = min(10000,int(len(text)/12))

    vatniðrep = []
    print(len(text))
    for i in range(int(len(text)/size)+2):
        print(i)
        print(len(vatniðrep))


        if i*size < len(text):

            st.text('Búið að lesa inn ' + str(int(i*size/len(text)*100)) + '% af orðunum í skjalinu ')
            vatniðrep += get_repeated_words(text[i*size:(i+1)*size])

    orð_í_vatni = [[x[0][0].lower()+x[0][1:]] + x[1:] for x in vatniðrep]
    cmn = Counter([(x[1], x[2]) for x in orð_í_vatni if x[2] not in ['pfn','st','fs', 'stt', 'fs', 'nhm']])


    cmn = cmn.most_common(len(cmn))
    #[(x,y) for x,y in cmn.items()]

    word2beyg = {}
    for common_word in [x for x in cmn if x[-1] > 3 ]:
        beygingar = [(x[0], x[-1]) for x in orð_í_vatni if x[1:3] == [common_word[0][0], common_word[0][1]]]
        z = dict(Counter(beygingar))

        word2beyg[common_word[0]] = {k: v for k, v in sorted(z.items(), key=lambda item: item[1], reverse=True)}
    word2beyg


    jeison = {}
    for common_word in [x for x in cmn if x[-1] > 3 ]:

        key = common_word[0][0] + ' ({})'.format(common_word[0][1])

        jeison[key] = {}
        jeison[key]['tíðni'] = common_word[-1]

        if common_word[0][0] in combined.keys():
            jeison[key]['samheiti'] = list(set(combined[common_word[0][0]]))
        else:
            jeison[key]['samheiti'] = []
        jeison[key]['beygingar'] = {k[0] + ' ({})'.format(k[1]):v for k,v in word2beyg[common_word[0]].items()}

    vatnsam = {k:v for k,v in jeison.items() if jeison[k]['samheiti'] }


    i = 0
    for k in vatnsam.keys():

        word,fl = k.split(' ')
        fl = fl.strip('(').strip(')')
        syns = vatnsam[k]['samheiti']
        synsinfl = syns_in_ofl(word,fl)
        vatnsam[k]['samheiti'] = synsinfl
    vatnsam = {k:v for k,v in vatnsam.items() if v['samheiti']}

    st.header("Orðtíðni")
    st.text("Hér eru öll orðin sem komu fyrir, í lækkandi röð eftir tíðni. \n Fyrir hvert orð er tíðnin, samheiti ef einhver og mismunandi beygingarmyndir orðsins (ásamt tíðni). ")

    st.json(jeison, expanded=False)
    st.header("Samheiti")
    st.text("Hér eru öll orðin sem samheiti fundust fyrir:")
    st.json(vatnsam, expanded=False)
    #st.json(body, *, expanded=True)



#st.json(vatnord)
