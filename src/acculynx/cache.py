from typing import Dict, Optional
from datetime import datetime, timedelta
import asyncio
from .models import Job
from asyncio import Lock, Semaphore

class JobCache:
    def __init__(self, refresh_interval: int = 3600):
        """Initialize the job cache.
        
        Args:
            refresh_interval: How often to refresh the cache in seconds (default: 1 hour)
        """
        self._jobs: Dict[str, Job] = {}
        self._jobs_by_number: Dict[str, Job] = {}
        self._last_refresh: Optional[datetime] = None
        self.refresh_interval = refresh_interval
        self._refresh_task: Optional[asyncio.Task] = None
        self._lock = Lock()
        self._rate_limit = Semaphore(25)  # Allow 25 concurrent requests (buffer for safety)

    async def start_refresh_task(self, api):
        """Start the periodic refresh task."""
        self._refresh_task = asyncio.create_task(self._periodic_refresh(api))

    async def stop_refresh_task(self):
        """Stop the periodic refresh task."""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            self._refresh_task = None

    async def _periodic_refresh(self, api):
        """Periodically refresh the job cache."""
        while True:
            await self.refresh(api)
            await asyncio.sleep(self.refresh_interval)

    async def _wait_for_rate_limit(self):
        """Ensure we don't exceed 30 requests per minute."""
        now = datetime.now()
        if (now - self._last_request_time) < timedelta(minutes=1):
            await asyncio.sleep(2)  # Wait 2 seconds between batches
        self._last_request_time = now

    async def refresh(self, api):
        """Refresh the job cache."""
        jobs = []
        try:
            # First request to get total count
            initial_jobs = await api.get_jobs(page_size=25, page_start_index=0)
            jobs.extend(initial_jobs)
            
            # Keep fetching until we get no more jobs
            start_index = 25
            while True:
                tasks = []
                for _ in range(25):  # Create batch of 25 requests
                    tasks.append(api.get_jobs(page_size=25, page_start_index=start_index))
                    start_index += 25

                job_lists = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                new_jobs_found = False
                for job_list in job_lists:
                    if isinstance(job_list, list) and job_list:
                        jobs.extend(job_list)
                        new_jobs_found = True
                
                print(f"Cached {len(jobs)} jobs...")
                
                # If no new jobs were found in this batch, we're done
                if not new_jobs_found:
                    break

            async with self._lock:
                self._jobs = {job.id: job for job in jobs}
                self._jobs_by_number = {job.job_number: job for job in jobs if job.job_number}
                self._last_refresh = datetime.now()
            print(f"Job cache refreshed with {len(jobs)} jobs")
        except Exception as e:
            print(f"Error refreshing cache: {e}")

    def get_by_id(self, job_id: str) -> Optional[Job]:
        """Get a job by its ID."""
        return self._jobs.get(job_id)

    async def get_by_number(self, job_number: str) -> Optional[Job]:
        """Get a job by its number."""
        async with self._lock:
            return self._jobs_by_number.get(job_number)

    async def search(self, query: str) -> list[Job]:
        """Search for jobs by name or number."""
        query = query.lower()
        async with self._lock:
            return [
                job for job in self._jobs.values()
                if (job.job_number and query in job.job_number.lower()) or
                   (job.job_name and query in job.job_name.lower())
            ]

    @property
    def last_refresh(self) -> Optional[datetime]:
        """Get the timestamp of the last refresh."""
        return self._last_refresh 