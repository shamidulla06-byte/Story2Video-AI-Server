from datetime import datetime
from threading import Lock


class JobManager:
    """
    Story2Video Job Queue Manager

    Handles video generation jobs and their status.
    """

    def __init__(self):
        self.jobs = {}
        self.lock = Lock()

    def create_job(self, job_id: str, prompt: str, mode: str, duration: int):

        job = {
            "job_id": job_id,
            "status": "queued",
            "prompt": prompt,
            "mode": mode,
            "duration": duration,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "video_url": None,
            "error": None
        }

        with self.lock:
            self.jobs[job_id] = job

        return job

    def update_status(
        self,
        job_id: str,
        status: str,
        video_url=None,
        error=None
    ):

        with self.lock:

            if job_id not in self.jobs:
                return None

            self.jobs[job_id]["status"] = status
            self.jobs[job_id]["updated_at"] = (
                datetime.utcnow().isoformat()
            )

            if video_url is not None:
                self.jobs[job_id]["video_url"] = video_url

            if error is not None:
                self.jobs[job_id]["error"] = error

            return self.jobs[job_id]

    def get_job(self, job_id: str):

        with self.lock:
            return self.jobs.get(job_id)

    def get_all_jobs(self):

        with self.lock:
            return list(self.jobs.values())


job_manager = JobManager()
