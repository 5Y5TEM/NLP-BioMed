"""
PACKAGES:
    tika
    pdftitle !
    pdfrw
    csv
    spacy
"""



from pdfrw import PdfReader
import subprocess




def GetMetadata(filename, pdf, get_title):

    digits_count = 0
    pdfTitle = ""

    try:
        pdf_clean = pdf.replace("\n", "")

        try:

            # pdfTitle = PdfReader(filename).Info.Title
            pdfAuthors = PdfReader(filename).Info.Author
            pdfDoi = None
            pdfKeywords = PdfReader(filename).Info.Keywords


            # if pdfTitle != None:
            #     pdfTitle = pdfTitle.strip('()')

            if pdfAuthors != None:
                pdfAuthors = pdfAuthors.strip('()')

            if pdfDoi != None:
                pdfDoi = pdfDoi.strip('()')

            if pdfKeywords != None:
                pdfKeywords = pdfKeywords.strip('()')
        except:
            print("Skip metadata")
            pdfTitle = None
            pdfAuthors = None
            pdfDoi = None
            pdfKeywords = None

        """
        GET PDF TITLE
        """
        if get_title:
            try:
                pdfTitle = PdfReader(filename).Info.Title
                if pdfTitle != None:
                    pdfTitle = pdfTitle.strip('()')
            except: pdfTitle = None

            if pdfTitle is None: pdfTitle = ""
            for c in pdfTitle:
                if c.isnumeric():
                    digits_count += 1

            # if string contains too many numbers or is too short, it can't be a title
            if digits_count >= 8 or len(pdfTitle) <= 20:
                pdfTitle = ""
                # try:
                #     pdfTitle = subprocess.check_output(['pdftitle', '-p', filename])
                # except:
                #     print("")
                #
                # if not pdfTitle == "":
                #     pdfTitle = pdfTitle.decode("utf-8")

            # else:
            #     if pdfTitle is None: pdfTitle = ""
            #     for c in pdfTitle:
            #         if c.isnumeric():
            #             digits_count += 1
            #
            #     # if string contains too many numbers or is too short, it can't be a title
            #     if digits_count >= 8 or len(pdfTitle) <= 10:
            #         pdfTitle = ""
            #         try:
            #             pdfTitle = subprocess.check_output(['pdftitle', '-p', filename])
            #         except:
            #             print("")
            #
            #         if not pdfTitle == "":
            #             pdfTitle = pdfTitle.decode("utf-8")



            # # Checking again if title is too short
            # if len(pdfTitle) <= 10:
            #     pdfTitle = ""

        """
        TITLE
        """
        # it might be that the title was cut off, because it contained cursive letters

        # if pdfTitle is not "":
        #     pdfTitle = pdfTitle.replace("\n", "")
        #     if pdfTitle.endswith("of") or pdfTitle.endswith("from") or pdfTitle.endswith("in") or pdfTitle.endswith("with"):
        #         if pdfTitle in pdf:
        #             title = pdf.split(pdfTitle)
        #             pdfTitle = pdfTitle + title[1][0:40]






        # Lets split the pdf paragraphs for easier handling
        splitted = pdf.split("\n\n")

        # remove all empty elements from list
        while "" in splitted:
            splitted.remove("")

        abstract_idx = 0
        doi_idx = 0
        key_idx = 0
        author_idx = 0
        has_abstract = False
        has_doi = False
        has_keywords = False
        has_author = False
        abstract_one_block = False
        author_one_block = False
        key = ""

        search_authors = True
        search_doi = True
        search_keywords = True

        x = 0

        """
        ABSTRACT
        """
        this = True
        abstract_words = ["Abstract", "ABSTRACT", "Summary", "SUMMARY", "Background", "BACKGROUND", "Objective",
                          "OBJECTIVE"]
        for text in splitted:
            if any(w in text for w in abstract_words):
                has_abstract = True

                for x in abstract_words:
                    if x in text:
                        while this is True:
                            abstract_key = x
                            if len((text.split(abstract_key))[1]) >= 20: abstract_one_block = True
                            this = False
            else:
                if not (has_abstract): abstract_idx += 1

            allAuthors = ""
            if pdfAuthors is not None and pdfAuthors is not "":
                # for string in splitted:
                if pdfAuthors in text and search_authors:
                    allAuthors = text.split(pdfAuthors)
                    pdfAuthors = pdfAuthors + allAuthors[1]
                    search_authors = False

            if pdfDoi == None and search_doi:
                # for text in splitted:
                if "doi" in text or "//doi" in text or "DOI" in text or "Doi" in text:
                    if "//doi" in text:
                        doi_key = "//doi"
                    elif ".doi" in text:
                        doi_key = ".doi"
                    elif "doi." in text:
                        doi_key = "doi."
                    elif "doi" in text:
                        doi_key = "doi"
                    elif "DOI" in text:
                        doi_key = "DOI"
                    elif "Doi" in text:
                        doi_key = "Doi"
                    has_doi = True
                    search_doi = False
                else:
                    if not(has_doi): doi_idx += 1


            if pdfKeywords == None or pdfKeywords == "":
                if search_keywords:
                    if "Keywords" in text or "keywords" in text or "KEYWORDS" in text or "Key Words" in text or "Key words" in text:
                        if "Keywords" in text:
                            key_key = "Keywords"
                        elif "keywords" in text:
                            key_key = "keywords"
                        elif "KEYWORDS" in text:
                            key_key = "KEYWORDS"
                        elif "Key Words" in text:
                            key_key = "Key Words"
                        elif "Key words" in text:
                            key_key = "Key words"

                        has_keywords = True
                        search_keywords = False
                    else:
                        if not(has_keywords): key_idx += 1


        if pdfAuthors is not None and pdfAuthors is not "":
            if len(pdfAuthors) < 10:
                pdfAuthors = None



        # If the text has the word Abstract in it
        if has_abstract:
            ab_words = ["Method", "METHOD", "Conclusion", "CONCLUSION", "Result", "RESULT"]
            i = 2
            # and if the abstract: declaration is in the same block as the text (no new lines), get the same block
            if abstract_one_block:
                pdfAbstract = splitted[abstract_idx]
                if abstract_key in pdfAbstract:
                    le_abstract = pdfAbstract.split(abstract_key)
                    pdfAbstract = le_abstract[1]
                    if len(pdfAbstract) <= 200:
                        pdfAbstract = pdfAbstract+splitted[abstract_idx+1]

            else:
                pdfAbstract = splitted[abstract_idx + 1]
                if len(pdfAbstract) <= 200:
                    pdfAbstract = pdfAbstract +"\n"+ splitted[abstract_idx+i]
                    i += 1
            # methods = splitted[abstract_idx+i]
            # conclusions = splitted[abstract_idx+i+1]
            for j in range(i, i+5):
                par = splitted[abstract_idx+j]
                if any(abKey in par for abKey in ab_words):
                    pdfAbstract = "\n" + pdfAbstract + par + "\n"

            # Last check:
            if len(pdfAbstract) <= 600:
                pdfAbstract = ""
                line = splitted[abstract_idx]
                if len(line) <= 100: line=splitted[abstract_idx+1]
                if len(line) <= 100: line=splitted[abstract_idx+2]
                y = 1

                while len(line) >= 50:
                    pdfAbstract = pdfAbstract + line + "\n"
                    line  = splitted[abstract_idx+y]
                    y += 1

        else: pdfAbstract = None


        le_doi = ""
        if has_doi:
            pdfDoi = splitted[doi_idx]
            if not "http" in pdfDoi or "www." in pdfDoi:
                le_doi = pdfDoi.split(doi_key)
                if doi_key == "//doi":
                    pdfDoi = "https://doi" + le_doi[1]
                else:
                   #pdfDoi = doi_key +" "+ le_doi[1]
                    pdfDoi = le_doi[1]

                if pdfDoi.startswith("\t"): pdfDoi.replace("\t", "")
                if pdfDoi.startswith("\n"): pdfDoi.replace("\n", "")

                if len(pdfDoi) < 5:
                    pdfDoi = splitted[doi_idx+1]
                    if not "10." in pdfDoi: pdfDoi = ""

                if pdfDoi is not None and len(pdfDoi) > 2:
                    if pdfDoi[0] == ":": pdfDoi = pdfDoi[1::]
                    if pdfDoi[0] == " ": pdfDoi = pdfDoi[1::]



            elif "http" in pdfDoi:
                le_doi = pdfDoi.split("http")
                le_doi = "http" + le_doi[1]
                le_doi = le_doi.split(" ")
                pdfDoi = le_doi[0]

            if "\n" in pdfDoi:
                pdfDoi = pdfDoi.split("\n")
                pdfDoi = pdfDoi[0]

            elif " " in pdfDoi:
                pdfDoi = pdfDoi.split(" ")
                pdfDoi = pdfDoi[0]

            elif "\t" in pdfDoi:
                pdfDoi = pdfDoi.split("\t")
                pdfDoi = pdfDoi[0]

            # Convert to URL
            if pdfDoi.startswith("10."): pdfDoi = "http://dx.doi.org/" + pdfDoi
            elif pdfDoi.startswith(".org"): pdfDoi = "http://dx.doi" + pdfDoi
            elif pdfDoi.startswith("org"): pdfDoi = "http://dx.doi." + pdfDoi

            if sum(c.isdigit() for c in pdfDoi) < 4: pdfDoi = None
            if pdfDoi is not None:
                if "http" not in pdfDoi: pdfDoi = None

            # Clean URL
            if pdfDoi is not None and pdfDoi is not "":
                while not pdfDoi[-1].isdigit():
                    pdfDoi = pdfDoi[:-1]



            # if pdfDoi[0].isalpha(): pdfDoi = None



       #else: pdfDoi = None

        le_keywords = ""
        if has_keywords:
            pdfKeywords = splitted[key_idx]
            le_keywords = pdfKeywords.split(key_key)
            pdfKeywords = le_keywords[1]

            # If Keywords are written vertically
            if len(pdfKeywords)<4:
                i = key_idx + 1
                pdfKeywords = ""
                x = True
                while x == True:
                    split = splitted[i].split(" ")
                    if len(split) == 1 or len(split) == 2 or split[1] == "":
                        pdfKeywords = pdfKeywords + splitted[i] + "\n "
                        i += 1
                    else: x = False

            # Check if whitespace in keywords
            if "\n" in pdfKeywords:
                pdfKeywords = pdfKeywords.split("\n")
                # Now check if the whitespace seperated keywords, or paragraphs
                if len(pdfKeywords) <= 2:
                    pdfKeywords = pdfKeywords[0]
                else:
                    if len(pdfKeywords[1]) > 30:
                        pdfKeywords = pdfKeywords[0]
                    else:
                        s = ""
                        for item in pdfKeywords:
                            if len(item) >= 2:
                                s = s + str(item) + ", "

                        pdfKeywords = s

            #if ":" in pdfKeywords: pdfKeywords = pdfKeywords.replace(":", "")

        # Clean Up
        if pdfKeywords is not None:
            if pdfKeywords.startswith(": "): pdfKeywords = pdfKeywords.replace(": ", "")
            elif pdfKeywords.startswith(":"): pdfKeywords = pdfKeywords.replace(":", "")





    except ImportError:
        print("Skipping Pdf!")

    return pdfTitle, pdfAuthors, pdfDoi, pdfKeywords, pdfAbstract








