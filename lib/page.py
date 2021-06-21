import dataclasses
import datetime
from dataclasses import dataclass
from typing import List


@dataclass()
class Page:
    title: str = ''
    content: str = ''
    file_path: str = ''
    rendered: str = ''
    teaser: str = ''
    tags: str = ''
    url: str = '/'
    other_files: List[str] = dataclasses.field(default_factory=list)
    date: datetime.datetime = datetime.datetime.now()
    last_update_time: datetime.datetime = datetime.datetime.now()