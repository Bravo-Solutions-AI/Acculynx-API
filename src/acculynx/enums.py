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


class DocumentFolderID(str, Enum):
    INVOICES = "956ba254-3570-49c6-ab5e-cdba50b92743"
    # Add other folder IDs as needed 