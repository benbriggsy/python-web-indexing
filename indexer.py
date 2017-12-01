import sys
import re
import string
import json

# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = []
count = 0

def write_index():
    # declare refs to global variables
    global docids
    global postings
    global vocab

    # writes to index files: docids, vocab, postings
    outlist1 = open('docids.txt', 'w')
    outlist2 = open('vocab.txt', 'w')
    outlist3 = open('postings.txt', 'w')

    json.dump(docids, outlist1)
    json.dump(vocab, outlist2)
    json.dump(postings, outlist3)

    outlist1.close()
    outlist2.close()
    outlist3.close()

    return

##################################################################
#
# clean_html(page_contents) takes the HTML contents of a webpage
# as a string. The function returns a string of words seperated
# by spaces, all code and useless data has been removed.
#
# note: some unicode id's get through, this still needs to be
# sorted.
#
##################################################################
def clean_html(page_contents):

    cleaned = ''    #init the string that will be output

    spacePatterns = (       r"(<footer)(.*?)(<\/footer>)|"  #removes the footer which is the same for every page.
                            r"(<footer)(.*?)(footer>)|"     #removes the footer safety.
                            r"(<script)(.*?)(<\/script>)|"  #removes everything between script tags.
                            r"(<script)(.*?)(script>)|"     #removes script tags safety.
                            r"(<style)(.*?)(<\/style>)|"    #removes everything between style tags.
                            r"(<style)(.*?)(style>)|"       #removes style tags safety.
                            r"(<!--)(.*?)(-->)|"            #removes all HTML comments.
                            r"(<)(.*?)(>)|"                 #removes all HTML tags.
                            r"(&)(.*?)(;)"                  #removes all HTML special characters.
                        )

    cleaned = re.sub(spacePatterns, " ", page_contents, flags=re.S) #removes patterns defined above from page_contents
                                                                    #and puts the cleaned string in cleaned.
    
    cleaned = re.sub(r"n't", " not", cleaned, flags=re.S)           #this block replaces all apostrophies with the 
    cleaned = re.sub(r"'s", " is", cleaned, flags=re.S)             #appropriate words.
    cleaned = re.sub(r"'m", " am", cleaned, flags=re.S)
    cleaned = re.sub(r"'d", " would", cleaned, flags=re.S)
    cleaned = re.sub(r"'ll", " will", cleaned, flags=re.S)
    cleaned = re.sub(r"'re", " are", cleaned, flags=re.S)
    cleaned = re.sub(r"'ve", " have", cleaned, flags=re.S)

    cleaned = re.sub(r"\-", " ", cleaned, flags=re.S)               #splits up hyphenations                   

    transTable = cleaned.maketrans(" ", " ", string.punctuation);   #this block removes all punctuation
    cleaned = cleaned.translate(transTable)
    cleaned = cleaned.lower()

    cleaned = re.sub(r'(\r)+?', "", cleaned, flags=re.S)            #this block deals with all the remaining
    cleaned = re.sub(r'(\t)+?', "", cleaned, flags=re.S)            #spacing once everything has been removed
    cleaned = re.sub(r'(\n)+?', "", cleaned, flags=re.S)
    cleaned = re.sub(r'( )+', " ", cleaned, flags=re.S)

    #unicode gets through but it is fine.
    return cleaned

##################################################################
#
# make_index(url, page_contents) takes url of a webpage and 
# the HTML contents of a webpage as a string or as bytes.
# 
# This function instantiates the global variables from the given 
# webpage so they can be used to search for terms.
#
##################################################################
def make_index(url, page_contents):
    # declare refs to global variables
    global docids
    global postings
    global vocab
    global count

    urlCheck = url                                              #get rid of http(s):// since it doesn't matter
    urlCheck = re.sub(r"https://", "", urlCheck, flags=re.S)
    urlCheck = re.sub(r"http://", "", urlCheck, flags=re.S)

    docidExists = 0
    for docid in docids:                                        #Check that the docid hasn't been seen before
        if docid[0] == urlCheck:
            docidExists = 1

    if docidExists == 0:                                        #Only proccess if docid hasn't been done already

        # first convert bytes to string if necessary
        if isinstance(page_contents, bytes):
            page_contents = page_contents.decode('utf-8', 'ignore')

        #prints out the page currently being indexed to the console
        count += 1
        print('===============================================')
        print(count, ': make_index: url = ', urlCheck)
        print('===============================================')

        page_text = clean_html(page_contents)                   #Gets clean text seperated by spaces.

        tempDocidsList = []                                     #This block adds the url and doc length
        tempDocidsList.append(urlCheck)                              #to docids.
        tempDocidsList.append(len(page_text.split(" ")))
        docids.append(tempDocidsList)
        docid = len(docids)-1                                   #the docid is its position in the list.

        tokens = page_text.split(" ")                           #splits the cleaned text into a list of strings.

        for x in tokens:
            if x != "":
                if x in vocab:                                      #if the token exists in vocab
                    tokenid = vocab.index(x)                        #get the index and put in tokenid.
                else:
                    vocab.append(x)                                 #otherwise add the token to the end of
                    tokenid = vocab.index(x)                        #vocab and assign its position to tokenid.

                if tokenid in postings:                             #if the token has been seen before
                    docExists = 0                                   #flag for if docid already in the postings element
                    for doclist in postings[tokenid]:
                        if doclist[0] == docid:                     #if the docid is present
                            doclist[1] += 1                         #increment the freq
                            docExists = 1                           #set flag

                    if docExists == 0:                              #if doc doesn't exist yet
                        postings[tokenid].append(createDocEntry(docid, 1))

                   # postings[tokenid][1] += 1                       #increment the total frequency of the token

                else:
                    postings[tokenid] = []                     #otherwise create new postings element
                    postings[tokenid].append(createDocEntry(docid, 1))
                   # postings[tokenid][1] = 1                        #set frequency to 1

        ####### Note:                                                                         ########
        ####### Postings is in the format ["vocabID": [[[docID, frequency]], totalFrequency]] ########

    return

def createDocEntry(docid, freq):
    docFreq = []
    docFreq.append(docid)
    docFreq.append(freq)
    return docFreq

#Standard Python boiler plate
if __name__ == '__main__':
    main()
