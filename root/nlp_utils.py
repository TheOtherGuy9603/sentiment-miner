import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from math import copysign

nltk.download('vader_lexicon')
# TODO: replace nltk with something that has gpu utilization or use multithreading
sid = SentimentIntensityAnalyzer()


def analyze_tree(list_of_nodes):

    tree_score = 0

    root = list_of_nodes[0][0]
    sentiment = sid.polarity_scores(root.text)
    root.pos = sentiment['pos']
    root.neg = sentiment['neg']
    root.neu = sentiment['neu']

    # finds the centroid between positive, negative, and neutral
    root.sentiment_score = (root.pos - root.neg)

    # the sentiment of the post as well as how many up/downvotes it got is important
    root.final_score = root.sentiment_score * root.score 


    tree_score += root.final_score
    for level in list_of_nodes[1:]:
        for node in level:
            sentiment = sid.polarity_scores(node.text)
            node.pos = sentiment['pos']
            node.neg = sentiment['neg']
            node.neu = sentiment['neu']

            # finds the centroid between positive, negative, and neutral
            node.sentiment_score = (node.pos - node.neg)
            # a comment with negative wording replying to a comment with negative wording is most likely positive
            parent_polarity = copysign(1, node.parent.sentiment_score)
            node.final_score = node.sentiment_score * node.score * parent_polarity
            tree_score += node.final_score

    return tree_score