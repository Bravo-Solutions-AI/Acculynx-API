from enum import Enum

class DateFilterType(str, Enum):
    """Filter types for job date filtering."""
    CREATED_DATE = "CreatedDate"
    MODIFIED_DATE = "ModifiedDate"
    MILESTONE_DATE = "MilestoneDate"


class SortOrder(str, Enum):
    """Sort order options."""
    ASCENDING = "Ascending"
    DESCENDING = "Descending" 