"""
create citybikes schema
"""

from typing import Any

from yoyo import step

__depends__: Any = {}

steps = [step("CREATE SCHEMA citybikes", "DROP SCHEMA citybikes")]
