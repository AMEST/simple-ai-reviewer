import logging

from flask import Flask, request

from configuration.web_configuration import WebConfiguration
from contracts.github_webhook import GithubWebhook
from contracts.pr_url import PrUrl
from contracts.gitea_webhook import GiteaWebhook
from contracts.review_task import ReviewTask
from services.gitea_service import GiteaService
from services.github_service import GithubService
from services.queue.task_queue import TaskQueue
from services.review_service import ReviewService


class Api:
    """
    API service for handling webhooks and review requests.
    
    This class provides endpoints for receiving webhooks from Git services
    and processing code review requests.
    """
    START_REVIEW_COMMAND: str = "/start_review"

    def __init__(self, configuration: WebConfiguration, gitea_service: GiteaService, review_service: ReviewService, queue: TaskQueue,
                github_service: GithubService):
        """
        Initialize the API with required services and configuration.
        
        Args:
            configuration (WebConfiguration): Web server configuration
            gitea_service (GiteaService): Service for Gitea interactions
            review_service (ReviewService): Service for performing code reviews
            queue (TaskQueue): Queue for review tasks
            github_service (GithubService): Service for GitHub interactions
        """
        self.configuration = configuration
        self.gitea_service = gitea_service
        self.github_service = github_service
        self.review_service = review_service
        self.queue = queue
        self.logger = logging.getLogger(Api.__name__)
        self.app = Flask(__name__)
        self.app.before_request(self.__require_api_auth)
        self.__configure_routes()

    def start(self):
        """
        Start the API web server.
        
        Runs the Flask application with the configured host and port.
        """
        self.app.run(host=self.configuration.host, port=self.configuration.port)

    def __configure_routes(self):
        """
        Configure API routes for webhook endpoints.
        
        Sets up routes for Gitea and GitHub webhook handlers.
        """
        self.app.add_url_rule("/webhook/gitea",  view_func=self.__gitea_webhook_route, methods=["POST"])
        self.app.add_url_rule("/webhook/github",  view_func=self.__github_webhook_route, methods=["POST"])

    def __require_api_auth(self):
        """
        Middleware for API authentication.
        
        Verifies the request contains a valid API token.
        """
        token = request.args.get("token")
        if token is not None and token == self.configuration.token:
            return
        bearer = request.headers.get("Authorization")
        if bearer is None or bearer == "" or not "Bearer" in bearer:
            return "Unauthorized", 401
        token = bearer.split()[1]
        if token == self.configuration.token:
            return
        return "Unauthorized", 401
    
    def __ensure_gitea_comment_event(self) -> GiteaWebhook:
        """
        Validate and parse Gitea comment webhook event.
        
        Returns:
            GiteaWebhook: Parsed webhook data if valid, None otherwise
        """
        gitea_event = request.headers.get("X-Gitea-Event", None)
        if gitea_event is None or gitea_event != "issue_comment":
            return None
        request_json = request.get_json()
        return GiteaWebhook(**request_json)
    
    def __ensure_github_comment_event(self) -> GithubWebhook:
        """
        Validate and parse GitHub comment webhook event.
        
        Returns:
            GithubWebhook: Parsed webhook data if valid, None otherwise
        """
        github_event = request.headers.get("X-Github-Event", None)
        if github_event is None or github_event != "issue_comment":
            return None
        request_json = request.get_json()
        return GithubWebhook(**request_json)
    
    def __process_review_request(self, pull_request_url: str, git_service: str, comment_body: str) -> None:
        """
        Process a review request from a webhook.
        
        Args:
            pull_request_url (str): URL of the pull request to review
            git_service (str): Name of the Git service (gitea/github)
            comment_body (str): The comment that triggered the review
        """
        self.logger.info("Processing command: %s", comment_body)
        user_message = comment_body.replace(self.START_REVIEW_COMMAND, "").strip()
        review_task = ReviewTask(pull_request_url, git_service, user_message if len(user_message) > 5 else None)
        self.queue.enqueue(review_task)
        pr_url = PrUrl.create_from_url(pull_request_url)
        self.logger.info("%s Review %s/%s #%s enqueued", git_service.upper(), pr_url.owner, pr_url.repo, pr_url.pr_number)
    
    # Routes

    def __gitea_webhook_route(self):
        webhook = self.__ensure_gitea_comment_event()
        if webhook is None:
            return "Not allowed event %s" %(request.headers.get("X-Gitea-Event", None)), 400 
        if webhook.action != "created" or webhook.comment is None:
            return "Is not comment create event. Ignore event", 200 
        if not webhook.comment.body.startswith(self.START_REVIEW_COMMAND):
            return "Comment not start with /start_review. Ignore event", 200
        user_email = webhook.comment.user.email if webhook.comment.user is not None else ""
        if not self.gitea_service.is_allowed_user(user_email):
            fail_response = f"User {user_email} not allowed to start review"
            self.logger.warning(fail_response)
            return fail_response, 403
        
        self.__process_review_request(webhook.comment.pull_request_url, "gitea", webhook.comment.body)
        return "Review task enqueued", 200
    
    def __github_webhook_route(self):
        webhook = self.__ensure_github_comment_event()
        if webhook is None:
            return "Not allowed event %s" %(request.headers.get("X-Github-Event", None)), 400 
        if webhook.action != "created" or webhook.comment is None:
            return "Is not comment create event. Ignore event", 200 
        if not webhook.comment.body.startswith(self.START_REVIEW_COMMAND):
            return "Comment not start with /start_review. Ignore event", 200
        user_login = webhook.comment.user.login if webhook.comment.user is not None else ""
        if not self.github_service.is_allowed_user(user_login):
            fail_response = f"User {user_login} not allowed to start review"
            self.logger.warning(fail_response)
            return fail_response, 403
                
        self.__process_review_request(webhook.issue.pull_request.html_url, "github", webhook.comment.body)
        return "Review task enqueued", 200
