import argparse

# from NER_KBC_MedicalTexts.metadata_extraction import GetMetadata
# from NER_KBC_MedicalTexts.ner_extraction import GetNER, get_class_lbls
# from NER_KBC_MedicalTexts.relation_extraction import subtree_matcher
# from NER_KBC_MedicalTexts.pdf_title_retrieval import retrieve_title
from metadata_extraction import GetMetadata
from ner_extraction import GetNER, get_class_lbls
from relation_extraction import subtree_matcher
from pdf_title_retrieval import retrieve_title
import spacy
import pandas as pd
import os
import nltk
import fitz
from tika import parser
from PyDictionary import PyDictionary
import time
import concurrent.futures
import glob
# t0 = time.time()

dictionary = PyDictionary()

# import en_core_web_sm
nlp = spacy.load('en_core_web_lg')

cmdparser = argparse.ArgumentParser(description='Get PDF Metadata')
cmdparser.add_argument('indir', type=str, help='Input dir for PDF files')
cmdparser.add_argument('outdir', type=str, default="output.xlsx", help='Output dir for xlsx file including the name')
args = cmdparser.parse_args()
xlsx_filename = args.outdir
directory = args.indir

# # where to save the xlsx sheet
# xlsx_filename = "results/fuu.xlsx"
# #
# # Paper directory
# directory = "data/test/"

print(xlsx_filename, directory)


dict = {
    "relations": [],
    "filenames": [],
    "relation_filenames": [],
    "titles": [],
    "authors": [],
    "doi": [],
    "keywords": [],
    "abstracts": []
}


def run(filename):
    ner_dict, label_dict = "", ""

    full_path = filename
    filename = filename.split("/")
    filename = filename[-1]

    print("Grabbing file: ", filename)
    dict["filenames"].append(filename)

    # full_path = os.path.join(directory, filename)

    # try:
    # Parse the PDF
    parsedPDF = parser.from_file(full_path)

    # Extract the text content from the parsed PDF
    pdf = parsedPDF["content"]

    if pdf is None:
        return "", "", ""
    # Process pdf
    pdf_clean = pdf.replace("\n", "")

    # Lets get the sentences in a list
    # sentences = nltk.tokenize.sent_tokenize(pdf_clean)

    # Get title by biggest font
    fitz_doc = fitz.open(full_path)

    # Shortening for metadata
    pdf_short = pdf.replace("\n\n", "")[:9000]

    try:
        title = retrieve_title(fitz_doc)
    except: title = None

    no_title = True

    if title is not None:
        if "http" in title: title = ""
        else:
            dict["titles"].append(title)
            no_title = False


    # Get METADATA
    pdfTitle, pdfAuthors, pdfDoi, pdfKeywords, pdfAbstract = GetMetadata(full_path, pdf, no_title)

    if no_title:
        dict["titles"].append(pdfTitle)

    dict["authors"].append((pdfAuthors))
    dict["doi"].append(pdfDoi)
    dict["keywords"].append(pdfKeywords)
    dict["abstracts"].append(pdfAbstract)

    # Get NER
    label_dict, ner_dict = GetNER(pdf_clean, filename)


    """
    NER TAGS
    """
    for key in label_dict:
        label_dict[key][1].append(label_dict[key][2])

    # except:
        # print("Skipping")






    # t1 = time.time() - t0
        # """
        # SYNONYMS
        # """
        #
        # print("Grabbing synonyms for: ")
        # for ent in ner_dict["entities"]:
        #     print("..."+ent)
        #     ner_dict["synonyms"].append(dictionary.synonym(ent))

    # t2 = time.time() - t0
    # t3 = time.time() - t0
    #
    # print("Elapsed time: \nStarted: {}  NER: {}  With Synonyms: {}  Total: {}".format(t0, t1, t2, t3))

    return ner_dict, label_dict, dict



def write_xlsx(ner_dict, label_dict, dict, xlsx_name = "output.xlsx"):
    """
    WRITING THE CSV FILE
    """

    rows = [list(x) for x in zip(dict["titles"],dict["authors"],dict["doi"],dict["keywords"],dict["abstracts"], label_dict["ORGANIZATIONS"][1],label_dict["LOCATIONS"][1], label_dict["BACTERIA"][1], label_dict["VIRUS"][1], label_dict["DISEASE"][1], label_dict["BODY"][1], label_dict["GENES"][1], label_dict["ANTIBIOTIC"][1])]
    # rows = [list(x) for x in zip(dict["filenames"],dict["titles"],dict["authors"],dict["doi"],dict["keywords"],dict["abstracts"])]

    fields = ['Title', 'Authors', 'doi', 'keywords', 'Abstract', 'Organizations', 'Locations identified', 'BACTERIA identified', 'VIRUS identified', 'DISEASE identified', 'BODY identified', 'GENES identified', 'ANTIBIOTIC identified']

    # rows_ner = [list(x) for x in zip(ner_dict["entities"], ner_dict["sentence_no"],ner_dict["index"], ner_dict["POS"], ner_dict["TAG"], ner_dict["DEP"], ner_dict["classes"], ner_dict["synonyms"])]
    rows_ner = [list(x) for x in zip(ner_dict["entities"], ner_dict["sentence_no"],ner_dict["index"], ner_dict["POS"], ner_dict["TAG"], ner_dict["DEP"], ner_dict["classes"])]


    rows_sen = [list(x) for x in zip(ner_dict["sentence_id"], ner_dict["sentence"])]



    df1 = pd.DataFrame(rows,
                       columns=fields,
                       index=[dict["filenames"]])

    df2 = pd.DataFrame(rows_ner,
                       # columns=['NER', 'Sentence No.','Word Pos in Sentence', 'POS', 'TAG', 'DEP', 'Class', 'Synonym'],
                       columns=['NER', 'Sentence No.', 'Word Pos in Sentence', 'POS', 'TAG', 'DEP', 'Class'],

                       index=[ner_dict["ner_filenames"]])

    df3 = pd.DataFrame(ner_dict["relations"],
                       columns=['Sentence No.','Entity 1 Class','Entity 1 Pos in Sentence', 'Entity 1', 'Relation Pos in Sentence', 'Tag', 'Lemma',  'Relation', 'Entity 2', 'Entity 2 Pos in Sentence', 'Entity 2 Class'],
                       index=[ner_dict["relation_filenames"]])

    df4 = pd.DataFrame(rows_sen,
                       columns=['Sentence No.', 'Sentence'],
                       index=[ner_dict["sentence_filename"]])


    writer = pd.ExcelWriter(xlsx_name, engine = 'xlsxwriter')
    df1.to_excel(writer, sheet_name = 'Metadata')
    df2.to_excel(writer, sheet_name = 'TERMS')
    df3.to_excel(writer, sheet_name = 'Tuples')
    df4.to_excel(writer, sheet_name = 'Sentences')
    writer.save()
    writer.close()

    print("Saved file to: ", xlsx_name)





# # Filenames of lists with keywords
# filenames = ["bacteria_list.txt", "virus_list.txt", "disease_list.txt", "body_list.txt", "antibiotic_list_2.txt", "gene_list.txt", "tests.txt"]
#
# # path of those lists
# filepath = "data/lists/"
#

#
#
# dict = {
#     "relations": [],
#     "filenames": [],
#     "relation_filenames": [],
#     "titles": [],
#     "authors": [],
#     "doi": [],
#     "keywords": [],
#     "abstracts": []
# }


def main():
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    # filenames = os.listdir(directory)
    filenames_pdf = glob.glob(directory+"*.pdf")
    filenames_PDF = glob.glob(directory+"*.PDF")

    filenames = filenames_PDF + filenames_pdf


    # for image_file, thumbnail_file in zip(image_files, executor.map(make_image_thumbnail, image_files)):


    a, b = list(), list()

    i = 0
    # for filename in executor.map(run, filenames):
    for filename in filenames:
        if filename.endswith(".pdf") or filename.endswith(".PDF"):
            ner_dict, label_dict, dict = run(filename)

            if ner_dict is not "" and label_dict is not "" and dict is not "":
                if i == 0:
                    a = ner_dict
                    b = label_dict
                    c = dict

                else:
                    a = {**a, **ner_dict}
                    b = {**b, **label_dict}
                    c = {**c, **dict}

                i += 1


    """
    RELATIONS
    """
    # Get relation classification
    print("Grabbing Tuple Entity Classes")
    ner_dict = get_class_lbls(a)


    write_xlsx(a, b, c, xlsx_filename)



if __name__ == '__main__':
    main()







