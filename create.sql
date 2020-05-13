CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    password VARCHAR NOT NULL
);

CREATE TABLE books (
    isbn varchar PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE reviews (
    id VARCHAR,
    isbn VARCHAR NOT NULL,
    rating INTEGER,
    review VARCHAR,
    PRIMARY KEY(id, isbn),
    FOREIGN KEY (id) REFERENCES users(id),
    FOREIGN KEY (isbn) REFERENCES books(isbn)
);