from datetime import date, datetime
from typing import List, Optional, Dict, Any, AsyncIterator, BinaryIO
from ..models import Job
from ..enums import DateFilterType, SortOrder, DocumentFolderID
import os
import mimetypes
from ..exceptions import AccuLynxAPIError


class JobsMixin:
    """Mixin for job-related API endpoints."""
    
    async def get_jobs(
        self,
        *,
        page_size: int = 25,
        page_start_index: int = 0,
        includes: Optional[List[str]] = None,
        filter_by_date: Optional[DateFilterType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        milestones: Optional[List[str]] = None,
        sort_by: Optional[DateFilterType] = None,
        sort_order: Optional[SortOrder] = None,
        query: Optional[str] = None,
    ) -> List[Job]:
        """Retrieve a list of jobs with filtering and sorting options."""
        params = {
            "pageSize": page_size,
            "pageStartIndex": page_start_index,
        }

        if includes:
            params["includes"] = ",".join(includes)
        if filter_by_date:
            params["filterByDate"] = filter_by_date.value
        if start_date:
            params["startDate"] = start_date.isoformat()
        if end_date:
            params["endDate"] = end_date.isoformat()
        if milestones:
            params["milestones"] = ",".join(milestones)
        if sort_by:
            params["sortBy"] = sort_by.value
        if sort_order:
            params["sortOrder"] = sort_order.value
        if query:
            params["query"] = query


        data = await self._get("/jobs", params=params)
        try:
            jobs = [Job.parse_obj(job) for job in data.get("items", [])]
            print(f"Successfully parsed {len(jobs)} jobs")
            return jobs
        except Exception as e:
            print(f"Error parsing jobs: {e}")
            raise

    async def get_jobs_iterator(
        self,
        *,
        page_size: int = 25,
        includes: Optional[List[str]] = None,
        filter_by_date: Optional[DateFilterType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        milestones: Optional[List[str]] = None,
        sort_by: Optional[DateFilterType] = None,
        sort_order: Optional[SortOrder] = None,
    ) -> AsyncIterator[Job]:
        """Iterate through all jobs using pagination."""
        page_start_index = 0
        
        while True:
            try:
                jobs = await self.get_jobs(
                    page_size=page_size,
                    page_start_index=page_start_index,
                    includes=includes,
                    filter_by_date=filter_by_date,
                    start_date=start_date,
                    end_date=end_date,
                    milestones=milestones,
                    sort_by=sort_by,
                    sort_order=sort_order,
                )
                
                if not jobs:
                    break
                    
                for job in jobs:
                    yield job
                
                if len(jobs) < page_size:  # We've reached the last page
                    break
                    
                page_start_index += len(jobs)
                
            except AccuLynxAPIError as e:
                if e.status_code == 416:  # RequestedRangeNotSatisfiable
                    break  # We've reached the end of the available records
                raise  # Re-raise other API errors

    async def get_job(
        self,
        job_id: str,
        includes: Optional[List[str]] = None,
    ) -> Job:
        """Retrieve a specific job by ID."""
        params = {}
        if includes:
            params["includes"] = ",".join(includes)
            
        data = await self._get(f"/jobs/{job_id}", params=params)
        return Job.parse_obj(data)

    async def create_job_message(
        self,
        job_id: str,
        *,
        message: str,
    ) -> Dict:
        """Create a new message (comment) for a job."""
        payload = {
            "message": message,
        }

        response = await self._client.post(
            f"/jobs/{job_id}/messages",
            json=payload
        )
        
        if response.status_code >= 400:
            self._handle_error(response)
        return response.json()

    async def create_payment_received(
        self,
        job_id: str,
        *,
        amount: float,
        payment_date: date,
        payment_type: str,
        check_number: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict:
        """Create a new payment received for a job."""
        payload = {
            "amount": amount,
            "paymentDate": payment_date.isoformat(),
            "paymentType": payment_type,
        }

        if check_number:
            payload["checkNumber"] = check_number
        if notes:
            payload["notes"] = notes

        response = await self._client.post(
            f"/jobs/{job_id}/payments/received",
            json=payload
        )
        
        if response.status_code >= 400:
            self._handle_error(response)
        return response.json()

    async def create_payment_paid(
        self,
        job_id: str,
        *,
        to: str,
        amount: float,
        payment_date: datetime,
        account_type_id: str,
        is_paid: bool = True,
        ref_number: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict:
        """Create a new payment paid for a job.
        
        Args:
            job_id: The job's unique identifier
            to: Payment paid to
            amount: Amount of payment paid
            payment_date: Payment datetime (UTC)
            account_type_id: Id of account type
            is_paid: Is Paid? (defaults to True)
            ref_number: Optional reference number
            notes: Optional note for the payment
        """
        payload = {
            "to": to,
            "amount": amount,
            "paymentDate": payment_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "accountTypeId": account_type_id,
            "isPaid": is_paid
        }

        if ref_number:
            payload["refNumber"] = ref_number
        if notes:
            payload["notes"] = notes

        response = await self._client.post(
            f"/jobs/{job_id}/payments/paid",
            json=payload
        )
        
        if response.status_code >= 400:
            self._handle_error(response)
        return response.json()

    async def upload_document(
        self,
        job_id: str,
        *,
        file: BinaryIO,
        filename: Optional[str] = None,
        folder_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict:
        """Upload a document to a job.
        
        Args:
            job_id: The ID of the job to upload to
            file: File-like object containing the document
            filename: Optional custom filename (if not provided, will use file.name)
            folder_id: Optional folder ID to place the document in
            description: Optional description of the document
            
        Returns:
            Dict containing the upload response
        """
        # Get filename from file object if not provided
        if not filename and hasattr(file, 'name'):
            filename = os.path.basename(file.name)
        elif not filename:
            raise ValueError("filename must be provided if file object has no name")

        # Determine content type
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = 'application/octet-stream'

        # Prepare the multipart form data
        files = {
            'file': (filename, file, content_type)
        }
        
        # Prepare additional form data
        data = {}
        if folder_id:
            data['folderId'] = folder_id
        if description:
            data['description'] = description

        response = await self._client.post(
            f"/jobs/{job_id}/documents",
            files=files,
            data=data,
            headers={
                "Accept": "application/json"
            }
        )
        
        if response.status_code >= 400:
            self._handle_error(response)
        return response.json()

    async def upload_photo_or_video(
        self,
        job_id: str,
        *,
        file: BinaryIO,
        filename: Optional[str] = None,
        tag_ids: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> Dict:
        """Upload a photo or video to a job.
        
        Args:
            job_id: The ID of the job to upload to
            file: File-like object containing the photo or video
            filename: Optional custom filename (if not provided, will use file.name)
            tag_ids: Optional list of tag IDs to apply to the upload
            description: Optional description of the photo/video
            
        Returns:
            Dict containing the upload response
        """
        # Get filename from file object if not provided
        if not filename and hasattr(file, 'name'):
            filename = os.path.basename(file.name)
        elif not filename:
            raise ValueError("filename must be provided if file object has no name")

        # Determine content type
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = 'application/octet-stream'

        # Prepare the multipart form data
        files = {
            'file': (filename, file, content_type)
        }
        
        # Prepare additional form data
        data = {}
        if tag_ids:
            data['tagIds'] = ','.join(tag_ids)
        if description:
            data['description'] = description

        response = await self._client.post(
            f"/jobs/{job_id}/photos-videos",
            files=files,
            data=data,
            headers={
                "Accept": "application/json"
            }
        )
        
        if response.status_code >= 400:
            self._handle_error(response)
        return response.json()

    async def search_jobs(
        self,
        *,
        search_term: Optional[str] = None,
        geo_location: Optional[Dict[str, Any]] = None,
        page_size: int = 25,
        page_start_index: int = 0,
        includes: Optional[List[str]] = None,
    ) -> List[Job]:
        """Search for jobs based on search terms and/or geographic location."""
        if not search_term and not geo_location:
            raise ValueError("At least one of search_term or geo_location must be provided")

        params = {
            "pageSize": min(page_size, 25),  # API limit
            "pageStartIndex": min(page_start_index, 100000),  # API limit
        }

        if includes:
            params["includes"] = ",".join(includes)

        payload = {}
        if search_term:
            payload["searchTerm"] = search_term
        if geo_location:
            payload["geoLocation"] = geo_location


        response = await self._client.post("/jobs/search", params=params, json=payload)
        
        if response.status_code >= 400:
            self._handle_error(response)
            
        data = response.json()
        try:
            jobs = [Job.parse_obj(job) for job in data.get("items", [])]
            print(f"Successfully parsed {len(jobs)} jobs from search")
            return jobs
        except Exception as e:
            print(f"Error parsing jobs from search: {e}")
            raise

    async def add_job_document(
        self,
        job_id: str,
        *,
        file_path: str,
        document_folder_id: DocumentFolderID = DocumentFolderID.INVOICES,
        description: Optional[str] = None
    ) -> Dict:
        """Upload a document to a job.
        
        Args:
            job_id: The ID of the job
            file_path: Path to the file to upload
            document_folder_id: Folder ID to store the document in (default: Invoices)
            description: Optional description of the document
        """
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, 'application/octet-stream')
            }
            data = {
                'documentFolderId': document_folder_id.value
            }
            if description:
                data['description'] = description

            response = await self._client.post(
                f"/jobs/{job_id}/documents",
                data=data,
                files=files
            )
            
            if response.status_code >= 400:
                self._handle_error(response)
            return response.json()