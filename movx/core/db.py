import uuid
import time
import inspect
import os
import shutil
import enum
from typing import Set, List, Optional
from pathlib import Path
from contextlib import contextmanager
from sqlalchemy_continuum import make_versioned

from sqlalchemy import (
    ForeignKey,
    JSON,
    Enum,
    Table,
    Column,
    create_engine,
    select,
    delete,
)
from sqlalchemy.orm import (
    relationship,
    DeclarativeBase,
    mapped_column,
    Mapped,
    MappedAsDataclass,
    sessionmaker,
    scoped_session,
    validates,
    configure_mappers,
)

db_path = Path.home() / ".movx" / "movx.db"

# db_path.unlink()

db_url = "sqlite:///%s" % db_path.absolute()

engine = None
Session = None
session = None
session_factory = None

make_versioned(user_cls=None)


def del_db_file():
    shutil.copyfile(str(db_path), str(db_path.parent / "backup.backupdb"))
    os.remove(db_path)


class Base(MappedAsDataclass, DeclarativeBase):
    """
    Base Class for DB Declarative Model

    Contain some useful function to make working with Model Object easier, like in Django
    """

    # __allow_unmapped__ = False

    def add(self):
        """
        Add this object to the DB
        """
        with Session() as session:
            session.add(self)
            session.commit()

    def delete(self):
        """
        Delete this object from the DB
        """
        with Session() as session:
            session.execute(delete(self.__class__).where(self.__class__.id == self.id))
            session.commit()

    def update(self, **args):
        """
        update this object values according to the paremeters passed to this function
        """
        with Session() as session:
            session.execute(
                self.__table__.update().where(self.__class__.id == self.id).values(args)
            )
            session.commit()

    @classmethod
    def get(self=None, id=None):
        """
        Hybrid method to get from the DB:

        - Called on an instance, it return a fresh version of this object

        - Called on a Class get all the objects from this object table
        OR get a particular object if the id parameter is provided
        """
        with Session() as session:
            if inspect.isclass(self):
                if id:
                    return session.get(self, id)
                else:
                    return session.scalars(select(self)).all()
            else:
                return session.get(self.__class__, self.id)

    @classmethod
    def get_all(cls):
        """
        get all objects of this same class from the DB
        """
        with Session() as session:
            return session.scalars(
                select(cls), execution_options={"prebuffer_rows": True}
            ).all()

    @classmethod
    def clear(cls):
        """
        Clear this object table (delete all the rows)
        """
        with Session() as session:
            session.query(cls).delete()
            session.commit()

    @classmethod
    def filter(cls, expr):
        """
        Filter query on this object class
        """
        with Session() as session:
            return session.scalars(
                select(cls).filter(expr), execution_options={"prebuffer_rows": True}
            )

    @contextmanager
    def fresh(self):
        """
        Context manager that get a fresh version of this very object, yield, and commit it.
        """
        with Session() as session:
            t = session.query(self.__class__).get(self.id)
            yield t
            session.commit()


class User(Base):
    """
    Represent a user
    """

    __tablename__ = "user"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    avatar: Mapped[Optional[str]] = mapped_column()


class Tags(Base):
    """
    A Generic Tag
    """

    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    color: Mapped[str] = mapped_column(unique=True)


class Status(Base):
    """
    A DCP status
    """

    __tablename__ = "statuses"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    color: Mapped[str] = mapped_column(unique=True)


class LocationType(enum.Enum):
    Local = 1
    NetShare = 2


class Location(Base):
    """
    A Location is a folder where MovX should look for DCP's
    """

    __tablename__ = "location"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    path: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    last_scan: Mapped[float] = mapped_column(
        insert_default=time.time(), default=time.time()
    )
    netshare: Mapped[Optional[str]] = mapped_column(default="")
    type: Mapped[Optional[LocationType]] = mapped_column(default=LocationType.Local)

    # dcps: Mapped[List["DCP"]] = relationship(
    #    back_populates="location", default_factory=list
    # )

    @validates("path")
    def validate_path(self, key, path):
        if not Path(path).exists():
            raise ValueError("Path %s do not exist" % Path(path).absolute())
        return path

    def dcps(self):
        """
        Get all DCP's from this location
        """
        with Session() as session:
            return session.scalars(select(DCP).where(DCP.location == self)).all()


movies_tags = Table(
    "movies_tags",
    Base.metadata,
    Column("movie_id", ForeignKey("movie.id")),
    Column("tag_id", ForeignKey("tags.id")),
)


class Movie(Base):
    """
    A Movie can have one or more DCP's
    """

    __tablename__ = "movie"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    # dcps: Mapped[List["DCP"]] = relationship(
    #    back_populates="movie", default_factory=list
    # )
    # tags_id: Mapped[List[int]] = mapped_column(
    #     init=False, default_factory=list
    # )

    tags: Mapped[List["Tags"]] = relationship(
        init=False, secondary=movies_tags, lazy="selectin"
    )

    def dcps(self):
        """
        Get all the movie's dcp
        """
        with Session() as session:
            return session.scalars(
                select(DCP).where(DCP.movie == self),
                execution_options={"prebuffer_rows": True},
            ).all()

    def ovs(self):
        """
        Get all the OV's related to this movie
        """
        ovs = []
        for dcp in self.dcps():
            if dcp.package_type == "OV":
                ovs.append(dcp)
        return ovs

    def vfs(self):
        """
        Get all the VF's related to this movie
        """
        vfs = []
        for dcp in self.dcps():
            if dcp.package_type == "VF":
                vfs.append(dcp)
        return vfs


dcps_tags = Table(
    "dcps_tags",
    Base.metadata,
    Column("dcp_id", ForeignKey("dcp.id")),
    Column("tag_id", ForeignKey("tags.id")),
)


class DCP(Base):
    """
    Represent a Digitel Cinema Package
    """

    __tablename__ = "dcp"
    __versioned__ = {}
    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    uid: Mapped[uuid.UUID] = mapped_column(init=False, unique=True)

    location_id: Mapped[int] = mapped_column(ForeignKey(Location.id), init=False)
    movie_id: Mapped[int] = mapped_column(
        ForeignKey(Movie.id), init=False, nullable=True
    )
    tags_id: Mapped[int] = mapped_column(ForeignKey(Tags.id), init=False, nullable=True)

    path: Mapped[str] = mapped_column(unique=True)

    location: Mapped["Location"] = relationship(Location, lazy="selectin")

    movie: Mapped[Optional["Movie"]] = relationship(default=None, lazy="selectin")
    tags: Mapped[List["Tags"]] = relationship(
        init=False, secondary=dcps_tags, lazy="selectin"
    )

    title: Mapped[str] = mapped_column(default="")
    package_type: Mapped[Optional[str]] = mapped_column(default="")
    kind: Mapped[Optional[str]] = mapped_column(default="")
    size: Mapped[Optional[int]] = mapped_column(default=0)
    notes: Mapped[Optional[str]] = mapped_column(default="")

    @validates("path")
    def validate_path(self, key, path):
        if not Path(path).exists():
            raise ValueError("Path %s do not exist" % Path(path).absolute())
        return path

    def __post_init__(self):
        self.uid = uuid.uuid5(uuid.NAMESPACE_X500, str(self.path))

    def jobs(self, type=None):
        with Session() as session:
            if type:
                return session.scalars(
                    select(Job)
                    .where(
                        Job.dcp == self,
                        Job.type == type,
                    )
                    .order_by(Job.finished_at.desc()),
                    execution_options={"prebuffer_rows": True},
                ).all()
            else:
                return session.scalars(
                    select(Job).where(Job.dcp == self).order_by(Job.finished_at.desc()),
                    execution_options={"prebuffer_rows": True},
                ).all()


class JobStatus(enum.Enum):
    errored = 0
    created = 1
    started = 2
    running = 3
    finished = 4
    cancelled = 5


class JobType(enum.Enum):
    test = 0
    parse = 1
    probe = 2
    check = 3
    copy = 4


class Job(Base):
    """
    Represent a task that take time and is related to a DCP, and that has been created by someone
    """

    __tablename__ = "job"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    dcp_id: Mapped[int] = mapped_column(ForeignKey(DCP.id), init=False, nullable=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey(User.id), init=False, nullable=True
    )

    dcp: Mapped[DCP] = relationship(DCP, lazy="selectin")
    author: Mapped[User] = relationship(User, lazy="selectin")

    type: Mapped[JobType]
    status: Mapped[JobStatus] = mapped_column(default=JobStatus.created)

    description: Mapped[Optional[str]] = mapped_column(default="")
    progress: Mapped[Optional[int]] = mapped_column(insert_default=-1, default=-1)
    elapsed_time_s: Mapped[Optional[int]] = mapped_column(insert_default=0, default=0)
    created_at: Mapped[Optional[float]] = mapped_column(
        insert_default=time.time(), default=time.time()
    )
    started_at: Mapped[Optional[float]] = mapped_column(insert_default=-1, default=-1)
    finished_at: Mapped[Optional[float]] = mapped_column(insert_default=-1, default=-1)

    result = mapped_column(JSON, insert_default={}, default={})

    def duration(self):
        if self.finished_at > 0:
            return round(self.finished_at - self.started_at)
        else:
            return round(time.time() - self.started_at)

    def eta(self):
        prog = round(self.progress, 2)
        if prog >= 1:
            return 0
        elif prog > 0:
            return (1 - prog) / ((prog) / self.duration()) + 1
        else:
            return -1

    def is_running(self):
        return True if self.status() == "running" else False


configure_mappers()

engine = create_engine(db_url)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Scoped_Session = scoped_session(session_factory)

Base.metadata.create_all(engine)


def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


anonymous = User("anonymous", avatar="anonymous")
# anonymous.add()
