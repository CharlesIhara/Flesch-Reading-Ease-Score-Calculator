# Flesch-Reading-Ease-Score-Calculator
This repository contains a script for calculating the [Flesch Reading Ease Score](https://en.wikipedia.org/wiki/Flesch–Kincaid_readability_tests) of a text. 

It uses the [CMU Pronouncing Dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict) to calculate the number of syllables, words, and sentences in a file.

This script was used in a research project at the UC Irvine Department of Obstetrics and Gynecology to score the readability of ChatGPT's responses to patient questions about Pelvic Floor Disorders (PFDs). 

The manual_counts.json file contains a dictionary of syllable counts for words that are not in the CMU Pronouncing Dictionary.

The Flesch.txt file contains a sample ChatGPT response that was scored using this script.
