from datetime import datetime
from typing import List, Optional, Dict, Union
from ..models import LeadHistory, Lead, CreateLeadRequest

class LeadsMixin:
    """Mixin for lead-related API endpoints."""
    
    async def create_lead(
        self,
        *,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[Dict] = None,
        source: Optional[str] = None,
        notes: Optional[str] = None,
        status: Optional[str] = None,
        sales_rep_id: Optional[str] = None,
        trade_type_ids: Optional[List[str]] = None,
        job_category_id: Optional[int] = None,
        work_type_id: Optional[int] = None,
        lead_source_id: Optional[str] = None,
        milestone: Optional[str] = None,
        milestone_date: Optional[Union[datetime, str]] = None,
        priority: Optional[str] = None,
    ) -> Lead:
        """Create a new lead.
        
        Note: This endpoint uses API v1, unlike other endpoints which use v2.
        
        Args:
            first_name: Lead's first name
            last_name: Lead's last name
            email: Optional email address
            phone: Optional phone number
            address: Optional address dictionary
            source: Optional lead source name
            notes: Optional notes about the lead
            status: Optional lead status
            sales_rep_id: Optional ID of the sales representative
            trade_type_ids: Optional list of trade type IDs
            job_category_id: Optional job category ID
            work_type_id: Optional work type ID
            lead_source_id: Optional lead source ID
            milestone: Optional milestone name
            milestone_date: Optional milestone date
            priority: Optional priority level
        
        Returns:
            Lead object containing the created lead information
        """
        # Create request model
        request = CreateLeadRequest(
            firstName=first_name,
            lastName=last_name,
            email=email,
            phone=phone,
            address=address,
            source=source,
            notes=notes,
            status=status,
            salesRepId=sales_rep_id,
            tradeTypeIds=trade_type_ids,
            jobCategoryId=job_category_id,
            workTypeId=work_type_id,
            leadSourceId=lead_source_id,
            milestone=milestone,
            milestoneDate=milestone_date,
            priority=priority,
        )

        # Construct the v1 endpoint URL
        v1_base_url = self.base_url.replace('/api/v2', '/api/v1')
        
        response = await self._client.post(
            f"{v1_base_url}/leads",
            json=request.dict(by_alias=True, exclude_none=True)
        )
        
        if response.status_code >= 400:
            self._handle_error(response)
            
        return Lead.parse_obj(response.json())

    async def get_lead_history(
        self,
        lead_id: str,
        *,
        includes: Optional[List[str]] = None
    ) -> List[LeadHistory]:
        """Get the history of actions performed for a lead."""
        params = {}
        if includes:
            params["includes"] = ",".join(includes)
            
        data = await self._get(f"/leads/{lead_id}/history", params=params)
        return [LeadHistory.parse_obj(item) for item in data]