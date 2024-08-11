from datetime import datetime
from typing import Optional
from dataclasses import dataclass

@dataclass
class Visitor:
    id: int
    email: str
    is_admin: bool
    updated_at: Optional[datetime] = None
