import uuid
import time
from typing import List, Optional, Any
from typing_extensions import Annotated
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from sqlalchemy_continuum import make_versioned

from sqlalchemy import ForeignKey, DateTime, JSON, create_engine, select, delete
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column, Mapped, MappedAsDataclass, sessionmaker, scoped_session, validates, configure_mappers

db_path = Path.home() / ".movx" / "movx.db"

#db_path.unlink()

db_url = 'sqlite:///%s' % db_path.absolute()

make_versioned(user_cls=None)

# Create the database engine and session
engine = create_engine(db_url)

session_factory = sessionmaker(bind=engine, expire_on_commit=False)

Session = scoped_session(session_factory)

session = Session()

class Base(MappedAsDataclass, DeclarativeBase):   
    '''
    Base Class for DB Declarative Model

    Contain some useful function to make working with Model Object easier
    ''' 
    __allow_unmapped__ = False

    def add(self):
        with session:
            session.add(self)
            session.commit()

    def delete(self):
        with session:
            session.execute( delete(self.__class__).where(self.__class__.id == self.id))
            session.commit()
        
    def get(self):
        return Session.get(self.__class__, self.id)

    def update(self, **args):
        with session:
            session.execute( self.__table__.update().where(self.__class__.id == self.id).values( args ) )
            session.commit()

    @classmethod
    def get(cls, id):
        return Session.get(cls, id)

    @classmethod
    def get_all(cls):
        return Session.scalars( select(cls) ).all()

    @classmethod
    def clear_all(cls):
        with session:
            session.query(cls).delete()
            session.commit()

    @contextmanager
    def fresh(self):
        with session:
            t = session.query(self.__class__).get(self.id)
            yield t
            session.commit()

class Status(Base):
    __tablename__ = 'status'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("status.id"), init=False, nullable=True)
    name: Mapped[str] = mapped_column(unique=True)
    color: Mapped[str] = mapped_column(unique=True)
    type: Mapped[Optional[str]] = mapped_column(default="")
    nexts: Mapped[List["Status"]] = relationship( default_factory=list )

class Location(Base):
    __tablename__ = 'location'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    path: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    last_scan: Mapped[float] =  mapped_column(insert_default=time.time(), default=time.time())
    netshare: Mapped[Optional[str]] = mapped_column(default="")
    type: Mapped[Optional[str]] = mapped_column(default="")

    dcps: Mapped[List["DCP"]] = relationship(
        back_populates="location", default_factory=list
    )

    @validates("path")
    def validate_path(self, key, path):
        if not Path(path).exists():
            raise ValueError("Path %s do not exist" % Path(path).absolute())
        return path

class Movie(Base):
    __tablename__ = 'movie'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    dcps: Mapped[List["DCP"]] = relationship(
        back_populates="movie", default_factory=list
    )

    status_id: Mapped[int] = mapped_column(ForeignKey(Status.id), init=False, nullable=True)
    status: Mapped[Optional["Status"]] = relationship(default=None)

class DCP(Base):
    __tablename__ = 'dcp'
    __versioned__ = {}
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    uid: Mapped[uuid.UUID] = mapped_column(init=False, unique=True)

    location_id: Mapped[int] = mapped_column(ForeignKey(Location.id), init=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey(Movie.id), init=False, nullable=True)
    status_id: Mapped[int] = mapped_column(ForeignKey(Status.id), init=False, nullable=True)

    path: Mapped[str] = mapped_column(unique=True)

    location: Mapped["Location"] = relationship()

    movie: Mapped[Optional["Movie"]] = relationship(default=None)
    status: Mapped[Optional["Status"]] = relationship(default=None)

    title: Mapped[str] = mapped_column(default="")
    package_type: Mapped[Optional[str]] = mapped_column(default="")
    kind: Mapped[Optional[str]] = mapped_column(default="")
    size: Mapped[Optional[int]] = mapped_column(default=0)
    owner: Mapped[Optional[str]] = mapped_column(default="")

    tasks: Mapped[List["Task"]] = relationship(
       back_populates="dcp", default_factory=list
    )

    @validates("path")
    def validate_path(self, key, path):
        if not Path(path).exists():
            raise ValueError("Path %s do not exist" % Path(path).absolute())
        return path
    
    def __post_init__(self):
        self.uid = uuid.uuid5(uuid.NAMESPACE_X500, str(self.path))

class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    dcp_id: Mapped[int] = mapped_column(ForeignKey(DCP.id), init=False, nullable=True)
    dcp: Mapped["DCP"] = relationship(DCP)

    name: Mapped[str]
    status: Mapped[str]
    type: Mapped[str]

    description: Mapped[Optional[str]] = mapped_column(default="")
    progress: Mapped[Optional[int]] = mapped_column(insert_default=-1, default=-1)
    author: Mapped[Optional[str]] = mapped_column(insert_default="", default="")
    elapsed_time_s: Mapped[Optional[int]] = mapped_column(insert_default=0, default=0)
    created_at: Mapped[Optional[float]] = mapped_column(insert_default=time.time(), default=time.time())
    last_update: Mapped[Optional[float]] = mapped_column(insert_default=time.time(), default=time.time())
    timestamp: Mapped[Optional[float]] = mapped_column(insert_default=time.time(), default=time.time())
    eta: Mapped[Optional[int]] = mapped_column(insert_default=-1, default=-1)
    result = mapped_column(JSON, insert_default={}, default={})

    def start(self):
        self.update(
            progress=0,
            status="started",
            timestamp = time.time(),
            created_at = time.time()
        )

    def done(self, status="done", result = None):
        self.update(
            progress = 1,
            status = status,
            result = result or { "no result" },
            eta = 0,
            elapsed_time_s = time.time() - self.timestamp,
        )

    def update_progress(self, progress, t):
        with fresh(self) as task:
            prog = round(progress, 2)
            task.status = "ready"
            task.eta = -1
            if prog >=1 :
                task.status = "done"
                task.eta = 0
            elif prog > 0:
                task.status = "inprogress"
                if prog >= 3:
                    task.eta = (1-prog) / ((prog) / t) + 1
            task.progress = prog

configure_mappers()

Base.metadata.create_all(engine)


def clear(cls):
    with session:
        session.query(cls).delete()
        session.commit()


'''
# Create a Location object
location = Location(path='/path/to/locsdati4sad2')

# Create a DCP object with the Location
dcp = DCP(location=location)

# Create several CheckAction objects and add them to the DCP
action1 = CheckTask(name='Check 1', timestamp=datetime.now())
action2 = CheckTask(name='Check 2', timestamp=datetime.now())
action3 = CheckTask(name='Check 3', timestamp=datetime.now())

dcp.tasks.append(action1)
dcp.tasks.append(action2)
dcp.tasks.append(action3)

with session:
    # Add the objects to the session and commit the changes
    session.add(dcp)
    session.commit()


# Retrieve the first DCP object from the database
dcp = session.query(DCP).first()

# Print the DCP's ID and the location's path
print(f'DCP ID: {dcp.id}')
print(f'Location: {dcp.location.path}')

# Print the details of each CheckAction in the DCP
for action in dcp.actions:
    if isinstance(action, CheckAction):
        print(f'Action ID: {action.id}')
        print(f'Name: {action.name}')
        print(f'Timestamp: {action.timestamp}')
        print(f'Limit: {action.limit}')
        print('---')

'''

def get_movies():
    return Session.scalars( select(Movie) ).all()
