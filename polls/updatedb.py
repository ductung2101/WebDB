import requests
import pandas as pd

from polls.models import Poll, Media
from polls.util import convertDateField, convertingdatetimefield

# auto update poll using requests
def auto_update_president_polls():
    url = 'https://projects.fivethirtyeight.com/polls-page/president_primary_polls.csv'
    r = requests.get(url, allow_redirects=True)
    open('polls\\new_file.csv', 'wb').write(r.content)
    temp = pd.read_csv('polls\\new_file.csv', sep=',', quotechar='"')
    with open('polls\\new_file.csv', 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        header = next(reader)
        total_row_new_record = sum(1 for line in csv_file)
        print(total_row_new_record)
        total_new_records_count = total_row_new_record - Poll.objects.count()
        print(total_new_records_count)
        csv_file.seek(0)
        header = next(reader)
        subsequent_no_new_poll = 0
        for row in reader:
            current_poll_id = row[1]
            current_candidate_id = row[30]
            # print(current_poll_id)
            if Poll.objects.filter(poll_id=current_poll_id, candidate_id=current_candidate_id).count() == 0:
                subsequent_no_new_poll = 0
                _, created = Poll.objects.get_or_create(
                    question_id=row[0],
                    poll_id=row[1],
                    cycle=row[2],
                    state=row[3],
                    pollster_id=row[4],
                    pollster=row[5],
                    sponsor_ids=row[6],
                    sponsors=row[7],
                    display_name=row[8],
                    pollster_rating_id=row[9],
                    pollster_rating_name=row[10],
                    fte_grade=row[11],
                    sample_size=row[12],
                    population=row[13],
                    population_full=row[14],
                    methodology=row[15],
                    office_type=row[16],
                    start_date=convertDateField(row[17]),
                    end_date=convertDateField(row[18]),
                    sponsor_candidate=row[19],
                    internal=row[20],
                    partisan=row[21],
                    tracking=row[22],
                    nationwide_batch=row[23],
                    created_at=convertingdatetimefield(row[24]),
                    notes=row[25],
                    url=row[26],
                    stage=row[27],
                    party=row[28],
                    answer=row[29],
                    candidate_id=row[30],
                    candidate_name=row[31],
                    pct=row[32]
                )
                if type(created) != bool:
                    created.save()
            else:
                subsequent_no_new_poll += 1
            if subsequent_no_new_poll == 200:
                break
    # problem: date is sorted decreasingly, if new records are written, they are added to the end
    # -> need to sort whole DB due to start_date -> not optimal, use poll_id instead.
    # compare current file with existing model data
        #pdb.set_trace()
    return False

