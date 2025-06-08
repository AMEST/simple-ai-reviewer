import threading
import time
import logging

from contracts.pr_url import PrUrl
from contracts.review_task import ReviewTask
from services.git_service import GitService
from services.gitea_service import GiteaService
from services.github_service import GithubService
from services.queue.task_queue import TaskQueue
from services.review_service import ReviewService

class Worker(threading.Thread):
    """
    Worker thread for processing code review tasks.
    
    This worker continuously processes tasks from a queue, performing code reviews
    using the appropriate Git service and review service.
    """
    def __init__(self, gitea_service: GiteaService, github_service: GithubService, review_service: ReviewService, queue: TaskQueue):
        """
        Initialize the worker with required services and task queue.
        
        Args:
            gitea_service (GiteaService): Service for Gitea interactions
            github_service (GithubService): Service for GitHub interactions
            review_service (ReviewService): Service for performing code reviews
            queue (TaskQueue): Queue containing review tasks
        """
        super().__init__(daemon=True)
        self.gitea_service = gitea_service
        self.github_service = github_service
        self.review_service = review_service
        self.queue = queue
        self.logger = logging.getLogger(Worker.__name__)

    def run(self):
        """
        Main worker loop that processes tasks from the queue.
        
        Continuously dequeues tasks and processes them using the appropriate Git service.
        Handles errors and implements retry logic.
        """
        while True:
            try:
                review_task: ReviewTask  = self.queue.dequeue()
                if review_task is None:
                    time.sleep(60) # Check for new tasks every 60 seconds
                    continue
                if review_task.git_service == "gitea":
                    self.__process_review(self.gitea_service, review_task)
                elif review_task.git_service == "github":
                    self.__process_review(self.github_service, review_task)
                else:
                    self.logger.error("Unknown git service: %s", review_task.git_service)
            except Exception as e:
                self.logger.error("Error in worker thread: %s", e, exc_info=True)
                time.sleep(60 * 10) # Wait longer after an error
            time.sleep(60) # Check for new tasks every 60 seconds

    def __process_review(self, service: GitService, review_task: ReviewTask) -> None:
        """
        Process a single review task.
        
        Args:
            service (GitService): The Git service to use for the review
            review_task (ReviewTask): The review task to process
        """
        try:
            pull_request = PrUrl.create_from_url(review_task.pull_request_url)
            self.logger.info("Start review (%s) %s/%s #%s", review_task.git_service, pull_request.owner, pull_request.repo, pull_request.pr_number)
            diff = service.get_pr_diff(pull_request)
            self.logger.info("Send diff to LLM for review")
            review_batch = self.review_service.review_pull_request(diff, review_task.user_message)
            for review in review_batch:
                service.post_comment(pull_request, review)
            self.logger.info("Review completed")
        except Exception as e:
            self.logger.error("Error during review process for PR (%s) %s: %s", review_task.git_service, review_task.pull_request_url, e, exc_info=True)
            time.sleep(60 * 10) # Wait longer after an error
