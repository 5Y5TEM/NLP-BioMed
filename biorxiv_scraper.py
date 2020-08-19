import requests
from bs4 import BeautifulSoup
import re

# We are going to get the search results of bioRxiv for a given search term
# -> read search term out from list

with open('data/lists/gene_list_3.txt', 'r') as file:
    bacteria_list = file.readlines()

# Number of pages we want to scrape
num_pages = 1


for search_term in bacteria_list:
# search_term = 'Acinetobacter Bbaumannii'



    # Convert search term to readable URL and filename
    # search_term = re.sub('\s+', '%252B', search_term)
    search_term = search_term.replace(" ", "%252B")
    search_term = re.sub('\s+', '', search_term)
    name = re.sub('%252B', '_', search_term)

    print("Search term: ", name)

    # bioRxiv URL
    base_url = 'https://www.biorxiv.org/search/'+search_term+'?page='

    # print("URL: ", url)


    # First we need to get the HTML of the site we want to scrape
    # We can set headers so that our requests looks like a legitimate browser
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

    # counter for file naming
    counter = 0

    article_urls = list()

    for i in range(num_pages):
        # Now let's fetch a page
        print("Grabbing page number " + str(i))
        new_url = base_url+str(i)
        print("URL: ", new_url)
        req = requests.get(new_url, headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        # print(soup.prettify())


        a_tags = soup.findAll('a', {"class": "highwire-cite-linked-title"})
        # divs = soup.findAll("div").get('href')

        # If no results found, skip to next search term
        if not a_tags:
            print("Skipping\n\n")
            break

        # print(divs[0])

        # Let's save the URLs to the results in a list
        for articles in a_tags:
            article_urls.append(articles.get('href'))





        # Grab the URL and download the PDF
        for url in article_urls:
            url = "http://www.biorxiv.org"+url+'.pdf'
            r = requests.get(url, stream=True)
            chunk_size = 2000

            print("Saving...: ", name+'_'+str(counter))
            print("From URL: ", url)

            with open('data/papers/genes/'+name+'_'+str(counter)+'.pdf', 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)

            counter += 1