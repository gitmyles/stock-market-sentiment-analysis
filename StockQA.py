#Myles' Stock Market QA System
#UD CISC882 - Dr. Kathleen Mccoy -  NLP Assignment #1 - Due 10/3/16
#Code written entirely by Myles Johnson-Gray (mjgray@udel.edu)

#This system takes an input of a text document and some number of questions that may pertain to that document. Using
#natural language processing and machine learning techniques, the system will attempt to answer the provided question(s).
#-----------------------------------------------------------------------------------------------------------------------
#IMPORTS
import nltk #Natural Language Tool Kit for Python (http://www.nltk.org)
import re # for regex
import sys # for commandline arguments
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

synonyms1 = ["rise", "rose", "increase", "climb", "grow", "grew", "inflate", "ascend", "raise", "swell", "surge", "incline",
             "improve"]  # synonyms for "rise"
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

    #Tokenize the question and remove the stopwords to extract the keywords in the question.
    split_question = nltk.word_tokenize(lower_question)
    key_words = list(set(split_question) - set(stop))
    print("Extracted key words: " + str(key_words))

    #Check if extracted keyword list contains words similar to "rise" AND "fall," so we know the type of question.
    check1, check2 = False, False
    for word in key_words:
        if ((word in synonyms1) | (word is "up")):
            check1 = True #there is a word that is a synonym for "rise"
        if word in synonyms2:
            check2 = True #there is a word that is a synonym for "fall"

    #-------------------------------------------------------------------------------------------------------------------

    #PREPARATION (Initialize variables ans find indexes/verbs.)

    # Initialize variables:
    index = []  # holds indexes found in the questions
    verb = []  # holds verbs found in the questions

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
        answer_list1 = []  # holds answers <index> rose
        answer_list2 = [] #holds answers for <index> fell

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
                    answer_list1.append(token)
                    up_score += 1
                if re.match(new_regex2, token):
                    answer_list1.append(token)
                    up_score += 1

        #Match occurrences of <index> with a synonym of fall
        for word in synonyms2:  # fall
            new_regex1 = regex1 + word + ".*\s" + noun + "\s.*$" #matches:  ^.*\s<verb>.*\s<index>\s.*$
            new_regex2 = regex2 + word + ".*$" #matches ^.*\s<index>\s.*\s<verb>.*$

            #Iterate through sentences to find the number of sentences involving <index> falling.
            for token in sentences:
                #If regex templates match the sentence, increment down_score.
                if re.match(new_regex1, token):
                    answer_list2.append(token)
                    down_score += 1
                if re.match(new_regex2, token):
                    answer_list2.append(token)
                    down_score += 1

        #Output the scores, potential answer, and sources.
        print("up_score: " + str(up_score) + " | down_score: " + str(down_score))

        #Print max(up_score, down_score) OR "No answer" if equal
        if up_score > down_score:
            print("ANSWER: It rose.")
            print(answer_list1)
        elif (down_score > up_score):
            print("ANSWER: It fell.")
            print("SOURCES: " + str(answer_list2))
        else:
            print("ANSWER: No information available to answer the question.")
        print("---------------------------------------------------------------------------")

    #Otherwise, this is a question asking the amount <index> rose/fell or opened/closed at. (QUESTION TYPE 2)
    else:
        print("This question is asking HOW MUCH <index> rose/fell, or HOW MUCH <index> opened/closed at.")
        if(len(verb) > 1): #too many non-nouns are bad for the system
            print("Perhaps this question is too complex...Try again!")
        else:
            #Initialize variables for this question type.
            final_answer = [None] * 15 #hold sentences that may contain answers
            final_score = [0] * 15 # holds scores for respective sentences
            result = [None] * 15 #holds the resulting answer
            answer_counter = 0 #counter to help assignment

            #Tokenize the question(this one has caps!), remove stop words, and use pos tagging.
            question = nltk.word_tokenize(question)
            key_words2 = list(set(question) - set(stop)) #keywords for the question
            pos_sentences = nltk.pos_tag(key_words2) #pos tagging

            #Iterate through keywords, and a if a keyword is not a "NNP" (proper noun), append it to verb list.
            for word in key_words2:
                for i in range(0, len(pos_sentences)):
                    if ((word == pos_sentences[i][0]) & (pos_sentences[i][1] != "NNP")):
                        if word not in verb:
                            verb.append(word)

            # Prepare regular expression templates.
            regex1 = "^.*\s"  # template to match <verb> before index
            regex2 = "^.*\s" + noun + "\s.*"  # template to match <index> before <verb>

            #Match occurrences of <index> with a synonym of rise if one if found.
            if (verb[0] in synonyms1): #synonym of rise
                for word in synonyms1:

                    #Add rise synonyms to regex templates with numbers.
                    new_regex1 = regex1 + word + ".*\s([0-9/%.]+).*\s" + noun + "\s.*"
                    new_regex2 = regex2 + word + ".*\s([0-9/%.]+).*\s.*"

                    #Iterate through sentences to find the sentences involving <index> rising.
                    for token in sentences:
                        #If regex templates match the sentence, store the information.
                        if re.match(new_regex1, token):
                            final_answer[answer_counter] = token #add sentence
                            final_score[answer_counter] = -.5 #add score

                            #Attempt to pull the correct answer from the sentence.
                            res = re.match(new_regex1, token)
                            if res is not None:
                                result[answer_counter] = res.group(1)
                            answer_counter += 1

                        if re.match(new_regex2, token): #the other template
                            final_answer[answer_counter] = token
                            final_score[answer_counter] = 0
                            res = re.match(new_regex2, token)
                            if res is not None:
                                result[answer_counter] = res.group(1)
                            answer_counter += 1

            #Match occurrences of <index> with a synonym of fall if one if found.
            elif (verb[0] in synonyms2):
                for word in synonyms2:
                    new_regex1 = regex1 + word + ".*\s([0-9/%.]+).*\s" + noun + "\s.*"
                    new_regex2 = regex2 + word + ".*\s([0-9/%.]+).*\s.*"

                    # Iterate through sentences to find sentences involving <index> falling.
                    for token in sentences:
                        #If regex templates match the sentence, store the information.
                        if re.match(new_regex1, token):
                            final_answer[answer_counter] = token
                            final_score[answer_counter] = -.5

                            # Attempt to pull the correct answer from the sentence.
                            res = re.match(new_regex1, token)
                            if res is not None:
                                result[answer_counter] = res.group(1)
                            answer_counter += 1

                        if re.match(new_regex2, token): #other template
                            final_answer[answer_counter] = token
                            final_score[answer_counter] = 0
                            res = re.match(new_regex2, token)
                            if res is not None:
                                result[answer_counter] = res.group(1)
                            answer_counter += 1

            #The verb does not involve a rise/fall synonym
            else:

                #Create templates
                new_regex1 = regex1 + str(verb[0]) + ".*\s([0-9/%.]+).*\s" + noun + "\s.*"
                new_regex2 = regex2 + str(verb[0]) + ".*\s([0-9/%.]+).*\s.*"

                # If regex templates match the sentence, store the information.
                for token in sentences:
                    if re.match(new_regex1, token):
                        final_answer[answer_counter] = token
                        final_score[answer_counter] = -.5

                        res = re.match(new_regex1, token)
                        if res is not None:
                            result[answer_counter] = res.group(1)
                        answer_counter += 1

                    if re.match(new_regex2, token): #other template
                        final_answer[answer_counter] = token
                        final_score[answer_counter] = 0

                        res = re.match(new_regex2, token)
                        if res is not None:
                            result[answer_counter] = res.group(1)
                        answer_counter += 1

            #Scoring (score each sentence based on the question and other criteria
            #Sentences were given a score of -.5 if <verb><index> template and 0 if generated by <index><verb> template.
            max_score = 0
            answer_index = 0 #holds index for the best answer

            for i in range(0, len(final_answer)):
                if (final_answer[i] != None): #if there is an answer...
                    if(verb[0] in final_answer[i]): #if the sentence contains the verb, increase score
                        final_score[i]+=1
                    if ("%" in result[i]):
                        final_score[i] += .5 #if answer contains "%", increase score slightly
                    if ("." in result[i]):
                        final_score[i] += .5 #if answer contains ".", increase score slightly

                    #Sentences found towards the beginning and end have slightly extra weighting.
                    final_score[i]+= .001 * ((len(final_answer) / 2) - i)

                    #Save information for best answer so far.
                    if (final_score[i] > max_score):
                        max_score = final_score[i]
                        answer_index = i

            if (max_score == 0): #if no answer found...
                print("ANSWER: No information available to answer the question.")
            else:
                print("ANSWER: " + str(result[answer_index]))
                print("SOURCE: " + str(final_answer[answer_index]))
                print("POSSIBLE ANSWERS:" + str(final_answer))
            print("---------------------------------------------------------------------------")

# -----------------------------------------------------------------------------------------------------------------------

#MAIN EXECUTION!!!!!!!!!!!!!!!

print("---------------------------------------------------------------------------")
execute = 1 #if this isn't 1, exit the program

if (len(sys.argv) > 3): #should have up to two arguments (program_name, input_file, *optional txt.file*)
    print("You've entered too many arguments. Try again!")
else:
    # Prepare tokenizer and read in desired input text file.
    tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
    fp = open(sys.argv[1])
    input_file = fp.read()

    # Tokenize input text file by sentence, then by word. Then tag with part-of-speech.
    sentences = nltk.sent_tokenize(input_file.lower())

    if(len(sys.argv) == 3): #question text file input mode
        with open(sys.argv[2]) as f:
            content = f.readlines() #read questions into array

            for i in range(0, len(content)): #answer all the questions...
                print(content[i].rstrip('\n'))
                ans_Question(content[i])
    else: #manual input mode
        while (execute == 1):
            #Read in a question from the user and print it to the screen.
            print("---------------------------------------------------------------------------")
            print("Enter 'EXIT' to leave the program.")
            question = input("Enter a question relating to the supplied stock market article:")
            if(question == "EXIT"): #user can exit the program with "EXIT"
                execute = -1
            elif(question == ""):
                print("Please type a question...")
            else:
                ans_Question(question) #answer the question