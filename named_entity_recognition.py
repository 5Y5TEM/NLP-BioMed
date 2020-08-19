#!/usr/bin/env python
# coding: utf8
"""Example of training an additional entity type
This script shows how to add a new entity type to an existing pretrained NER
model. To keep the example short and simple, only four sentences are provided
as examples. In practice, you'll need many more — a few hundred would be a
good start. You will also likely need to mix in examples of other entity
types, which might be obtained by running the entity recognizer over unlabelled
sentences, and adding their annotations to the training set.
The actual training is performed by looping over the examples, and calling
`nlp.entity.update()`. The `update()` method steps through the words of the
input. At each word, it makes a prediction. It then consults the annotations
provided on the GoldParse instance, to see whether it was right. If it was
wrong, it adjusts its weights so that the correct action will score higher
next time.
After training your model, you can save it to a directory. We recommend
wrapping models as Python packages, for ease of deployment.
For more details, see the documentation:
* Training: https://spacy.io/usage/training
* NER: https://spacy.io/usage/linguistic-features#named-entities
Compatible with: spaCy v2.1.0+
Last tested with: v2.2.4
"""
from __future__ import unicode_literals, print_function

import plac
import random
import warnings
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
import pickle
import re


from NER_KBC_MedicalTexts.model import en_ner_disease_chem, en_ner_bionlp



import en_core_web_lg
nlp = en_core_web_lg.load()
# nlp = en_ner_bionlp.load()
# nlp = en_ner_disease_chem.load()

DATA_DIR = "data/processed/data_medium.json"

# new entity label
# LABEL = "ANIMAL"

# # training data
# # Note: If you're using an existing model, make sure to mix in examples of
# # other entity types that spaCy correctly recognized before. Otherwise, your
# # model might learn the new type, but "forget" what it previously knew.
# # https://explosion.ai/blog/pseudo-rehearsal-catastrophic-forgetting
# TRAIN_DATA = [
#     (
#         "Horses are too tall and they pretend to care about your feelings",
#         {"entities": [(0, 6, LABEL)]},
#     ),
#     ("Do they bite?", {"entities": []}),
#     (
#         "horses are too tall and they pretend to care about your feelings",
#         {"entities": [(0, 6, LABEL)]},
#     ),
#     ("horses pretend to care about your feelings", {"entities": [(0, 6, LABEL)]}),
#     (
#         "they pretend to care about your feelings, those horses",
#         {"entities": [(48, 54, LABEL)]},
#     ),
#     ("horses?", {"entities": [(0, 6, LABEL)]}),
# ]





with open(DATA_DIR, "rb") as fp:  # Unpickling
    TRAIN_DATA = pickle.load(fp)
# counter = 0
# for data in TRAIN_DATA:
#     print("Grabbing sentence: ", str(counter+1))
#     # print(data[0])
#     if data[0] is "":
#         TRAIN_DATA.remove(data)
#     counter+=1
#
# with open("data/processed/new_data.json", "wb+") as fp:
#     print("Saving trimmed data to: ", "data/processed/new_data.json")
#     pickle.dump(TRAIN_DATA, fp)



@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)



def main(model=nlp, new_model_name="biomedical", output_dir="model/002/", n_iter=200):
    """Set up the pipeline and entity recognizer, and train the new entity."""
    random.seed(0)
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")
    # Add entity recognizer to model if it's not in the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner)
    # otherwise, get it, so we can add labels to it
    else:
        ner = nlp.get_pipe("ner")


    # # ner.add_label("ANIMAL")
    ner.add_label("BACTERIA")  # add new entity label to entity recognizer
    # # Adding extraneous labels shouldn't mess anything up
    # ner.add_label("VIRUS")
    # ner.add_label("DISEASE")
    # ner.add_label("GENE")
    # ner.add_label("BODY")
    # ner.add_label("ANTIBIOTIC")
    ner.add_label("PERSON")
    ner.add_label("NORP")
    ner.add_label("FAC")
    ner.add_label("ORG")
    ner.add_label("GPE")
    ner.add_label("LOC")
    ner.add_label("PRODUCT")
    ner.add_label("EVENT")
    ner.add_label("WORK_OF_ART")
    ner.add_label("LAW")
    ner.add_label("LANGUAGE")
    ner.add_label("DATE")
    ner.add_label("TIME")
    ner.add_label("PERCENT")
    ner.add_label("MONEY")
    ner.add_label("QUANTITY")
    ner.add_label("ORDINAL")
    ner.add_label("CARDINAL")




    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.resume_training()
    move_names = list(ner.move_names)
    # get names of other pipes to disable them during training
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    # only train NER
    with nlp.disable_pipes(*other_pipes) and warnings.catch_warnings():
        # show warnings for misaligned entity spans once
        warnings.filterwarnings("once", category=UserWarning, module='spacy')

        sizes = compounding(1.0, 4.0, 1.001)
        # batch up the examples using spaCy's minibatch
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            batches = minibatch(TRAIN_DATA, size=sizes)
            losses = {}
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.35, losses=losses)
            print("Losses", losses)

    # test the trained model
    test_text = "Shigella is a bacterium and Erbovirus is a virus. But horses are animals. Meltem is my name. John Smith is not. E.Coli is also a Bacterium."
    doc = nlp(test_text)
    print("Entities in '%s'" % test_text)
    for ent in doc.ents:
        print(ent.label_, ent.text)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta["name"] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        # Check the classes have loaded back consistently
        assert nlp2.get_pipe("ner").move_names == move_names
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)


if __name__ == "__main__":
    plac.call(main)
