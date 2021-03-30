from pytrends.request import TrendReq
import csv

pytrend = TrendReq()

def get_trends_data(topic, searchterm, selection):
    selection_id = select_suggestion(searchterm, selection)
    pytrend.build_payload(kw_list=[selection_id])

    df = pytrend.interest_over_time()
    timestamps = df.index.values.astype(int) // 10 ** 9
    interest = getattr(df,selection_id).values
    with open('data/' + topic + '/gtrends.data', 'w+') as f:
        writer = csv.writer(f)
        writer.writerows(zip(timestamps, interest))


def select_suggestion(searchterm, selection):
    suggestions = pytrend.suggestions(searchterm)
    for suggestion in suggestions:
        if suggestion['type'] == selection:
            return suggestion['mid']

if __name__ == "__main__":
    mid = select_suggestion('Andrew Yang', 'American entrepreneur')
    get_trends_data('yang','Andrew Yang', 'American entrepreneur')