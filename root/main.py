from nlp_utils import analyze_tree
from reddit_utils import make_submission_tree, delete_submission_tree, get_submissions, log_event
from file_io_utils import append_to_file, read_last_date
from gtrends_utils import get_trends_data
from plot_utils import plot_data

import os
from anytree import RenderTree
import datetime as dt
import pytz
from tqdm import tqdm

# TODO: place search terms into seperate file (with multi search)

NUM_DAYS = 100

TOPIC = "bernie"
SEARCH_TERMS = ['"Bernie Sanders"','"Bernie"']
GTRENDS_SELECTION = 'United States Senator'
START_DATE = int(dt.datetime(2014,4,1).timestamp())
END_DATE = int(dt.datetime.utcnow().timestamp())

AMAX_TEMP = "data/" + TOPIC + "/amax.temp"
AMIN_TEMP = "data/" + TOPIC + "/amin.temp"

FILENAME = "data/" + TOPIC + "/reddit.data"

# checks status of file and resumes from last known point
resume_date = read_last_date(FILENAME)
if resume_date == None:
    resume_date = START_DATE


if __name__ == "__main__":
    print("collecting google trends data for " + SEARCH_TERMS[0] + "...")
    get_trends_data(TOPIC, SEARCH_TERMS[0], GTRENDS_SELECTION)
    window_max = 0
    window_min = 0
    global_max = 0
    global_min = 0
    window = [0,0,0,0,0,0,0]

    # initialize adjusted_max as zero. If a previous value exists, use that instead 
    if os.path.exists(AMAX_TEMP):
        values = [float(value.rstrip('\n')) for value in open(AMAX_TEMP)]
        adjusted_max = values[0]
        global_max = values[1]
    else:
        adjusted_max = 0
        global_max = 0
    
    # initialize adjusted_min as zero. If a previous value exists, use that instead
    if os.path.exists(AMIN_TEMP):
        values = [float(value.rstrip('\n')) for value in open(AMIN_TEMP)]
        adjusted_min = values[0]
        global_min = values[1]
    else:
        adjusted_min = 0
        global_max = 0

    # TODO: move reddit's csv building to reddit_utils
    print ("collecting reddit sentiment for " + TOPIC + ":")
    for date in tqdm(range(resume_date, END_DATE, 86400)):

        posts = get_submissions(SEARCH_TERMS, date)
        score = 0
        daily_max = 0
        daily_min = 0

        for post in posts:
            # get all comments of post in tree format
            node_list = make_submission_tree(post,4)

            # ensure tree is not empty
            if not node_list == None:
                tree_score = analyze_tree(node_list)

                # check if current score is highest for the day
                if tree_score > daily_max:
                    daily_max = tree_score
                    if tree_score > global_max:
                        global_max = tree_score

                #check if current score is lowest for the day
                if tree_score < daily_min:
                    daily_min = tree_score
                    if tree_score < global_min:
                        global_min = tree_score

                # add score of submission to score of day
                score += tree_score

                # delete the tree to save memory
                delete_submission_tree(node_list)

            # if a spike is detected, store the link in reddit.events
                if (tree_score > adjusted_max/5) or (tree_score < adjusted_min):
                    log_event(date, post, tree_score, TOPIC)
                
        # slide window to the right
        window = window[1:] + [daily_max]

        # find max and adjusted max
        window_max = max(window)
        adjusted_max = (window_max + 6*adjusted_max + global_max)/10
        # write to file in case of failure
        f = open(AMAX_TEMP, "w+")
        f.write(str(adjusted_max) + "\n" + str(global_max))
        f.close()

        # find min and adjusted min
        window_min = min(window)
        adjusted_min = (window_min + 6*adjusted_min + global_min)/10
        # write to file in case of failure
        f = open(AMIN_TEMP, "w+")
        f.write(str(adjusted_min) + "\n" + str(global_min))
        f.close()

        # write score to file
        append_to_file(date, score, FILENAME)

    os.remove(AMAX_TEMP)
    os.remove(AMIN_TEMP)
    plot_data(TOPIC)

