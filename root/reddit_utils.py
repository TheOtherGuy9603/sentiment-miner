import praw, prawcore
from psaw import PushshiftAPI
from  praw.models import MoreComments
import datetime, re
from anytree import AnyNode, RenderTree


# TODO: replace list with queue
# TODO: replace_more method for more comments
# TODO: add multiple reddit client instances (test first)

# initialize reddit instance
reddit = praw.Reddit(client_id='enter id here',
                     client_secret='enter secret key here',
                     user_agent='agent name (whatever you want)')

# initializes push shift api using reddit instance
api = PushshiftAPI(reddit)

# creates a tree structure with post as root and comments as nodes
def make_submission_tree(submission, depth):
    
    try:
        # creates a root node with submission data
        if not (submission.selftext == "[removed]" or submission.selftext == "[deleted]"):
            root = AnyNode(
                            text = submission.title + re.sub(r'\\(?=\')', '', submission.selftext).replace('\n', ''),
                            score = submission.score,
                            sentiment_score = None,
                            obj = submission)
            if submission.selftext == '':
                root.text = ''
        else:
            return None
        
        # creates nodes with comment data. replies to a comment are its children
        # TODO: replace list with queue later

        # adds top level comments to tree
        comments = [[]]
        # print(submission.title)
        for comment in submission.comments:
            if not isinstance(comment, MoreComments):
                if not (comment.body == '[removed]' or comment.body == '[deleted]'):
                    comments[0].append(AnyNode(text = re.sub(r'\\(?=\')', '', comment.body).replace('\n',''),
                                            score = comment.score,
                                            parent = root,
                                            obj = comment))

        # fills in rest of tree up to a certain depth (breadth first)
        for count in range(depth):
            comments.append([])
            for parent in comments[count]:
                for reply in parent.obj.replies:
                    if not isinstance(reply, MoreComments):
                        comments[count+1].append(AnyNode(text = reply.body.replace('\n',''),
                                                        score = reply.score,
                                                        parent = parent,
                                                        obj = reply))
        
        return [[root]] + comments
    except prawcore.exceptions.Forbidden:
        # to avoid 403 error
        return None

def log_event(date, submission, score, topic):
    file = "data/" + topic + "/reddit.events"
    f = open(file, "a+")
    date_string = datetime.datetime.fromtimestamp(date).isoformat()
    f.write(date_string + ": https://www.reddit.com" + submission.permalink + " score:" + str(score) + "\n")


def delete_submission_tree(list_of_nodes):
    for level in list_of_nodes:
        for node in level:
            del node

    return None

# get submissions
def get_submissions(keywords, date):

    starttimestamp = date
    stoptimestamp = starttimestamp + 86400    # start time + one day

    search_term = keywords[0]

    for keyword in keywords[1:]:
        search_term += '|'
        search_term += keyword

    submissions = list(api.search_submissions(after=starttimestamp,
                                            before=stoptimestamp,
                                            q=search_term,
                                            limit=100))

    return submissions
    

# get subreddits
def get_subreddits(names):

    subreddits = []
    # names = ['cryptocurrency']

    for name in names:
        if sub_exists(name):
            subreddits.append(reddit.subreddit(name))
    
    return subreddits

# check if subreddit exists
def sub_exists(sub):
    exists = True
    try:
        reddit.subreddits.search_by_name(sub, exact=True)
    except:
        exists = False
    return exists


