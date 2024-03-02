import os
from typing import Union, List


def getenv(
    param: str, default: str = "", separator: str = ","
) -> Union[str, List[str]]:
    value = os.getenv(param, default)
    return value.split(separator) if separator in value else value
