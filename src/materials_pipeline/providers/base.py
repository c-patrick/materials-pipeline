from abc import ABC, abstractclassmethod
from collections.abc import Mapping
from typing import Any

from materials_pipeline.models import MaterialRecord

RawRecord = Mapping[str, Any]


class MaterialProvider(ABC):
    """Base interface implemented by every materials data provider"""

    @abstractclassmethod
    def transform(self, raw: RawRecord) -> MaterialRecord:
        """Transform one provider-native record into a common material record"""
        raise NotImplementedError
