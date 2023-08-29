from sqlalchemy import select
from movx.core.db import Status, session, Session


def get_all():
    return Session.scalars(select(Status)).all()


def get(id):
    return Session.get(Status, id)


def add(name, color):
    status = Status(name, color)

    with session:
        session.add(status)
        session.commit()

    return status


def add_defaults():
    s_done = Status("done", "#81ff83")
    s_check = Status("check", "#81b1ff")
    s_todo = Status("todo", "#ffd447")
    s_block = Status("blocked", "#ff8181")

    with session:
        session.add(s_done)
        session.add(s_check)
        session.add(s_todo)
        session.add(s_block)
        session.commit()
