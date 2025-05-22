
from supabase import create_client
import os
import tensorflow as tf
from transformers import TFAutoModel, AutoTokenizer
import numpy as np
import csv
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from time import sleep
import datetime

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

yesterday = str(datetime.date.today() - datetime.timedelta(days = 1)) # for any day, parse all the articles published the day before
doi_to_title_abs = {}
doi_to_vector = {}

journal_name_to_rss_url = {
    "Science" : "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
    "Science Signalling" : "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=signaling",
    "Science Translational Medicine" : "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=stm",
    "Science Advances" : "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciadv",
    "Science Immunology" : "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciimmunol",
    "Science Robotics" : "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=scirobotics",
    "Nature" : "https://www.nature.com/nature.rss",
    "Nature Aging" : "https://www.nature.com/nataging.rss",
    "Nature Astronomy" : "https://www.nature.com/natastron.rss",
    "Nature Biomedical Engineering" : "https://www.nature.com/natbiomedeng.rss",
    "Nature Biotechnology" : "https://www.nature.com/nbt.rss",
    "Nature Cancer" : "https://www.nature.com/natcancer.rss",
    "Nature Cardiovascular Research" : "https://www.nature.com/natcardiovascres.rss",
    "Nature Catalysis" : "https://www.nature.com/natcatal.rss",
    "Nature Cell Biology" : "https://www.nature.com/ncb.rss",
    "Nature Chemical Biology" : "https://www.nature.com/nchembio.rss",
    "Nature Chemical Engineering" : "https://www.nature.com/natchemeng.rss",
    "Nature Chemistry" : "https://www.nature.com/nchem.rss",
    "Nature Cities" : "https://www.nature.com/natcities.rss",
    "Nature Climate Change" : "https://www.nature.com/nclimate.rss",
    "Nature Communications" : "https://www.nature.com/ncomms.rss",
    "Nature Computational Science" : "https://www.nature.com/natcomputsci.rss",
    "Nature Ecology & Evolution" : "https://www.nature.com/natecolevol.rss",
    "Nature Electronics" : "https://www.nature.com/natelectron.rss",
    "Nature Energy" : "https://www.nature.com/nenergy.rss",
    "Nature Food" : "https://www.nature.com/natfood.rss",
    "Nature Genetics" : "https://www.nature.com/ng.rss",
    "Nature Geoscience" :"https://www.nature.com/ngeo.rss",
    "Nature Human Behaviour" : "https://www.nature.com/nathumbehav.rss",
    "Nature Immunology" : "https://www.nature.com/ni.rss",
    "Nature Machine Intelligence" : "https://www.nature.com/natmachintell.rss",
    "Nature Materials" : "https://www.nature.com/nmat.rss",
    "Nature Medicine" : "https://www.nature.com/nm.rss",
    "Nature Mental Health" : "https://www.nature.com/natmentalhealth.rss",
    "Nature Metabolism" : "https://www.nature.com/natmetab.rss",
    "Nature Methods" : "https://www.nature.com/nmeth.rss",
    "Nature Microbiology" : "https://www.nature.com/nmicrobiol.rss",
    "Nature Nanotechnology" : "https://www.nature.com/nnano.rss",
    "Nature Neuroscience" : "https://www.nature.com/neuro.rss",
    "Nature Photonics" : "https://www.nature.com/nphoton.rss",
    "Nature Physics" : "https://www.nature.com/nphys.rss",
    "Nature Plants" : "https://www.nature.com/nplants.rss",
    "Nature Protocols" : "https://www.nature.com/nprot.rss",
    "Nature Structural & Molecular Biology" : "https://www.nature.com/nsmb.rss",
    "Nature Sustainability" : "https://www.nature.com/natsustain.rss",
    "Nature Synthesis" : "https://www.nature.com/natsynth.rss",
    "Scientific Reports" : "https://www.nature.com/srep.rss",
    "Cell" : "https://www.cell.com/cell/inpress.rss",
    "Cancer Cell" : "https://www.cell.com/cancer-cell/inpress.rss",
    "Cell Metabolism" : "https://www.cell.com/cell-metabolism/inpress.rss",
    "Cell Genomics" : "https://www.cell.com/cell-genomics/inpress.rss",
    "Cell Chemical Biology" : "https://www.cell.com/cell-chemical-biology/inpress.rss",
    "Cell Host & Microbe" : "https://www.cell.com/cell-host-microbe/inpress.rss",
    "Cell Reports" : "https://www.cell.com/cell-reports/inpress.rss",
    "Cell Reports Medicine" : "https://www.cell.com/cell-reports-medicine/inpress.rss",
    "Cell Stem Cell" : "https://www.cell.com/cell-stem-cell/inpress.rss",
    "Cell Systems" : "https://www.cell.com/cell-systems/inpress.rss",
    "Current Biology" : "https://www.cell.com/current-biology/inpress.rss",
    "Developmental Cell" : "https://www.cell.com/developmental-cell/inpress.rss",
    "Immunity" : "https://www.cell.com/immunity/inpress.rss",
    "Med" : "https://www.cell.com/med/inpress.rss",
    "Molecular Cell" : "https://www.cell.com/molecular-cell/inpress.rss",
    "Neuron" : "https://www.cell.com/neuron/inpress.rss",
    "Structure" : "https://www.cell.com/structure/inpress.rss",
    "Cell Reports Physical Science" : "https://www.cell.com/cell-reports-physical-science/inpress.rss",
    "Chem" : "https://www.cell.com/chem/inpress.rss",
    "Chem Catalysis" : "https://www.cell.com/chem-catalysis/inpress.rss",
    "Device" : "https://www.cell.com/device/inpress.rss",
    "Joule" : "https://www.cell.com/joule/inpress.rss",
    "Matter" : "https://www.cell.com/matter/inpress.rss",
    "Cell Reports Methods" : "https://www.cell.com/cell-reports-methods/inpress.rss",
    "Cell Reports Sustainability" : "https://www.cell.com/cell-reports-sustainability/inpress.rss",
    "Heliyon" : "https://www.cell.com/heliyon/inpress.rss",
    "iScience" : "https://www.cell.com/iscience/inpress.rss",
    "One Earth" : "https://www.cell.com/one-earth/inpress.rss",
    "Patterns" : "https://www.cell.com/patterns/inpress.rss",
    "STAR Protocols" : "https://www.cell.com/star-protocols/inpress.rss",
    "PNAS" : "https://www.pnas.org/action/showFeed?type=searchTopic&taxonomyCode=type&tagCode=research-article",
    "Bioinformatics" : "https://academic.oup.com/rss/site_5139/advanceAccess_3001.xml",
    "Brain" : "https://academic.oup.com/rss/site_5367/advanceAccess_3228.xml",
    "Nucleic Acids Research" : "https://academic.oup.com/rss/site_5127/advanceAccess_3091.xml"
     }

# AAAS journals: get dois from RSS feed
def get_dois_from_rss_aaas(journal_name, date):
  dois = []
  resp = requests.get(journal_name_to_rss_url[journal_name]) # get response from rss url link
  with open('ToC.xml', 'wb') as f:  # open a .xml file , overwrite to it the content of resp
        f.write(resp.content)

  tree = ET.parse('ToC.xml')
  root = tree.getroot()
  namespaces = dict([node for _, node in ET.iterparse('ToC.xml', events=['start-ns'])]) # creates namespaces dictionary

  for child in root.findall('item', namespaces):
    if date in child.find('dc:date', namespaces).text:
      if child.find('dc:type', namespaces).text == "Research Article":
        dois.append(child.find('prism:doi', namespaces).text)

  return dois

# PNAS journals: get dois from RSS feed
def get_dois_from_rss_pnas(journal_name :str, date :str):
  dois = []
  resp = requests.get(journal_name_to_rss_url[journal_name])
  with open('ToC.xml', 'wb') as f:  # open a .xml file , overwrite to it the content of resp
        f.write(resp.content)

  tree = ET.parse('ToC.xml')
  root = tree.getroot()
  namespaces = dict([node for _, node in ET.iterparse('ToC.xml', events=['start-ns'])]) # creates namespaces dictionary

  for child in root.findall('item', namespaces):
    if date in child.find('dc:date', namespaces).text:
      dois.append(child.find('prism:doi', namespaces).text)

  return dois

# this is only used for AAAS journals and PNAS, abstract in metadata on CrossRef
def get_tlabs_from_crossref_api(doi):
  headers = {
    'User-Agent': 'paper_recommender/0.1 (mailto:{"luna.q.y.li@gmail.com"})'
    }
  base_url = "https://api.crossref.org"
  url = f"{base_url}/works/{doi}"

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an HTTPError if response code is 4xx or 5xx
  except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    raise
  except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")
    raise

  response = response.json()
  title = response.get('message', {}).get('title', '')[0]
  clean_title = BeautifulSoup(title, "html.parser").get_text()
  abstract = response.get('message', {}).get('abstract', '')
  clean_abstract = BeautifulSoup(abstract, "html.parser").get_text()
  clean_abstract = " ".join(clean_abstract.split())
  author = response.get('message', {}).get('author', '')[0]
  author = author["given"] + " " + author["family"]

  return clean_title, clean_abstract, author

# function to call crossref to get title and abstract on a list of dois, execution time is around 30s for 100 dois
def batch_call_crossref_aaas(doi_to_title_abs, doi_list):
  for i in range(0,len(doi_list)):
    title , abstract, author = get_tlabs_from_crossref_api(doi_list[i])
    link = "https://www.science.org/doi/abs/" + str(doi_list[i])
    doi_to_title_abs[doi_list[i]] = [title, abstract, link, author]
    sleep(0.1) # rests for 0.1s between crossref api calls to not exceed request limit
  return doi_to_title_abs

def batch_call_crossref_pnas(doi_to_title_abs, doi_list):
  for i in range(0,len(doi_list)):
    title , abstract, author = get_tlabs_from_crossref_api(doi_list[i])
    link = "https://www.pnas.org/doi/abs/" + str(doi_list[i])
    doi_to_title_abs[doi_list[i]] = [title, abstract, link, author]
    sleep(0.1) # rests for 0.1s between crossref api calls to not exceed request limit
  return doi_to_title_abs

# fetch "doi":["title", "description"] into a dictionary, for Nature journals
def get_info_Nature(journal_name :str, date :str, doi_to_title_abs :dict):
  resp = requests.get(journal_name_to_rss_url[journal_name])
  with open('ToC.xml', 'wb') as f:
    f.write(resp.content)
  tree = ET.parse('ToC.xml')
  root = tree.getroot()
  namespaces = dict([node for _, node in ET.iterparse('ToC.xml', events=['start-ns'])])

  for child in root.findall('item', namespaces):
    if date in child.find('dc:date', namespaces).text:
      if "/s" in child.find('prism:doi', namespaces).text: # /s indicates that this is a research article-like document
        title = BeautifulSoup(child.find('title', namespaces).text,"html.parser").get_text()
        if "Author Correction" not in title:
          if "Publisher Correction" not in title:
            doi = child.find('prism:doi', namespaces).text
            description = child.find("content:encoded", namespaces).text
            description = description.split("</p>",1)[1]
            description = BeautifulSoup(description, "html.parser").get_text()
            link = child.find('prism:url', namespaces).text
            if title == description: # some papers just have the title as the description, set description to ""
              description = ""
            author = child.find('dc:creator', namespaces)
            author = author.text if author is not None else ""
            doi_to_title_abs[doi] = [title, description, link, author]

  return doi_to_title_abs

# fetch "doi":["title", "description"] into a dictionary, for Cell journals
def get_info_Cell(journal_name :str, date :str, doi_to_title_abs :dict):
  resp = requests.get(journal_name_to_rss_url[journal_name])
  with open('ToC.xml', 'wb') as f:
    f.write(resp.content)
  tree = ET.parse('ToC.xml')
  root = tree.getroot()
  namespaces = dict([node for _, node in ET.iterparse('ToC.xml', events=['start-ns'])])

  for child in root.findall('item', namespaces):
    if date in child.find('dc:date', namespaces).text:
      if child.find('prism:section', namespaces).text in ["Article", "Short article", "Resource"]:
        doi = child.find('dc:identifier', namespaces).text
        title = child.find('title', namespaces).text
        description = child.find('description', namespaces).text
        link = child.find('link', namespaces).text
        if "?rss=yes" in link:
          link = link.replace("?rss=yes", "")
        author = child.find("dc:creator", namespaces).text
        author = author.split(",", 1)[0]

        doi_to_title_abs[doi] = [title, description, link, author]

  return doi_to_title_abs

# fetch "doi":["title", "description"] into a dictionary, for OUP journals, adjusts to some different styles
def get_info_OUP(journal_name :str, date :str, doi_to_title_abs :dict):
  headers = {
    'User-Agent': 'paper_recommender/0.1 (mailto:{"luna.q.y.li@gmail.com"})'
    }
  resp = requests.get(journal_name_to_rss_url[journal_name], headers=headers) # NOTE: OUP's .xml file is weird, can't be parsed normally
  resp = resp.content.decode('utf-8')
  root = ET.fromstring(resp)
  channel = root.find("channel")

  date_to_store = date
  #change time format
  date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d %b %Y')

  for item in channel.findall("item"):
    if date in item.find("pubDate").text:
      title = item.find("title").text
      doi = item.find("guid").text # this actually gives an https address, split to find doi
      doi = doi.split("doi.org/",1)[1]
      try:
        description = item.find("description")
        description = BeautifulSoup(description.text,"html.parser").get_text()
      except:
        description = "" 
      link = item.find("link").text
      if "?rss=1" in link:
        link = link.replace("?rss=1", "")
      author = ""

      doi_to_title_abs[doi] = [title, description, link, author]

  return doi_to_title_abs

# remember that with AAAS and PNAS, the link field is not filled out in the doi_to_title_abs dictionary, create the link using the base url
def get_date_info(journal_name_list, date, doi_to_title_abs):
  for journal in journal_name_list:
    url = journal_name_to_rss_url[journal] # call global dictionary

    if "https://www.science.org/" in url: # AAAS journal
      doi_list = get_dois_from_rss_aaas(journal, date)
      doi_to_title_abs = batch_call_crossref_aaas(doi_to_title_abs, doi_list)
      print(f"Successfully retrieved data for {journal} published on {date}!")

    elif "https://www.nature.com/" in url: # Nature portfolio journal
      doi_to_title_abs = get_info_Nature(journal, date, doi_to_title_abs)
      print(f"Successfully retrieved data for {journal} published on {date}!")

    elif "https://www.cell.com/" in url: # Cell portfolio journal
      doi_to_title_abs = get_info_Cell(journal, date, doi_to_title_abs)
      print(f"Successfully retrieved data for {journal} published on {date}!")

    elif "https://www.pnas.org/" in url: # PNAS
      doi_list = get_dois_from_rss_pnas(journal, date)
      doi_to_title_abs = batch_call_crossref_pnas(doi_to_title_abs, doi_list)
      print(f"Successfully retrieved data for {journal} published on {date}!")

    elif "https://academic.oup.com/" in url: # OUP portfolio journal
      doi_to_title_abs = get_info_OUP(journal, date, doi_to_title_abs)
      print(f"Successfully retrieved data for {journal} published on {date}!")

  return doi_to_title_abs

names = []
for key in journal_name_to_rss_url:
  names.append(key)

doi_to_title_abs = get_date_info(names, yesterday, doi_to_title_abs)

print(f"There are {len(doi_to_title_abs)} new papers published yesterday.")


# encode title + abstract into vector embeddings 
tokenizer = AutoTokenizer.from_pretrained("allenai/specter")
encoder = TFAutoModel.from_pretrained("allenai/specter")

doi_to_vector = {}

def encode_papers(doi_to_title_abs, doi_to_vector):
  papers = [doi_to_title_abs[paper][0] + tokenizer.sep_token + doi_to_title_abs[paper][1] for paper in doi_to_title_abs]
  inputs = tokenizer(papers, padding=True, return_tensors="tf")
  results = encoder(**inputs)
  last = results.last_hidden_state[:, 0, :]
  embeds = tf.nn.l2_normalize(last, axis=1) # this is the raw EagerTensor output
  embeds = tf.keras.backend.get_value(embeds)

  counter = 0 # initialise at element 0 of embeds, adds one after processing each paper
  for paper in doi_to_title_abs:
    doi_to_vector[paper] = embeds[counter]
    counter +=1

  return doi_to_vector

doi_to_vector = encode_papers(doi_to_title_abs, doi_to_vector)

print(f"{len(doi_to_vector)} new papers have been encoded.")

for key in doi_to_title_abs:
  data = {
    "doi": key,
    "title": doi_to_title_abs[key][0],
    "abstract": doi_to_title_abs[key][1],
    "author": doi_to_title_abs[key][3],
    "link": doi_to_title_abs[key][2],
    "embedding" : doi_to_vector[key].tolist() # tolist is important to make sure the data sent is JSON serialisable
    }
  response = supabase.table("latest_papers").insert(data).execute()
  if response.data:
    print("inserted new paper to latest_paper database")