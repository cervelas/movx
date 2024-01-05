from sqlalchemy import select
from movx.core.db import Tags, Session, Session


def add_defaults():
    """
    Add some default status
    """
    t_done = Tags("done", "#81ff83")
    t_check = Tags("check", "#81b1ff")
    t_todo = Tags("todo", "#ffd447")
    t_block = Tags("blocked", "#ff8181")

    with Session() as session:
        session.add(t_done)
        session.add(t_check)
        session.add(t_todo)
        session.add(t_block)
        session.commit()
