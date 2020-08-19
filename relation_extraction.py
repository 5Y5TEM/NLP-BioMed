import spacy
import en_core_web_lg
nlp = en_core_web_lg.load()

#actions = ["cause", "treat", "be", "take", "inhibit", "block", "impact", "have", "transmit", "get", "affect", "resist", "indicate"]
#filter = ["review", "http", "license", "doi"]

def subtree_matcher(doc):
    x, y, v, x_i, y_i, v_i, lemma, dep = '','','','','','','', ''
    tokens = list()
    token_text = list()

    for i, tok in enumerate(doc):
        # print(tok.text, tok.dep_)
        tokens.append(tok.dep_)
        token_text.append(tok.text)

        if tok.dep_=="ROOT":
            #if any(word == tok.lemma_ for word in actions):
                # v = tok.lemma_
                v = tok.text
                v_i = tok.i
                dep = tok.dep_
                lemma = tok.lemma_

                for i, tok in enumerate(doc):
                    if "subj" in tok.dep_:
                        if x == "":
                            x = tok.text
                            x_i = tok.i

                    if "obj" in tok.dep_:
                        if y == "":
                            y = tok.text
                            y_i = tok.i



                #if any(word in x or word in y for word in filter):
                # if not any(x in ent for ent in ents) and not any(y in ent for ent in ents):
                #     x, v, y, x_i, y_i = "", "", "", "", ""

                if not v.replace(" ", "").isalpha() or not x.replace(" ", "").isalpha() or not y.replace(" ", "").isalpha(): x, v, y, x_i, y_i = "", "", "", "", ""

                if len(x)<3 or len(y)<3 or len(v)<2:  x, v, y, x_i, y_i = "", "", "", "", ""



    for i,token in enumerate(tokens):
        if token == "ROOT":
            a = len(tokens)
            if a < i+1:
            # try:
                if tokens[i+1] == "acomp":
                    v = v + " " + token_text[i+1]
                    dep = dep + "acomp"
                elif tokens[i+1] == "attr":
                    v = v + " " + token_text[i+1]
                    dep = dep + "attr"
                elif tokens[i+1] == "prep":
                    v = v + " " + token_text[i+1]
                    dep = dep + "prep"
            # except(IndexError):
            #     print("Skipping Index check")


    for chunk in doc.noun_chunks:
        root = chunk.root
        if x in chunk.text:
            x = chunk.text
        elif y in chunk.text:
            y = chunk.text


    return x, v, y, x_i, y_i, v_i, lemma, dep


#
# import en_core_web_lg
# from spacy import displacy
#
# nlp = en_core_web_lg.load()
#
# text = "Shigella flexneri isolates were obtained from Jiangsu Province, Shigella flexneri isolates were obtained from Jiangsu Province."
#
# doc = nlp(text)
# print(subtree_matcher(doc))
# # displacy.serve(doc, style="dep")


