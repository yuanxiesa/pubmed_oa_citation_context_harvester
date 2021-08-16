# citation_context_harvester.py
# author: Yuanxi Fu
# this script takes in (1) an iCite report of citing articles for a PMID (cited_pmid); and
# (2) metadata file for articles archived in pubmed open access subset (oa_file.list.csv)
# and find all citation context for the cited pmid.

# package dependencies
from bs4 import BeautifulSoup as bs
import glob
import xml.etree.ElementTree as ET
import pandas as pd
from nltk.tokenize import sent_tokenize
from pathlib import Path
import requests
import tarfile
import os
import shutil


def extract_urls(icite_file, oa_list_file):
    """
    :param: icite_file: the file path of the icite_report
    :param: oa_list_file: the file path of the oa_file_list.csv downloaded from ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.csv

    :return: list of urls with two columns: PMID and File (urls without prefix)
    """

    icite = pd.read_excel(icite_file, usecols=[0])
    oa_list = pd.read_csv(oa_list_file)

    # find overlap
    overlap = icite.merge(oa_list, on='PMID')

    # get urls
    urls = overlap[['PMID', 'File']]
    urls.to_csv('data/urls.csv', index=False)

    return urls


def file_download(input_url):
    """
    :param: input_url: the urls from metadata file (without prefix)
    :return: none
    """
    prefix = 'https://ftp.ncbi.nlm.nih.gov/pub/pmc/'

    url = prefix + input_url

    # download and extract the file
    response = requests.get(url, stream=True)
    file = tarfile.open(fileobj=response.raw, mode="r|gz")
    file.extractall(path="data")


def xml_processing(cited_pmid, citing_pmid):
    """
    :param: input_cited_pmid: the pmid of the target paper whose citation contexts are being analyzed
    :param: input_citing_pmid: the pmid of the paper citing the target paper

    :return: None
    """

    # obtain file name
    name_list = glob.glob("data/PMC*/*.nxml")
    xml_file_name = name_list[0]

    # use xml.etree to extract reference number
    tree = ET.parse(xml_file_name)
    root = tree.getroot()

    find_ref = root.findall(".//*[pub-id='%s']/.." % cited_pmid)

    try:
        if len(find_ref) > 1:
            print('Find more than one ref matching the input pmid') # write into log

        ref_item = find_ref[0]
        ref_id = ref_item.attrib['id']
        for item in root.findall(".//*[pub-id='%s']/.." % cited_pmid):
            ref_id = item.attrib['id']

        print('Find in this paper, the reference number is: ', ref_id)

        # use BeautifulSoup to get paragraphs (text between <p> and </p> that contains the target reference)
        content = []

        # Read the XML file
        with open(xml_file_name, "r") as file:
            content = file.readlines()
            # Combine the lines in the list into a string
            content = "".join(content)
            bs_content = bs(content, "lxml")

        # find all p element
        p_l = bs_content.find_all('p')

        # list p_target_l contains all p element that contains the reference
        p_target_l = []

        for p in p_l:
            if p.find_all('xref', {'rid': ref_id}):
                p_target_l.append(p)

        # identify the string representing xref
        try:
            xref_str = p_target_l[0].find('xref', {'rid': ref_id}).text
            print("Find in this paper, the citation string is: ", xref_str)
            # check whether output file exists. Yes: open and read the file; No: initiate a new file
            out_file_name = 'A' + cited_pmid + '.csv'
            my_out_file = Path(out_file_name)

            if my_out_file.exists():
                storage_df = pd.read_csv(my_out_file)
            else:
                storage_df = pd.DataFrame(
                        columns=['citing_pmid', 'cited_pmid', 'in_paper_id', 'citation_str', 'paragraph', 'cit_contxt'])

            # parse text to find the sentence that contains the citation string
            for i in range(len(p_target_l)):
                paragraph = p_target_l[i].text
                sent_l = sent_tokenize(text=paragraph)
                cit_contxt = ''

                for sent in sent_l:
                    if xref_str in sent:
                        cit_contxt = sent
                        # print(cit_contxt)

                storage_df = storage_df.append({'citing_pmid': citing_pmid, 'cited_pmid': citing_pmid,
                                                    'in_paper_id': i,
                                                    'citation_str': xref_str,
                                                    'paragraph': paragraph,
                                                    'cit_contxt': cit_contxt}, ignore_index=True)

                storage_df.to_csv(out_file_name, encoding='utf-8', index=False)

        except IndexError:
            print('p_target_l is empty ...')  # in the future, write into log

    except IndexError:
        print('Find_ref is empty')  # in the future, write a log


def delete_pmc_folder():
    """
    :return: None. Delete all folders that start with PMC in data folder, after processing the content.
    """
    folder_name_l = glob.glob("data/PMC*")
    for folder_name in folder_name_l:
        shutil.rmtree(folder_name)


def main():
    print("Citation Context Harvester starts working ...")
    print("Make sure you have a folder called 'data' under the current working directory.")
    input('Press any key to continue...')

    icite_file = input('Please enter the path to the icite report: ')
    oa_list_file = input('Please enter the path to the oa metadata file: ')
    cited_pmid = input('Please enter the pmid of the paper whose citation context will be harvested: ')

    print('Extracting urls for all citing articles ...')
    urls = extract_urls(icite_file, oa_list_file)

    for i in range(len(urls)):
        print("Downloading file: ", (i + 1), '/', len(urls), ',PMID', urls.loc[i, 'PMID'])
        file_download(urls.loc[i, 'File'])

        print("Finding citation context sentences ... ")
        xml_processing(cited_pmid, urls.loc[i, 'PMID'])

        print("Delete PMC folder after content processing ...")
        delete_pmc_folder()
        print()


if __name__ == "__main__":
    main()
