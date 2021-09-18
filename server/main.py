#!/usr/bin/python

import psycopg2
from fastapi import FastAPI
import random
import configparser
import json
from json.decoder import JSONDecodeError
from typing import List

config = configparser.RawConfigParser()
config.read("config.ini")
db_url = config["Server"].get("DatabaseUrl")

conn = psycopg2.connect(dsn=db_url)
app = FastAPI()

DB_COLUMNS = [
    ("id", str),
    ("name", str),
    ("imglink", str),
    ("prep_time", int),
    ("yield", int),
    ("description", str),
    ("ingredients", lambda i: json.loads(i)),
    ("steps", lambda i: json.loads(i)),
    ("source", str),
    ("vegan", bool),
    ("vegetarian", bool),
    ("halal", bool),
    ("treenut_free", bool),
    ("peanut_free", bool)
]


class Recipe:
    __slots__ = [i[0] for i in DB_COLUMNS]

    def __init__(self, *args):
        # it is assumed that there isn't going to be blank fields
        # they are at least populated with None

        for name, value in zip(DB_COLUMNS, args):
            try:
                self.__setattr__(name[0], name[1](value))
            except (TypeError, JSONDecodeError):
                # likely a conversion error from None
                self.__setattr__(name[0], None)

    def to_json(self):
        return {i: getattr(self, i) for i in self.__slots__}

    def __repr__(self):
        return str(self.to_json())


@app.get("/recipes/")
def root(
    limit: int = 14,
    vegan: bool = False,
    vegetarian: bool = False,
    halal: bool = False,
    no_tree_nuts: bool = False,
    no_peanuts: bool = False,
):
    # return random w/query parameters
    # TODO: put this all in a try-catch-finally to close cursor and connection
    cur = conn.cursor()
    select = f"SELECT * FROM RECIPE;"
    cur.execute(select)
    rows = cur.fetchall()
    return list(map(lambda i: Recipe(*i), rows))


@app.get("/recipes/{item_id}")
def recipe_by_id(item_id: str):
    # TODO: put this all in a try-catch-finally to close cursor and connection
    cur = conn.cursor()
    select = f"SELECT * FROM RECIPE WHERE id={item_id};"
    cur.execute(select)
    rows = cur.fetchall()
    cur.close()


if __name__ == "__main__":
    print(root())