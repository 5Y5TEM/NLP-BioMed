import requests
from bs4 import BeautifulSoup


# URL
url = 'https://lpsn.dsmz.de/archive/-alintro.html'

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

bacteria_names = list()

# Now let's fetch
req = requests.get(url, headers)
soup = BeautifulSoup(req.content, 'html.parser')

p_tags = soup.findAll('p')


for tags in p_tags:
    species = tags.find('span', {"class": "genusspecies"})
    subspecies = tags.find('span', {"class": "specificepithet"})
    if species is not None and subspecies is not None:
        name = species.text.strip()+" "+subspecies.text.strip()
        if name not in bacteria_names:
            bacteria_names.append(name)
    elif species is not None and subspecies is None:
        name = species.text.strip()
        if name not in bacteria_names:
            bacteria_names.append(name)
print(bacteria_names)




# Grab the URL and download the PDF
with open('bacteria_list2.txt', 'w') as f:
    for item in bacteria_names:
        f.write("%s\n" % item)
