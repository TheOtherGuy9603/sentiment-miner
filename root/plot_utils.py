import matplotlib.pyplot as plt 
import datetime as dt
import csv

sources = ['reddit', 'gtrends']

def plot_data(topic):

    for source in sources:
        
        x = []
        y = []

        file = 'data/' + topic + '/' + source + '.data'
        with open(file, 'r') as csvfile:
            plots = csv.reader(csvfile, delimiter=',')
            for row in plots:
                x.append(dt.datetime.fromtimestamp(int(row[0])))
                y.append(float(row[1]))

        if source == 'gtrends':
            # scales it since gtrends is from 0-100
            y = [val*5 for val in y]

        # if source == 'reddit':
        #     # distributes upvotes over a period of 7 days (usually how long a post is active)
        #     templist = y.copy()
        #     y = [val * 0 for val in y]
        #     for day in reversed(range(8)):
        #         templist.pop()
        #         templist = [0] + templist
        #         y = [(yval + tempval*day/28) for (yval, tempval) in zip(y,templist)]

        plt.plot(x,y, label=source)

    plt.xlabel('time')
    plt.ylabel('sentiment')
    plt.title("Sentiment of " + topic + " over time")
    plt.legend()
    plt.show()



if __name__ == "__main__":
    topic = 'tulsi'
    plot_data(topic)