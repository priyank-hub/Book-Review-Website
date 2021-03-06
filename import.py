import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isb, tit, auth, ye in reader:
        db.execute("INSERT INTO books VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isb, "title": tit, "author": auth, "year": ye})
    db.commit()


if __name__ == "__main__":
    main()

