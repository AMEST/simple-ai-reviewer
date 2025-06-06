import threading
import time
import logging

from contracts.gitea_pr_url import GiteaPrUrl
from services.gitea_service import GiteaService
from services.queue.task_queue import TaskQueue
from services.review_service import ReviewService

class Worker(threading.Thread):
    def __init__(self, gitea_service: GiteaService, review_service: ReviewService, queue: TaskQueue):
        super().__init__(None, None, None, None, None, daemon=True)
        self.gitea_service = gitea_service
        self.review_service = review_service
        self.queue = queue
        self.logger = logging.getLogger(Worker.__name__)

    def run(self):
        while True:
            time.sleep(60)
            try:
                pull_request = self.queue.dequeue()
                if pull_request is None:
                    continue
                self.__process_review(pull_request)
            except:
                self.logger.error("Error in worker thread", exc_info=True)
                time.sleep(60 * 10)


    def __process_review(self, pull_request: GiteaPrUrl) -> None:
        self.logger.info(f"At first, get diff from repo {pull_request.owner}/{pull_request.repo} PR#{pull_request.pr_number}")
        diff = self.gitea_service.get_pr_diff(pull_request)
        self.logger.info(f"Send diff to LLM for review")
        review_batch = self.review_service.review_pull_request(diff)
        self.logger.info(f"Publish review in comments")
        for review in review_batch:
            self.gitea_service.post_comment(pull_request, review)
        self.logger.info("Review completed")
