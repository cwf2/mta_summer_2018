# Typical Scenes in Latin Epic (MTA 2018)

This repository collects documents, data and code for work on typical scenes in Classical Epic poetry, done over Summer 2018 at Mount Allison University.

Read more at the [GitHub Wiki](https://github.com/cwf2/mta_summer_2018/wiki).

The process derives and plots data from works of six different authors: Lucan, Ovid, Silius Italicus, Statius, Valerius Flaccus, and Vergil. It's broken down into 5 main steps in 5 seperate files found within the bin/ directory as follows:

1.) File: setup_0.init_cltk.py                                                                                                             Downloads the necessary tools/modules (JVReplacer, WordTokenizer, LemmaReplacer, amongst others) and tests them with the runTest()         functon when the script is run. 

JVReplacer: Replaces each instance of characters 'J' and 'V' in the text with 'I' and 'U' respectively. 

WordTokenizer: Breaks down each text into word tokens as individuals strings. 

LemmaReplacer: Converts tokens from the expressed word to the root word.

By running the script these are each tried on a few lines of Latin, in sequence. The script tests specifically for 'FileNotFoundError' and any failure to recover the Latin models. Otherwise, if an unknown error is encountered it returns 'FAIL: Unrecoverable error!'.
If no such error is encountered the script returns 'Success!' and the next file may be run.


2.)File: setup_1.dl_texts.py

When run, the script creates a destination folder for each author, if one already exists it is overwritten. Then, using the retrieveXML() function it fetches the texts and stores them in a local directory under the author name as XML files. 


3.)File: setup_2.extract_texts.py

The script in this file clears the destination directory, reads the imported corpus metadata and parses the local XML files with the parseXML() function. It then converts the files into discernable lines and stores them into a new folder as json files.


4.)File: lemmatize.py

Using the lemmanade() function, the script recalls the local json files, tokenizes the words, converts the tokens to lemmata, and saves them locally in a new folder. A gensim dictionary is created and a word count corresponding to the lemmata is stored with them according to each author. 


5.)File: sample.py

Creates sets of evenly sized samples, which can be adjusted for multiple results. The script iterates over all of the texts and uses the samples and the gensim dictionary to generate a set of vectors to be represented on a lexical dispersion plot and free to be interpreted. 



