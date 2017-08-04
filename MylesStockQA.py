#Myles' Stock Market QA System
#UD CISC882 - Dr. Kathleen Mccoy -  NLP Assignment #1 - Due 10/3/16
#Code written entirely by Myles Johnson-Gray (mjgray@udel.edu)

#This system takes an input of a text document and some number of questions that may pertain to that document. Using
#natural language processing and machine learning techniques, the system will attempt to answer the provided question(s).
#-----------------------------------------------------------------------------------------------------------------------

#IMPORTS

import nltk #Natural Language Tool Kit for Python (http://www.nltk.org)
#from nltk import *
import re

#-----------------------------------------------------------------------------------------------------------------------

# TEXT PREPROCESSING (read in, tokenize, and prepare input stock market article)

# Prepare tokenizer and read in desired input text file.
tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
fp = open("assign1-wsj_2300.txt")
input_file = fp.read()

# Tokenize input text file by sentence, then by word. Then tag with part-of-speech.
sentences = nltk.sent_tokenize(input_file.lower())

#-----------------------------------------------------------------------------------------------------------------------

# KEYWORD KNOWLEDGE BASE (Synonym knowledge base for "rise" and "fall".)    *Dr. McCoy said we could hardcode this*

synonyms1 = ["rise", "rose", "up", "increase", "climb", "grow", "grew", "inflate", "ascend", "raise", "swell", "surge", "incline",
             "improve", "gain"]  # synonyms for "rise"
synonyms2 = ["fall", "fell", "down", "decrease", "decline", "lessen", "slump", "reduce", "shrink", "shrunk", "shrank", "drop", "stagnate", "slip",
             "dip", "loss", "plunge", "recess", "dive", "dove", "tumble"]  # synonyms for "fall"

#-----------------------------------------------------------------------------------------------------------------------

#ANSWER QUESTION FUNCTION (Take a question as an input and use NLP and machine learning techniques to answer.)

def ans_Question(question):

    #Prepare the stop word list.
    lower_question = question.lower()
    stop = nltk.corpus.stopwords.words("english")
    stop.extend(["?", "much", "go", "How", "&"]) #no need for these words in a question
    stop.remove("up") #this word is useful to the system
    stop.remove("down") #this word is useful to to the system
    stop.remove("s") #this word is useful to to the system
    #print(stop)

    #Tokenize the question and remove the stopwords to extract the keywords in the question.
    split_question = nltk.word_tokenize(lower_question)
    key_words = list(set(split_question) - set(stop))
    print("Extracted key words: " + str(key_words))
    print("---------------------------------------------------------------------------")

    #Check if extracted keyword list contains words similar to "rise" AND "fall," so we know the type of question.
    check1, check2 = False, False
    for word in key_words:
        if word in synonyms1:
            check1 = True #there is a word that is a synonym for "rise"
        if word in synonyms2:
            check2 = True #there is a word that is a synonym for "fall"

    #-------------------------------------------------------------------------------------------------------------------

    #PREPARATION (Initialize variables ans find indexes/verbs.)

    # Initialize variables:
    index = []  # holds indexes found in the questions
    verb = []  # holds verbs found in the questions
    answer_list1 = []  # holds answers

    # Temporarily hardcoded due to difficulties with "&".
    if ("S&P" in question):
        noun = "s&p"
    else:  # otherwise just initialize to ""
        noun = ""

    # Go through extracted keywords and determine indexes and verbs.
    for word in key_words:
        if ((word in synonyms1) | (word in synonyms2)):  # if keyword is a synonym of rise/fall...
            verb.append(word)  # append to verb list
        else:
            index.append(word)  # append to index list

    # If there is more than one index, choose the one that occurs first.
    if len(index) > 1:
        i = 0
        for i in range(0, len((split_question))):
            for word in index:
                if noun == "":  # handles S&P case and only assigns first occurrence
                    if word is split_question[i]:  # if the words match
                        noun = word  # this is our main index!!!
    else:  # otherwise if there's one index, just assign
        noun = index[0]  # this is our main index!!!

    #-------------------------------------------------------------------------------------------------------------------

    #ANSWER QUESTION (Determine the type of question and use regex to help solve.)

    #If both are true, this is question asking whether <index> rose or fell. (QUESTION TYPE 1)
    if check1 == True & check2 == True:
        print("This is a question asking WHETHER <index> rose or fell.")

        #Initialize variable for this question type.
        up_score = 0 #holds score for <index> rose
        down_score = 0 #holds score for <index> fell
        answer_list2 = [] #holds answers for <index> fell (AND "answer_list1" holds answers for <index> rose!!!)

        #Prepare regular expression templates.
        regex1 = "^.*\s" #template to match <verb> before index
        regex2 = "^.*\s" + noun + "\s.*\s" #template to match <index> before <verb>

        #Match occurrences of <index> with a synonym of rise
        for word in synonyms1: #rise
            #Add rise synonyms to regex templates.
            new_regex1 = regex1 + word + ".*\s" + noun + "\s.*$" #matches:  ^.*\s<verb>.*\s<index>\s.*$
            new_regex2 = regex2 + word + ".*$" #    matches ^.*\s<index>\s.*\s<verb>.*$

            #Iterate through sentences to find the number of sentences involving <index> rising.
            for token in sentences:
                #If regex templates match the sentence, increment up_score.
                if re.match(new_regex1, token):
                    print(token)
                    answer_list1.append(token)
                    up_score += 1
                if re.match(new_regex2, token):
                    print(token)
                    answer_list1.append(token)
                    up_score += 1

        print("---------------------------------------------------------------------------")

        #Match occurrences of <index> with a synonym of fall
        for word in synonyms2:  # fall
            new_regex1 = regex1 + word + ".*\s" + noun + "\s.*$" #matches:  ^.*\s<verb>.*\s<index>\s.*$
            new_regex2 = regex2 + word + ".*$" #matches ^.*\s<index>\s.*\s<verb>.*$

            #Iterate through sentences to find the number of sentences involving <index> falling.
            for token in sentences:
                #If regex templates match the sentence, increment up_score.
                if re.match(new_regex1, token):
                    answer_list2.append(token)
                    down_score += 1
                if re.match(new_regex2, token):
                    answer_list2.append(token)
                    down_score += 1

        print("---------------------------------------------------------------------------")

        #Output the scores, potential answer, and sources.
        print("up_score: " + str(up_score) + " / down_score: " + str(down_score))

        #Print max(up_score, down_score) OR "No answer" if equal
        if up_score > down_score:
            print("It rose")
            print(answer_list1)
        elif (down_score > up_score):
            print("It fell")
            print(answer_list2)
        else:
            print("No information available to answer the question.")

    #Otherwise, this is a question asking the amount <index> rose/fell or opened/closed at. (QUESTION TYPE 2)
    else:
        print("This question is asking HOW MUCH <index> rose/fell, or HOW MUCH <index> opened/closed at.")

        final_answer = []
        final_score = []

        question = nltk.word_tokenize(question)
        key_words2 = list(set(question) - set(stop))
        pos_sentences = nltk.pos_tag(key_words2)

        for word in key_words2:
            for i in range(0, len(pos_sentences)):
                if ((word == pos_sentences[i][0]) & (pos_sentences[i][1] != "NNP")):
                    if word not in verb:
                        verb.append(word)

        # Prepare regular expression templates.
        regex1 = "^.*\s"  # template to match <verb> before index
        regex2 = "^.*\s" + noun + "\s.*"  # template to match <index> before <verb>

        if (verb[0] in synonyms1): #synonym of rise
            for word in synonyms1:
                new_regex1 = regex1 + word + ".*\s([0-9/%.]+).*\s" + noun + "\s.*"
                new_regex2 = regex2 + word + ".*\s([0-9/%.]+).*\s.*"

                # Iterate through sentences to find the number of sentences involving <index> rising.
                for token in sentences:
                    # If regex templates match the sentence, increment up_score.
                    if re.match(new_regex1, token):
                        answer_list1.append(token)
                        final_answer[token] = re.match(new_regex1, token).groups()
                        final_score[token] = 0
                    if re.match(new_regex2, token):
                        answer_list1.append(token)
                        final_answer[token] = re.match(new_regex2, token).groups()
                        final_score[token] = 0

        elif (verb[0] in synonyms2):
            for word in synonyms2:
                new_regex1 = regex1 + word + ".*\s([0-9/%.]+).*\s" + noun + "\s.*"
                new_regex2 = regex2 + word + ".*\s([0-9/%.]+).*\s.*"

                # Iterate through sentences to find the number of sentences involving <index> rising.
                for token in sentences:
                    # If regex templates match the sentence, increment up_score.
                    if re.match(new_regex1, token):
                        answer_list1.append(token)
                        #final_answer[token] = re.match(new_regex1, token).group(0)
                        #final_score[token] = 0
                    if re.match(new_regex2, token):
                        answer_list1.append(token)
                        #final_answer[token] = re.match(new_regex2, token).group(0)
                        #final_score[token] = 0
        else:
            # if length(verb) > 1 exit
            new_regex1 = regex1 + str(verb[0]) + ".*\s([0-9/%.]+).*\s" + noun + "\s.*"
            new_regex2 = regex2 + str(verb[0]) + ".*\s([0-9/%.]+).*\s.*"

            for token in sentences:
                # If regex templates match the sentence, increment up_score.
                if re.match(new_regex1, token):
                    answer_list1.append(token)
                    final_answer[token] = re.match(new_regex1, token).groups()
                    final_score[token] = 0
                if re.match(new_regex2, token):
                    answer_list1.append(token)
                    final_answer[token] = re.match(new_regex2, token).groups()
                    final_score[token] = 0

        print(answer_list1)
# -----------------------------------------------------------------------------------------------------------------------

#MAIN EXECUTION!!!!!!!!!!!!!!!

# Read in a question from the user and print it to the screen.
print("---------------------------------------------------------------------------")
question = input("Enter a question relating to the supplied stock market article:")
print("---------------------------------------------------------------------------")

# These are the 3 types of questions I have to answer.
question = ("Did the Dow rise or fall?")  # HARDCODED RN FOR EASE
#question = ("What did Walt Disney close at?") #HARDCODED RN FOR EASE
#question = ("How much did Dow go down?") #HARDCODED RN FOR EASE
#question = ("Did Walt Disney rise or fall?")
#question = ("Did dow increase or decrease?")
#question = ("How much did the Dow drop?")
#question = ("How much did IBM fall?")


print("Input Question: " + question)
print("---------------------------------------------------------------------------")
ans_Question(question)