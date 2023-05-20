from typing import Union
from pydantic import BaseModel


class Wav(BaseModel):
    wav_name: str
    wav_text: str

class Item(BaseModel):
    text: str