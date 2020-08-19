from tika import parser
import os
import nltk
from spacy.matcher import PhraseMatcher
import spacy
from langdetect import detect
nlp = spacy.load('en_core_web_lg')
matcher = PhraseMatcher(nlp.vocab)


PAPER_DIR = "data/1500_Papers/"
SAVE_DIR = "data/sentences/1500_Papers_2.json"
# FILENAMES = ["bacteria_list_2.txt", "virus_list_2.txt", "disease_list_2.txt", "body_list.txt", "antibiotic_list_2.txt", "gene_list_2.txt"]
FILENAMES = ["virus_list.txt"]
FILEPATH = "data/lists/"

keywords = list()
pdf_sentences = list()



def grab_keywords(path):
    with open(path, 'r') as file:
        list = file.readlines()
        for item in list:
            item = item.replace("\n", "")
            keywords.append(item)



def get_pdf_text(filename):
    # Parse the PDF
    parsedPDF = parser.from_file(filename)

    # Extract the text content from the parsed PDF
    pdf = parsedPDF["content"]
    if pdf is not None:
        pdf = pdf.replace("\n", "")
        return pdf

    else: return ""



for file in FILENAMES:
    path = FILEPATH+file
    grab_keywords(path)

print(keywords)
counter = 0

words = list()

for filename in os.listdir(PAPER_DIR):
    if counter < 20:

        if filename.endswith(".pdf") or filename.endswith(".PDF"):
            # print(os.path.join(directory, filename))
            print("\nGrabbing file no." +str(counter+1) + ": ", filename)

            filename = os.path.join(PAPER_DIR, filename)

            pdf_text = get_pdf_text(filename)

            # If Pdf Text is Type None (broken)
            if pdf_text == "":
                print("Pdf broken, skipping.")
                continue

            # Lets get the sentences in a list
            sentences = nltk.tokenize.sent_tokenize(pdf_text)

            for sentence in sentences:
                # if "virus" in sentence:
                if any(key in sentence for key in keywords):
                    pdf_sentences.append(sentence)
                    for key in keywords:
                        if key in sentence:
                            words.append(key)

            counter+=1


print(pdf_sentences)
print(words)

# with open(SAVE_DIR, 'w+') as file:
#     for item in pdf_sentences:
#         file.write(item+"\n\n")




# SENTENCES_DIR = "data/sentences/1500_Papers_2.json"
#
# with open(SENTENCES_DIR, 'r') as file:
#     sentences = file.readlines()
#
# print(len(sentences))