# This program uses the Carnegie Mellon University Pronouncing Dictionary (http://www.speech.cs.cmu.edu/cgi-bin/cmudict)
# This dictionary contains over 134,000 words and their pronunciations for North American English
# - Each entry is a list of pronunciations
# - Each pronunciation is a list of "phonemes"

# Here is an example cmudict entry for the word 'abandon':
# {  'abandon': [ ['AH0 B AE1 N D AH0 N'] , ['AH0 B AE1 N D AH0 N'] ]  }

# Vowel phonemes carry a numerical digit indicating lexical stress:
# 0 — No stress
# 1 — Primary stress
# 2 — Secondary stress

# The key idea of this program is to count the number of phonemes that are vowels
# (aka phonemes that end in a number) to estimate the number of syllables in a given word

# NOTE: many medical terms are not included in the cmu dictionary
# For this reason, I also keep a dictionary of words encountered that are not in the CMU pronouncing dictionary
# update the dictionary with that word as the key and the # of syllables manually input by the user as the value
# this dictionary is saved as a json file called "manual_counts.json" each time the program is executed

# setup
import json
import nltk  # Natural language Toolkit Library
import ssl
import inflect  # library for converting numbers to words

# bypass SSL verification to download the cmu dictionary
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('cmudict')  # only need to run this line once
from nltk.corpus import cmudict
import re  # regular expression module

# load in the dictionary of words not in the cmu dictionary (stored as a json file)
def load_dictionary(filepath):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)  # convert json file to python dictionary
    except FileNotFoundError:
        return {}  # return an empty dictionary if no dictionary file is found

# save the updated dictionary to a json file
def save_dictionary(dictionary, out_filepath):
    with open(out_filepath, 'w') as file:
        json.dump(dictionary, file)

# replace numbers in a text with word equivalent (i.e. 1 -> one)
def replace_numbers_with_words(text):
    p = inflect.engine()
    pattern = r'\b\d+\b'
    result = re.sub(pattern,lambda x: p.number_to_words(x.group()), text)
    return result


# count and return the number of syllables in a given word
def count_syllables_in_word(word):
    current_max = 0
    d = cmudict.dict()

    if word in d:
        # if the word is in the dictionary, get the list of pronunciations
        list_of_pronunciations = d.get(word)

        # each pronunciation is a list of phonemes
        for pronunciation in list_of_pronunciations:
            list_of_phonemes = pronunciation
            list_of_syllables = []

            for phoneme in list_of_phonemes:
                # if the phoneme ends in a number, count it as a syllable
                if phoneme[-1].isdigit():
                    list_of_syllables.append(phoneme)

            # if the current pronunciation has more syllables than others, reset the max
            if len(list_of_syllables) > current_max:
                current_max = len(list_of_syllables)

        #print("syllables in " + word + " : " + str(current_max))
        return current_max

    elif word in manual_counts:
        # convert syllable count dictionary entries from string to int
        return int(manual_counts.get(word))

    else:
        # if the word is not in the CMU pronouncing dictionary, but ends in an "s", try stripping it
        # NOTE: if a word ends in "'s", the apostrophe will get handled by the elif statement in the recursive call
        if word[-1] == "s":
            word_without_s = word[:-1]
            print("Removed s ")
            return count_syllables_in_word(word_without_s)

        # else if the word ends in apostrophe, strip it as well
        elif word[-1] == "'":
            word_without_apo = word[:-1]
            print("Removed ' ")
            return count_syllables_in_word(word_without_apo)

        # if the word is not in the CMU Pronouncing Dictionary, and doesn't end in an "s" or apostrophe,
        # ask the user directly
        manual_count = input("{0} not found in dictionary. Enter the # of syllables in {0}: ".format(word))

        # update the dictionary with the user's input count and return it
        manual_counts[word] = manual_count
        return int(manual_count)

# iterate over all the words in a text file, calling count_syllables_in_word() on each word
def count_syllables_in_file(filepath):
    total_syllables = 0
    with open(filepath,'r') as file:

        # parse each line by spaces
        for line in file:

            # replace any numbers with words
            words = replace_numbers_with_words(line)

            # parse the line by spaces
            words = words.split()

            # add the syllable count for each word in the line
            for word in words:

                print(word)

                # remove punctuation, spaces, and special characters
                word = re.sub(r'[.?!:;,\"*)(]', "", word)
                print("Stripped: " + word)

                # if a word is all uppercase and longer than one letter (acronym), add the length
                if word.isupper() and len(word) > 1:
                    # remove hyphens
                    word = re.sub(r'-', "", word)
                    print("syllables in Acronym " + word + " : " + str(len(word)))
                    total_syllables += len(word)

                else:
                    word = word.lower()
                    # if a hyphenated word is encountered and more than one character (not just a hyphen)
                    # split the word and call count_syllables() on each part
                    # NOTE: for word count, hyphenated word counts as 1, but for syllable count, split it
                    if word.__contains__("-") and len(word) > 1:
                        print("Dealing with hyphenated word: " + word)
                        parts = word.split("-")
                        for part in parts:
                            total_syllables += count_syllables_in_word(part)

                    # ignore spaces, empty strings, and single hyphens
                    elif word != " " and word != "" and word != "-":
                        total_syllables += count_syllables_in_word(word)

    return total_syllables

# count the number of words in the file
def count_words_in_file(filepath):
    total_words = 0
    with open(filepath,'r') as file:

        # parse each line by spaces
        for line in file:
            words_in_line = line.strip().split(" ")
            # print("ORIGINAL:")
            # print(words_in_line)
            # print()

            # prevent blank lines from being counted as one word
            if len(words_in_line) == 1 and words_in_line[0] == "":
                pass
            else:
                # remove a "word" if it is just a "-"
                for word in words_in_line:
                    if word == "-":
                        words_in_line.remove(word)
                        # print("UPDATED:")
                        # print(words_in_line)
                        # print()

                # update the counter
                #print(len(words_in_line))
                total_words += len(words_in_line)

    return total_words

# count the number of sentences in the file
def count_sentences_in_file(filepath):
    total_sentences = 0
    with open(filepath,'r') as file:

        for line in file:

            # if the line contains no punctuation, skip it (lines that end in colons and blank lines)
            if all(char not in line for char in (".?!")):
                # print("SKIPPED LINE:")
                # print(line)
                continue

            # otherwise, parse the line by punctuation
            else:
                sentences = re.split(r'[.?!]', line)
                # print("ORIGINAL:")
                # print(sentences)
                # print()

                """
                # ERROR: This doesn't fully work if there are characters (not just empty spaces) at the end of a line
                # remove empty lines and empty strings at the end of each line
                # for sentence in sentences:
                #     if sentence.strip():
                #         continue
                #     else:
                #         sentences.remove(sentence)
                #         print("UPDATED:")
                #         print(sentences)
                #         # print(len(sentences))
                #         # print()
                """

                # update counter:
                # subtract one from the step to exclude the string of characters after the punctuation of a given line
                total_sentences += (len(sentences)-1)

    return total_sentences

# calculate the Flesch Reading Ease Score using the formula
def calculate_score(total_words,total_sentences,total_syllables):
    # ASL = # words / # sentences
    asl = total_words / total_sentences
    print("ASL: " + str(asl))

    # ASW = # syllables / # words
    asw = total_syllables / total_words
    print("ASW: " + str(asw))

    # RE = 206.835 - (1.015 * ASL) - (84.6 * ASW)
    re = 206.835 - (1.015 * asl) - (84.6 * asw)
    print("Readability Ease: " + str(re))

# Main:
# load the dictionary
dictionary_filepath = "/Users/charlesihara/PycharmProjects/UCI ChatGPT PFD Project/manual_counts.json"
manual_counts = load_dictionary(dictionary_filepath)

# load the text file to read
text_filename = "/Users/charlesihara/PycharmProjects/UCI ChatGPT PFD Project/Flesch Test.txt"
total_words = count_words_in_file(text_filename)
total_sentences = count_sentences_in_file(text_filename)
total_syllables = count_syllables_in_file(text_filename)
print("Total words in file: " + str(total_words))
print("Total sentences in file: " + str(total_sentences))
print("Total syllables in file: " + str(total_syllables))
print()
calculate_score(total_words, total_sentences, total_syllables)

# save the updated dictionary back to the json file
save_dictionary(manual_counts, dictionary_filepath)