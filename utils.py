from nltk.corpus import *
from nltk.probability import *
from nltk.model import NgramModel
from nltk.tag import *

from nltk import *


################################################################################
# Initializes corpus, n for ngrams and the smoothing technique
################################################################################
def init_base(corpus_, N_, est_):

    # Sets the training set and extracts its contents as a list of words
    words = get_words_list_from_corpus(corpus_)

    # Set the N-gram N factor
    N = N_

    # Set the smoothing estimator
    estimator = set_estimator(est_, words)

    return words, N, estimator



################################################################################
# Constructs the language model
################################################################################
def init_language_model(words, N, estimator):

    # Ngram language model based on the training set
    if estimator:
        langModel = NgramModel(N, words, estimator=estimator)
    else:
        langModel = NgramModel(N, words)

    return langModel



################################################################################
# Constructs the tagging model
################################################################################
def init_tagger_model(corpus_):

    words = get_tagged_words_list_from_corpus(corpus_)

    # Last-resort tagger
    regexp_backoff = tag.RegexpTagger([
        (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),   # cardinal numbers
        (r'(The|the|A|a|An|an)$', 'AT'),   # articles
        (r'.*able$', 'JJ'),                # adjectives
        (r'.*ness$', 'NN'),                # nouns formed from adjectives
        (r'.*ly$', 'RB'),                  # adverbs
        (r'.*s$', 'NNS'),                  # plural nouns
        (r'.*ing$', 'VBG'),                # gerunds
        (r'.*ed$', 'VBD'),                 # past tense verbs
        (r'.*', 'NN')                      # nouns (default)
        ])


    # Taggers in backoff
    tagger_1 = tag.NgramTagger(1, words, backoff=regexp_backoff)
    tagger_2 = tag.NgramTagger(2, words, backoff=tagger_1)
    tagger_3 = tag.NgramTagger(3, words, backoff=tagger_2)
    tagger_4 = tag.NgramTagger(4, words, backoff=tagger_3)


    #templates
    templates = [
        tag.brill.SymmetricProximateTokensTemplate(tag.brill.ProximateTagsRule, (1,1)),
        tag.brill.SymmetricProximateTokensTemplate(tag.brill.ProximateTagsRule, (2,2)),
        tag.brill.SymmetricProximateTokensTemplate(tag.brill.ProximateTagsRule, (1,2)),
        tag.brill.SymmetricProximateTokensTemplate(tag.brill.ProximateTagsRule, (1,3)),
        tag.brill.SymmetricProximateTokensTemplate(tag.brill.ProximateWordsRule, (1,1)),
        tag.brill.SymmetricProximateTokensTemplate(tag.brill.ProximateWordsRule, (2,2)),
        tag.brill.SymmetricProximateTokensTemplate(tag.brill.ProximateWordsRule, (1,2)),
        tag.brill.SymmetricProximateTokensTemplate(tag.brill.ProximateWordsRule, (1,3)),
        tag.brill.ProximateTokensTemplate(tag.brill.ProximateTagsRule, (-1, -1), (1,1)),
        tag.brill.ProximateTokensTemplate(tag.brill.ProximateWordsRule, (-1, -1), (1,1))
        ]

    trainer = tag.brill.FastBrillTaggerTrainer(tagger_4, templates)
    brill_tagger = trainer.train(words, max_rules=100, min_score=3)

    return brill_tagger



################################################################################
def init(corpus_, N_, est_):

    # Initialize the corpus (sentences), size N (for ngrams)
    # and the estimator (estimator) if smoothing is selected
    words, N, estimator = init_base(corpus_, N_, est_)

    # Builds the language model based on the selected base
    language_model = init_language_model(words, N, estimator)

    tag_model = init_tagger_model(corpus_)

    return language_model



################################################################################
# Sets the training set and extracts its contents as a list of words
################################################################################
def get_words_list_from_corpus(corpus_):

    sentences = ""

    # Set the training set
    # Treebank produces unorthodox results in the context of a usual conversation
    # because of its economic content.
    if corpus_ == "treebank":
        sentences = treebank.words()
    elif corpus_ == "brown":
        sentences = brown.words()
    elif corpus_ == "shakespeare":
        sentences = shakespeare.words() # TODO Review this, not compatible
    else:
        print "Falling back to treebank as training set"
        sentences = treebank.words()

    # The tokenized training set as a list
    words = []
    for sentence in sentences:
        sent = word_tokenize(sentence)
        for s in sent:
            words.append(s)

    return words



################################################################################
# Sets the training set and extracts its contents as a list of tagged words
################################################################################
def get_tagged_words_list_from_corpus(corpus_):

    sentences = ""

    # Set the training set
    # Treebank produces unorthodox results in the context of a usual conversation
    # because of its economic content.
    if corpus_ == "treebank":
        sentences = treebank.tagged_sents(simplify_tags = "universal")
    elif corpus_ == "brown":
        sentences = brown.tagged_sents(simplify_tags = "universal")
    elif corpus_ == "shakespeare":
        sentences = shakespeare.tagged_sents(simplify_tags = "universal") # TODO Review this, not compatible
    else:
        print "Falling back to treebank as training set"
        sentences = treebank.tagged_sents(simplify_tags = "universal")

    return sentences



################################################################################
# Sets the estimator for smoothing
################################################################################
def set_estimator(est_, words):

    # Find how many bins we'll need
    bins = len(words)

    # Smoother selection
    if est_ == 0:
        estimator = None
    elif est_ == 1:
        print "Using LidstoneProbDist as smoother"
        estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.1)
    elif est_ == 2:
        print "Using WittenBellProbDist as smoother"
        estimator = lambda fdist, bins: WittenBellProbDist(fdist)
    elif est_ == 3:
        print "Using SimpleGoodTuringProbDist as smoother"
        estimator = lambda fdist, bins: SimpleGoodTuringProbDist(fdist)
    elif est_== 4:
        print "Using UniformProbDist as smoother"
        estimator = lambda fdist, bins: UniformProbDist(fdist)
    elif est_== 5:
        print "Using MLEProbDist as smoother"
        estimator = lambda fdist, bins: MLEProbDist(fdist)
    elif est_== 6:
        print "Using ELEProbDist as smoother"
        estimator = lambda fdist, bins: ELEProbDist(fdist)
    elif est_== 7:
        print "Using MutableProbDist as smoother" # This is vvvvvery slow
        estimator = lambda fdist, bins: MutableProbDist(UniformProbDist(words), words)
    else:
        print "Falling back to Lidstone as smoother"
        estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.1)

    return estimator