"""Shared enum base for menu-selectable, human-labeled choices.

Several features (Explain's Audience, SQL's Capability, ...) are enums whose
values are display labels chosen by a 1-based menu index. This base centralizes
the label-listing and choice-mapping logic so it is written exactly once.
"""

from enum import Enum
from typing import Self


class LabeledEnum(Enum):
    """An enum whose member values are labels selectable by a 1-based index."""

    @classmethod
    def labels(cls) -> list[str]:
        """Return member labels in definition order, for menu rendering.

        :returns: One human-readable label per member.
        """
        return [member.value for member in cls]

    @classmethod
    def from_choice(cls, choice: int) -> Self:
        """Map a 1-based menu choice to the corresponding member.

        :param choice: A 1-based position matching :meth:`labels`.
        :returns: The member at that position.
        :raises ValueError: If ``choice`` is outside the valid range.
        """
        members = list(cls)
        if not 1 <= choice <= len(members):
            raise ValueError(f"Invalid choice: {choice}")
        return members[choice - 1]
