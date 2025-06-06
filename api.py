from flask import Flask, request
import logging
from services.gitea_service import GiteaService
from services.review_service import ReviewService
from utils.diff_utils import split_diff

from configuration.web_configuration import WebConfiguration

from contracts.gitea_webhook import GiteaWebhook
from contracts.gitea_pr_url import GiteaPrUrl

class Api:
    def __init__(self, configuration: WebConfiguration, gitea_service: GiteaService, review_service: ReviewService):
        self.configuration = configuration
        self.gitea_service = gitea_service
        self.review_service = review_service
        self.logger = logging.getLogger(Api.__name__)
        self.app = Flask(__name__)
        self.app.before_request(self.__require_api_auth)
        self.__configure_routes()

    def start(self):
        self.app.run(host=self.configuration.host, port=self.configuration.port)

    def __configure_routes(self):
        self.app.add_url_rule("/webhook/gitea",  view_func=self.__webhook_route, methods=["POST"])

    def __require_api_auth(self):
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
        gitea_event = request.headers.get("X-Gitea-Event", None)
        if gitea_event is None or gitea_event != "issue_comment":
            return None
        request_json = request.get_json()
        return GiteaWebhook(**request_json)
    
    # Routes

    def __webhook_route(self):
        webhook = self.__ensure_gitea_comment_event()
        if webhook.action != "created" or webhook.comment is None or webhook.comment.body != "/start_review":
            return "", 200
        self.logger.info(f"Processing command: {webhook.comment.body}")
        gitea_pr_url = GiteaPrUrl.create_from_url(webhook.comment.pull_request_url)

        self.logger.info(f"At first, get diff from repo {gitea_pr_url.owner}/{gitea_pr_url.repo} PR#{gitea_pr_url.pr_number}")
        diff = self.gitea_service.get_pr_diff(gitea_pr_url)
        self.logger.info(f"Send diff to LLM for review")
        review_batch = self.review_service.review_pull_request(diff)
        self.logger.info(f"Publish review in comments")
        for review in review_batch:
            self.gitea_service.post_comment(gitea_pr_url, review)
        return "", 200

