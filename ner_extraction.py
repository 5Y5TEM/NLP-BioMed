"""
PACKAGES:
    tika
    pdftitle !
    pdfrw
    csv
    spacy
"""

# from NER_KBC_MedicalTexts.model import en_ner_disease_chem, en_ner_bionlp
# from NER_KBC_MedicalTexts.relation_extraction import subtree_matcher
from model import en_ner_disease_chem, en_ner_bionlp
from relation_extraction import subtree_matcher

import re
import nltk


import en_core_web_lg
nlp = en_core_web_lg.load()
bio_nlp = en_ner_bionlp.load()
ner_disease_chem = en_ner_disease_chem.load()



# PATH, ENTITY LIST, STRING HOLDER, DEP LIST, POS LIST
label_dict = {
    "BACTERIA": ["data/lists/bacteria_list.txt", [], "", []],
    "VIRUS": ["data/lists/virus_list.txt", [], "", []],
    "DISEASE": ["data/lists/disease_list.txt", [], "", []],
    "BODY": ["data/lists/body_list.txt", [], "", []],
    "ANTIBIOTIC": ["data/lists/antibiotic_list_2.txt", [], "", []],
    "GENES": ["data/lists/gene_list.txt", [], "", []],
    "ORGANIZATIONS": ["data/lists/facility_list.txt", [], "", []],
    "LOCATIONS": ["data/lists/country_list.txt", [], "", []],
    "OTHER": ["", [], "", []]
}

dict = {
    "relations": [],
    "filenames": [],
    "relation_filenames": [],
    "ner_filenames": [],
    "entities": [],
    "synonyms": [],
    "classes": [],
    "index": [],
    "sentence_no": [],
    "POS": [],
    "TAG": [],
    "DEP": [],
    "sentence": [],
    "sentence_filename": [],
    "sentence_id": []
}


def grab_keywords(path):
    my_list = list()
    with open(path, 'r') as file:
        sentences = file.readlines()
        for sentence in sentences:
            sentence = sentence.replace("\n", "")
            if not sentence == "":
                my_list.append(sentence)

    return my_list




def get_class_lbls(ner_dict):
    """
    ner_dict["relations"] = (sentence_no, x_lbl, x_i, x, v_i, dep, lemma, v, y, y_i, y_lbl)
    """
    for idx,item in enumerate(ner_dict["relations"]):
        x = item[3]
        y = item[8]
        x_lbl, y_lbl = "",""
        ner_dict["relations"][idx] = list(ner_dict["relations"][idx])

        search_x, search_y = True, True

        for i,ent in enumerate(ner_dict["entities"]):
            if x.lower() in ent and search_x:
                x_lbl = ner_dict["classes"][i]
                ner_dict["relations"][idx][1] = x_lbl
                search_x = False

            if y.lower() in ent and search_y:
                y_lbl = ner_dict["classes"][i]
                ner_dict["relations"][idx][10] = y_lbl
                search_y = False

            if y_lbl is "" or y_lbl is " ":
                ner_dict["relations"][idx][10] = "OTHER"
            if x_lbl is "" or x_lbl is " ":
                ner_dict["relations"][idx][1] = "OTHER"

        ner_dict["relations"][idx] = tuple(ner_dict["relations"][idx])


    return ner_dict






def GetNER(pdf_clean, filename):
    # csv_filename = "test.csv"
    list_dir = "data/lists/"

    country_list = grab_keywords(list_dir + "country_list.txt")
    facility_list = grab_keywords(list_dir + "facility_list.txt")
    bacteria_list = grab_keywords(list_dir + "bacteria_list.txt")
    virus_list = grab_keywords(list_dir + "virus_list.txt")
    disease_list = grab_keywords(list_dir + "disease_list.txt")
    body_list = grab_keywords(list_dir + "body_list.txt")
    antibiotic_list = grab_keywords(list_dir + "antibiotic_list_2.txt")
    gene_list = grab_keywords(list_dir + "gene_list.txt")






    counter = 0

    # Reset temporal strings
    try:
        for key in label_dict:
            label_dict[key][2] = ""


        """
        ENTITIES
        """
        # sentences = nltk.tokenize.sent_tokenize(pdf_clean)
        sentences = pdf_clean.split(".")
        sentence_no = 0

        for sentence in sentences:
            # if 10 <= len(sentence) <= 200:
            dict["sentence_id"].append(sentence_no)
            dict["sentence"].append(sentence)
            dict["sentence_filename"].append(filename)

            doc = nlp(sentence)
        # if len(pdf_clean) < 1000000:
        #     doc = nlp(pdf_clean)

            # tokens = list()
            # for token in doc:
            #     print("Token: ", token, "\ntag: ", token.tag_, "\n\n")
            #     tokens.append(token)

            for X in doc:
                newEnt = True
                for key in body_list:
                    if re.match(key, X.text, re.IGNORECASE):
                        if len(key) == len(X.text):
                            if key.lower() not in label_dict["BODY"][2]:
                                label_dict["BODY"][2] = label_dict["BODY"][2] + key.lower() + "; "
                                label_dict["BODY"][3].append(X.i)
                                dict["ner_filenames"].append(filename)
                                dict["entities"].append(key.lower())
                                dict["classes"].append("BODY")
                                dict["index"].append(X.i)
                                dict["POS"].append(X.pos_)
                                dict["TAG"].append(X.tag_)
                                dict["DEP"].append(X.dep_)
                                dict["sentence_no"].append(sentence_no)
                            newEnt = False

                for key in gene_list:
                    if X.text == key:
                        if key not in label_dict["GENES"][2]:
                            label_dict["GENES"][2] = label_dict["GENES"][2] + key + "; "
                            label_dict["GENES"][3].append(X.i)
                            dict["ner_filenames"].append(filename)
                            dict["entities"].append(key.lower())
                            dict["classes"].append("GENES")
                            dict["index"].append(X.i)
                            dict["POS"].append(X.pos_)
                            dict["TAG"].append(X.tag_)
                            dict["DEP"].append(X.dep_)
                            dict["sentence_no"].append(sentence_no)
                        newEnt = False

                for key in antibiotic_list:
                    if key in X.text:
                        if key not in label_dict["ANTIBIOTIC"][2]:
                            label_dict["ANTIBIOTIC"][2] = label_dict["ANTIBIOTIC"][2] + key + "; "
                            label_dict["ANTIBIOTIC"][3].append(X.i)
                            dict["ner_filenames"].append(filename)
                            dict["entities"].append(key.lower())
                            dict["classes"].append("ANTIBIOTIC")
                            dict["index"].append(X.i)
                            dict["POS"].append(X.pos_)
                            dict["TAG"].append(X.tag_)
                            dict["DEP"].append(X.dep_)
                            dict["sentence_no"].append(sentence_no)
                        newEnt = False

                if newEnt:
                    if X.text.isalpha() and (3 <= len(X.text) <= 15):
                        text = X.text
                        label = "OTHER"
                        for ent in doc.ents:
                            if X.text in str(ent):
                                text = str(ent)
                                label = ent.label_

                        if text not in label_dict["OTHER"][2]:
                            label_dict["OTHER"][2] = label_dict["OTHER"][2] + X.text + "; "
                            label_dict["OTHER"][3].append(X.i)
                            dict["ner_filenames"].append(filename)
                            dict["entities"].append(X.text.lower())
                            dict["classes"].append(label)
                            dict["index"].append(X.i)
                            dict["POS"].append(X.pos_)
                            dict["TAG"].append(X.tag_)
                            dict["DEP"].append(X.dep_)
                            dict["sentence_no"].append(sentence_no)




            for X in doc.noun_chunks:
                # if "NN" in X.tag_:
                # for X in doc.ents:
                    newEnt = True

                    # for key in body_list:
                    #     if re.match(key, X.text, re.IGNORECASE):
                    #         if len(key) == len(X.text):
                    #             if key.lower() not in label_dict["BODY"][2]:
                    #                 label_dict["BODY"][2] = label_dict["BODY"][2] + key.lower() + "; "
                    #                 label_dict["BODY"][3].append(X.root.i)
                    #                 dict["ner_filenames"].append(filename)
                    #                 dict["entities"].append(key.lower())
                    #                 dict["classes"].append("BODY")
                    #                 dict["index"].append(X.root.i)
                    #                 dict["POS"].append(X.root.pos_)
                    #                 dict["TAG"].append(X.root.tag_)
                    #                 dict["DEP"].append(X.root.dep_)
                    #                 dict["sentence_no"].append(sentence_no)
                    #             newEnt = False

                    for key in facility_list:
                        if key in X.text:
                        #if re.search(key, X.text, re.IGNORECASE):
                            if X.text not in label_dict["ORGANIZATIONS"][2]:
                                label_dict["ORGANIZATIONS"][2] = label_dict["ORGANIZATIONS"][2] + X.text + "; "
                                label_dict["ORGANIZATIONS"][3].append(X.root.i)
                                dict["ner_filenames"].append(filename)
                                dict["entities"].append(key.lower())
                                dict["classes"].append("ORGANIZATIONS")
                                dict["index"].append(X.root.i)
                                dict["POS"].append(X.root.pos_)
                                dict["TAG"].append(X.root.tag_)
                                dict["DEP"].append(X.root.dep_)
                                dict["sentence_no"].append(sentence_no)
                            newEnt = False

                    for key in country_list:
                        #if key in X.text:
                        if key in X.text:
                            if key not in label_dict["LOCATIONS"][2]:
                                label_dict["LOCATIONS"][2] = label_dict["LOCATIONS"][2] + key + "; "
                                label_dict["LOCATIONS"][3].append(X.root.i)
                                dict["ner_filenames"].append(filename)
                                dict["entities"].append(key.lower())
                                dict["classes"].append("LOCATIONS")
                                dict["index"].append(X.root.i)
                                dict["POS"].append(X.root.pos_)
                                dict["TAG"].append(X.root.tag_)
                                dict["DEP"].append(X.root.dep_)
                                dict["sentence_no"].append(sentence_no)
                            newEnt = False

                    for key in bacteria_list:
                        if key in X.text:
                            if key not in label_dict["BACTERIA"][2]:
                                label_dict["BACTERIA"][2] = label_dict["BACTERIA"][2] + key + "; "
                                label_dict["BACTERIA"][3].append(X.root.i)
                                dict["ner_filenames"].append(filename)
                                dict["entities"].append(key.lower())
                                dict["classes"].append("BACTERIA")
                                dict["index"].append(X.root.i)
                                dict["POS"].append(X.root.pos_)
                                dict["TAG"].append(X.root.tag_)
                                dict["DEP"].append(X.root.dep_)
                                dict["sentence_no"].append(sentence_no)
                            newEnt = False

                    for key in virus_list:
                        if key in X.text:
                            if key not in label_dict["VIRUS"][2]:
                                label_dict["VIRUS"][2] = label_dict["VIRUS"][2] + key + "; "
                                label_dict["VIRUS"][3].append(X.root.i)
                                dict["ner_filenames"].append(filename)
                                dict["entities"].append(key.lower())
                                dict["classes"].append("VIRUS")
                                dict["index"].append(X.root.i)
                                dict["POS"].append(X.root.pos_)
                                dict["TAG"].append(X.root.tag_)
                                dict["DEP"].append(X.root.dep_)
                                dict["sentence_no"].append(sentence_no)
                            newEnt = False

                    for key in disease_list:
                        if key in X.text:
                            if key not in label_dict["DISEASE"][2]:
                                label_dict["DISEASE"][2] = label_dict["DISEASE"][2] + key + "; "
                                label_dict["DISEASE"][3].append(X.root.i)
                                dict["ner_filenames"].append(filename)
                                dict["entities"].append(key.lower())
                                dict["classes"].append("DISEASE")
                                dict["index"].append(X.root.i)
                                dict["POS"].append(X.root.pos_)
                                dict["TAG"].append(X.root.tag_)
                                dict["DEP"].append(X.root.dep_)
                                dict["sentence_no"].append(sentence_no)
                            newEnt = False


                    if newEnt:
                        if X.text.isalpha() and (3 <= len(X.text) <= 15):
                            text = X.text
                            label = "OTHER"
                            for ent in doc.ents:
                                if X.text in str(ent):
                                    text = str(ent)
                                    label = ent.label_

                            if text not in label_dict["OTHER"][2]:
                                label_dict["OTHER"][2] = label_dict["OTHER"][2] + X.text + "; "
                                label_dict["OTHER"][3].append(X.root.i)
                                dict["ner_filenames"].append(filename)
                                dict["entities"].append(X.text.lower())
                                dict["classes"].append(label)
                                dict["index"].append(X.root.i)
                                dict["POS"].append(X.root.pos_)
                                dict["TAG"].append(X.root.tag_)
                                dict["DEP"].append(X.root.dep_)
                                dict["sentence_no"].append(sentence_no)


            # Get entity relation information
            x, v, y, x_i, y_i, v_i, lemma, dep  = subtree_matcher(doc)

            # Set entity labels empty
            x_lbl, y_lbl = "",""

            relation = (sentence_no, x_lbl, x_i, x, v_i, dep, lemma, v, y, y_i, y_lbl)
            check = (x, v, y)
            if not any(var is "" or var is " " for var in check):
                # relation = ["","","","","","","","","","",""]
                dict["relations"].append(relation)
                dict["relation_filenames"].append(filename)

            sentence_no += 1



    except ImportError:
        print("error!")


    return label_dict, dict

