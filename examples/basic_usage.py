import asyncio
import os
from datetime import date, datetime
from acculynx import AccuLynxAPI
from acculynx.client import DateFilterType, SortOrder, AccountType
from acculynx.exceptions import AccuLynxAPIError

async def job_examples():
    """Examples of job-related API operations."""
    api_key = os.getenv("ACCULYNX_API_KEY")
    if not api_key:
        raise ValueError("Please set ACCULYNX_API_KEY environment variable")

    async with AccuLynxAPI(api_key=api_key) as api:
        try:
            # job = await api.get_job(
            #     job_id="b97816ac-06ee-4a31-b628-86ee1b06e092"
            # )
            # print(job)
            
            
            # await api.add_job_document(
            #     job_id='76132e3e-0b1e-4341-869d-034e35d5e4dd',
            #     file_path="examples/test.pdf"
            # )
            
            ## Use datetime object directly instead of converting to ISO string
            today = datetime.now()
            
            await api.create_payment_paid(
                job_id='76132e3e-0b1e-4341-869d-034e35d5e4dd',
                to="ABC",
                amount=175.75,
                payment_date=today,
                account_type_id=AccountType.MATERIALS,
                is_paid=True,
                ref_number="1234567890"
            )   
            
            
            # # Example 1: Get a single page of recent jobs
            # print("\n=== Recent Jobs ===")
            # jobs = await api.get_jobs(
            #     page_size=5,
            #     includes=["contact"],
            #     sort_by=DateFilterType.MODIFIED_DATE,
            #     sort_order=SortOrder.DESCENDING, 
            #     query="BNX-5179"
            # )
            
            # for job in jobs:
            #     print(f"Job: {job.job_number}")
            #     print(f"Status: {job.current_milestone}")
            #     if job.customer:
            #         print(f"Customer ID: {job.customer.id}")
            #     print("---")

            # # Example 2: Get a specific job with more details
            # if jobs:  # Use the first job from previous request
            #     first_job_id = jobs[0].id
            #     print(f"\n=== Detailed Job Info for {first_job_id} ===")
            #     detailed_job = await api.get_job(
            #         first_job_id,
            #         includes=["contact", "initialAppointment"]
            #     )
            #     print(f"Job Number: {detailed_job.job_number}")
            #     if detailed_job.location_address:
            #         print(f"Address: {detailed_job.location_address.street1}, "
            #               f"{detailed_job.location_address.city}, "
            #               f"{detailed_job.location_address.state.abbreviation}")

            # # Example 3: Use the iterator to get all jobs from last month
            # print("\n=== Last Month's Jobs ===")
            # today = date.today()
            # start_date = date(today.year, today.month - 1, 1)
            # end_date = date(today.year, today.month, 1)
            
            # job_count = 0
            # async for job in api.get_jobs_iterator(
            #     page_size=25,
            #     filter_by_date=DateFilterType.CREATED_DATE,
            #     start_date=start_date,
            #     end_date=end_date,
            # ):
            #     job_count += 1
            #     print(f"Found job: {job.job_name} (Created: {job.created_date})")
                
            #     # Limit the number of jobs for this example
            #     if job_count >= 10:
            #         break
            
            # print(f"\nProcessed {job_count} jobs")

        except AccuLynxAPIError as e:
            print(f"API Error: {str(e)} (Status: {e.status_code})")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


async def lead_examples():
    """Examples of lead-related API operations."""
    api_key = os.getenv("ACCULYNX_API_KEY")
    if not api_key:
        raise ValueError("Please set ACCULYNX_API_KEY environment variable")

    async with AccuLynxAPI(api_key=api_key) as api:
        try:
            # Get lead history with creator information
            lead_id = "your_lead_id_here"  # Replace with actual lead ID
            print(f"\n=== Lead History for {lead_id} ===")
            history = await api.get_lead_history(
                lead_id=lead_id,
                includes=["createdBy"]
            )
            
            for entry in history:
                print(f"Action: {entry.action}")
                print(f"Date: {entry.created_date}")
                if entry.created_by:
                    print(f"Created by: {entry.created_by.first_name} {entry.created_by.last_name}")
                print("---")

        except AccuLynxAPIError as e:
            print(f"API Error: {str(e)} (Status: {e.status_code})")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    # Run job examples
    asyncio.run(job_examples())
    
    # Run lead examples
    # asyncio.run(lead_examples())  # Uncomment when you have a lead ID to test with 