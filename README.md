# PubMed Open Access Subset citation context harvester

I wrote this program to help me harvesting citation contexts citing ONE specific paper in the PubMed Open Access Subset (https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/).

In fact, finding which PMIDs have cited the paper (i.e., mapping) is the hard part and beyond my current skill level. To make the matter simpler, I downloaded the iCite citation report (.xlsx) from iCite (https://icite.od.nih.gov/analysis) of the paper of interest and use it as the input to find all citation contexts. Besides, you will also need the metadata file for the OA subset to find the URLs for XML files of the citing papers (ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.csv).

The output will be a .csv file including the following columns:  
- citing_pmid: PMIDs of the papers that cited the paper of interest
- cited_pmid: PMID of the paper whose citation contexts are being harvested (i.e., the paper of interest).
- in_paper_id: One paper may contain multiple citation contexts concerning the paper of interest. This column assigns a unique id to different citation context
- paragraph: the paragraph that contains a specific citation context. 
- cit_contxt: the citation context citing this paper of interest. Notice: this could be incorrect because (1) I use the citation string (e.g., 1, 28) to search for the citation context, but numbers such as 1 and 28 can appear for other reasons; (2) I only record the last sentence that contains the citation string. However, you always have a chance to read the paragraph to see whether the citation context is correct or not.

I also added a .yml file to help you reconstruct the environment that I use (i.e., all packages and their version number)

last updated: August 14, 2021
