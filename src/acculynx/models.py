from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class State(BaseModel):
    id: int
    name: str
    abbreviation: str
    _link: str


class Country(BaseModel):
    id: int
    name: str
    abbreviation: str
    _link: str


class GeoLocation(BaseModel):
    latitude: float
    longitude: float


class TradeType(BaseModel):
    id: str
    name: str


class JobCategory(BaseModel):
    id: int
    category_id: int = Field(alias="categoryId")
    name: str


class WorkType(BaseModel):
    id: int
    name: str
    system_default: bool = Field(alias="systemDefault")
    _link: str


class LeadSource(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = Field(None, alias="parentId")
    _link: str


class Address(BaseModel):
    street1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[State] = None
    zip_code: Optional[str] = Field(None, alias="zipCode")
    country: Optional[Country] = None


class Contact(BaseModel):
    id: str
    _link: str


class JobContact(BaseModel):
    id: str
    contact: Contact
    is_primary: bool = Field(alias="isPrimary")
    relation_to_primary: str = Field(alias="relationToPrimary")
    _link: str


class Job(BaseModel):
    id: str
    contacts: List[JobContact]
    location_address: Optional[Address] = Field(None, alias="locationAddress")
    geo_location: Optional[GeoLocation] = Field(None, alias="geoLocation")
    trade_types: List[TradeType] = Field(default_factory=list, alias="tradeTypes")
    job_category: Optional[JobCategory] = Field(None, alias="jobCategory")
    work_type: Optional[WorkType] = Field(None, alias="workType")
    lead_source: Optional[LeadSource] = Field(None, alias="leadSource")
    lead_dead_reason: Optional[str] = Field("", alias="leadDeadReason")
    current_milestone: Optional[str] = Field(None, alias="currentMilestone")
    milestone_date: Optional[datetime] = Field(None, alias="milestoneDate")
    created_date: Optional[datetime] = Field(None, alias="createdDate")
    modified_date: Optional[datetime] = Field(None, alias="modifiedDate")
    job_name: Optional[str] = Field(None, alias="jobName")
    job_number: Optional[str] = Field(None, alias="jobNumber")
    priority: Optional[str] = None
    _link: str

    @property
    def customer(self) -> Optional[Contact]:
        """Get the primary contact."""
        primary_contacts = [jc.contact for jc in self.contacts if jc.is_primary]
        return primary_contacts[0] if primary_contacts else None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class Customer(BaseModel):
    id: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class Lead(BaseModel):
    id: str
    status: str
    source: str
    customer: Customer
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    notes: Optional[str] = None


class Payment(BaseModel):
    amount: float
    payment_date: datetime = Field(alias="paymentDate")
    payment_type: str = Field(alias="paymentType")
    check_number: Optional[str] = Field(None, alias="checkNumber")
    notes: Optional[str] = None

    class Config:
        allow_population_by_field_name = True 


class JobMessage(BaseModel):
    message: str

    class Config:
        allow_population_by_field_name = True 


class User(BaseModel):
    """Model for a user who created a lead history entry."""
    id: str
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    email: Optional[str] = None
    _link: str


class LeadHistory(BaseModel):
    """Model for a lead history entry."""
    id: str
    action: str
    created_date: datetime = Field(alias="createdDate")
    created_by: Optional[User] = Field(None, alias="createdBy")
    _link: str

    class Config:
        allow_population_by_field_name = True 


class CreateLeadRequest(BaseModel):
    """Model for creating a new lead."""
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    sales_rep_id: Optional[str] = Field(None, alias="salesRepId")
    trade_type_ids: Optional[List[str]] = Field(None, alias="tradeTypeIds")
    job_category_id: Optional[int] = Field(None, alias="jobCategoryId")
    work_type_id: Optional[int] = Field(None, alias="workTypeId")
    lead_source_id: Optional[str] = Field(None, alias="leadSourceId")
    milestone: Optional[str] = None
    milestone_date: Optional[datetime] = Field(None, alias="milestoneDate")
    priority: Optional[str] = None

    class Config:
        populate_by_name = True 