import csv

from app import db, insert_question


# Getting and inserting all the questions from the csv file to the database
def upload_questions_from_csv():
    with open('avatar_questions.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for line in csv_reader:
            answers = line['answers'].split(',')
            print(line['questions'])
            insert_question(line['questions'], line['score'], line['pic'], *answers)


# Reset the database with the questions from the csv file.
def reset_db():
    db.drop_all()
    db.create_all()
    upload_questions_from_csv()
