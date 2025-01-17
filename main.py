################################################################################
# Imports
################################################################################
import sys
import time
import datetime
import nltk_utils
import language_check_utils
import argparse
from nltk.parse.chart import ChartParser



################################################################################
# The entry point of the program
################################################################################
def main():

	# Parse the command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--corpus", type=str, help="The corpus to use for training")
	parser.add_argument("-cc", "--corpus_category", type=str, help="The specific categories of the corpus to use for training")
	parser.add_argument("-n", "--N", type=int, help="N-gram factor")
	parser.add_argument("-e", "--est", type=int, help="Which estimator to use for smoothing")
	parser.add_argument("-g", "--check_grammar", type=int, help="Whether to check for grammatical errors")
	parser.add_argument("-r", "--record", type=int, help="Record the story")
	parser.add_argument("-d", "--record_directory", type=str, help="The directory in which the story is recorded")
	args = parser.parse_args()

	corpus = args.corpus
	corpus_category = args.corpus_category
	N = args.N
	est = args.est
	record = args.record
	record_directory = args.record_directory


	if args.corpus is None:
		corpus = "treebank"
		print "--Using treebank as the default corpus"

	if args.corpus_category is None:
		corpus_category = "news"
		if corpus == "brown":
			print "--Using news as the default corpus category"

	if args.N is None:
		N = 3
		print "--Using N = 3 as default ngram factor"

	if args.est is None:
		est = 1
		print "--Using Lidstone as the default smoothing technique"

	if args.check_grammar is None:
		check_grammar = True
		print "--Using grammar checks by default"
	else:
		if args.check_grammar == 0:
			check_grammar = False
			print "--Not using grammar checks"
		else:
			check_grammar = True
			print "--Using grammar checks"

	if args.record is None:
		record = 0
	elif record > 0:
		# Default directory in which the story will be recorded
		record_directory = "stories\\"

	if args.record_directory is not None:
		record_directory = args.record_directory+"\\"
		record = 1


	if record > 0:
		# The name of the file in which the story is recorded
		file_name = record_directory + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
		print "--Story recorded in", file_name
	else:
		print "--The story below will remain strictly between us"

	# Log the parameters of the language model in `file_name`
	if record > 0:
		f = open(file_name, 'w+') # Initialize the file that we want to log to
		f.close()
		log(file_name, "N = " + str(N))
		log(file_name, "Corpus: " + corpus + "." + corpus_category)
		log(file_name, "Smoother: " + str(est))
		log(file_name, "Grammar: " + str(check_grammar))
		log(file_name, "")



	# The language induced from the corpus used
        # Required arguments are the corpus, a category to semantically and
        # grammatically limit the corpus's language, the order of the language
        # model N, and, optionally, a probability distribution, here called
        # `est`, as a smoothing operator
	langModel = nltk_utils.init(corpus, corpus_category, N, est)

	# The conversation has to have N-1 places in the beginning
	conversation = ["",] * (N-1)


	print "It took a while, but I'm ready; let's play!"
	while True:

		try:

                        # Its the human's turn.
                        # He inputs a word and that word is added to the
                        # story, or, as it is here called, the conversation.
                        # If grammar checking is employed, the human must
                        # provide a word that does not break the grammatical
                        # coherence of the so far conversation.
                        # If it does, the user is prompted to type another
                        # word instead.
			conversation = user_says(conversation, check_grammar)

                        # It's the agent's turn.
                        # The agent predicts a word based on the so far
                        # conversation and the language model it employs.
                        # The last N-1 words in the conversation act as the
                        # context in which the agent's response is based on.
                        # Again, if grammatical checking is employed, the
                        # agent has to come up with a word that does not
                        # violate the grammatical structure of the so far
                        # conversation.
			conversation = agent_says(conversation, N, langModel, check_grammar)

                        # Since conversation is a list of words,
                        # make a human readable version of it in order to
                        # print it.
			human_readable_conversation = " ".join(conversation)

			print human_readable_conversation

			# Record the conversation for experimental purposes
			if record > 0:
				log(file_name, human_readable_conversation)

                        # Necessary precautionary measure, or else, there is
                        # a division by zero. This is due to NLTK's
                        # implementation. Read the code for NLTK/model::entropy
                        # to understand why.
			if (len(conversation)-(N-1)) > N:
				if record > 0:
					log(file_name, str(langModel.entropy(conversation)))


		except KeyboardInterrupt:
			sys.exit(1)



################################################################################
# The user's response. It returns the conversation in full.
################################################################################
def user_says(conversation, check_grammar):

	# Keep a backup of the so far conversation
	if check_grammar:
		valid_conversation = list(conversation)

	# Read the user's word and check the validity of the so far conversation
	users_input_is_correct = False
	while not users_input_is_correct:

		# Read the user's word input
		users_word = raw_input()

		# Add it to the story, but keep a backup of the story so far,
		# maybe the user's input is incorrect.
		conversation.append(users_word)

                # Grammar checking?
		if check_grammar:

			# Check the conversation's correctness
			users_input_is_correct = language_check_utils.check(conversation)

                        # If the human's input violates the grammatical or
                        # syntacticall coherence of the so far conversation
                        # he is prompted to provide another word in its place.
			if not users_input_is_correct:
				print "Unacceptable input. Please try again."
				conversation = list(valid_conversation)
		else:
			users_input_is_correct = True

	return conversation



################################################################################
# The agent's response. The agent returns the conversation in full.
################################################################################
def agent_says(conversation, N, langModel, check_grammar):

	# Keep a backup of the so far conversation
	if check_grammar:
		valid_conversation = list(conversation)

	sentence_is_correct = False

	while not sentence_is_correct:

		# The last N-1 words are the context in which the next word should
		# be placed
		if N == 1:
			context = [""]
		else:
			context = conversation[-(N-1):]

		# Predict one word, add it to the story and print the story so far

		predicted_phrase = langModel.generate(1, context)

		predicted_word = predicted_phrase[-1]

		# Add the predicted word to the story,
		# but keep a backup of the story so far,
		# maybe the agent's guess is incorrect
		conversation.append(predicted_word)

		if check_grammar:

			sentence_is_correct = language_check_utils.check(conversation)

                        # If the agent's output violates the grammatical or
                        # syntacticall coherence of the so far conversation
                        # he must provide another word in its place.
			if not sentence_is_correct:
				conversation = list(valid_conversation)
		else:
			sentence_is_correct = True

	return conversation



################################################################################
# Records `content_` in the directory `filename_`
################################################################################
def log(file_, content_):
	with open(file_, 'a') as f:
		f.write(content_+ "\n")
		f.close()




if __name__ == '__main__':
	main()
