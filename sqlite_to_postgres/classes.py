from dataclasses import dataclass, field
import uuid
from datetime import datetime
from typing import Union

@dataclass
class UUIDMIXIN:
    id: uuid

@dataclass
class TimeMixin:
    created_at: datetime
    updated_at: datetime

@dataclass
class FilmWork(UUIDMIXIN, TimeMixin):
    title: str
    description: str
    creation_date: datetime
    file_path: str
    rating: Union[int, float]
    type: str

@dataclass
class Genre(UUIDMIXIN, TimeMixin):
    name: str
    description: str

@dataclass
class GenreFilmWork(UUIDMIXIN):
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Person(UUIDMIXIN, TimeMixin):
    full_name: str

@dataclass
class PersonFilmWork(UUIDMIXIN):
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime = field(default_factory=datetime.utcnow)
