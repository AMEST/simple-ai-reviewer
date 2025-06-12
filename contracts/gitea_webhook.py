from dataclasses import dataclass, fields
from typing import Any, List, Optional, Union

@dataclass
class User:
    id: int
    login: str
    login_name: str
    full_name: str
    email: str
    avatar_url: str
    language: str
    is_admin: bool
    last_login: str
    created: str
    restricted: bool
    active: bool
    prohibit_login: bool
    location: str
    website: str
    description: str
    visibility: str
    followers_count: int
    following_count: int
    starred_repos_count: int
    username: str

@dataclass
class PullRequest:
    merged: bool
    merged_at: Optional[str]

@dataclass
class RepoInIssue:
    id: int
    name: str
    owner: str
    full_name: str

@dataclass
class Permissions:
    admin: bool
    push: bool
    pull: bool

@dataclass
class Repository:
    id: int
    owner: Union[User,dict]
    name: str
    full_name: str
    description: str
    empty: bool
    private: bool
    fork: bool
    template: bool
    parent: Optional[Any]
    mirror: bool
    size: int
    language: str
    languages_url: str
    html_url: str
    ssh_url: str
    clone_url: str
    original_url: str
    website: str
    stars_count: int
    forks_count: int
    watchers_count: int
    open_issues_count: int
    open_pr_counter: int
    release_counter: int
    default_branch: str
    archived: bool
    created_at: str
    updated_at: str
    permissions: Union[Permissions,dict]
    has_issues: bool
    internal_tracker: dict
    has_wiki: bool
    has_pull_requests: bool
    has_projects: bool
    ignore_whitespace_conflicts: bool
    allow_merge_commits: bool
    allow_rebase: bool
    allow_rebase_explicit: bool
    allow_squash_merge: bool
    allow_rebase_update: bool
    default_delete_branch_after_merge: bool
    default_merge_style: str
    avatar_url: str
    internal: bool
    mirror_interval: str
    mirror_updated: str
    repo_transfer: Optional[Any]

    def __post_init__(self):
        user_fields = {f.name for f in fields(User)}
        self.owner = User(**{k: v for k, v in self.owner.items() if k in user_fields}) if isinstance(self.owner, dict) else self.owner
        permissions_fields = {f.name for f in fields(Permissions)}
        self.permissions = Permissions(**{k: v for k, v in self.permissions.items() if k in permissions_fields})
        self.parent = self.parent if self.parent else None
        self.repo_transfer = self.repo_transfer if self.repo_transfer else None

@dataclass
class Comment:
    id: int
    html_url: str
    pull_request_url: str
    issue_url: str
    user: Union[User,dict]
    original_author: str
    original_author_id: int
    body: str
    created_at: str
    updated_at: str

    def __post_init__(self):
        user_fields = {f.name for f in fields(User)}
        self.user = User(**{k: v for k, v in self.user.items() if k in user_fields}) if isinstance(self.user, dict) else self.user

@dataclass
class Issue:
    id: int
    url: str
    html_url: str
    number: int
    user: Union[User, dict]
    original_author: str
    original_author_id: int
    title: str
    body: str
    ref: str
    labels: List[Any]
    milestone: Optional[Any]
    assignee: Optional[Any]
    assignees: Optional[Any]
    state: str
    is_locked: bool
    comments: int
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    due_date: Optional[str]
    pull_request: Union[PullRequest,dict]
    repository: Union[RepoInIssue,dict]

    def __post_init__(self):
        user_fields = {f.name for f in fields(User)}
        self.user = User(**{k: v for k, v in self.user.items() if k in user_fields}) if isinstance(self.user, dict) else self.user
        pr_fields = {f.name for f in fields(PullRequest)}
        self.pull_request = PullRequest(**{k: v for k, v in self.pull_request.items() if k in pr_fields})
        repo_fields = {f.name for f in fields(RepoInIssue)}
        self.repository = RepoInIssue(**{k: v for k, v in self.repository.items() if k in repo_fields})
        self.milestone = self.milestone if self.milestone else None
        self.assignee = self.assignee if self.assignee else None
        self.assignees = self.assignees if self.assignees else None
        self.closed_at = self.closed_at if self.closed_at else None
        self.due_date = self.due_date if self.due_date else None

@dataclass
class GiteaWebhook:
    action: str
    issue: Union[Issue,dict]
    comment: Union[Comment,dict]
    repository: Union[Repository,dict]
    sender: Union[User,dict]
    is_pull: bool

    def __post_init__(self):
        issue_fields = {f.name for f in fields(Issue)}
        self.issue = Issue(**{k: v for k, v in self.issue.items() if k in issue_fields})
        comment_fields = {f.name for f in fields(Comment)}
        self.comment = Comment(**{k: v for k, v in self.comment.items() if k in comment_fields})
        repository_fields = {f.name for f in fields(Repository)}
        self.repository = Repository(**{k: v for k, v in self.repository.items() if k in repository_fields})
        sender_fields = {f.name for f in fields(User)}
        self.sender = User(**{k: v for k, v in self.sender.items() if k in sender_fields}) if isinstance(self.sender, dict) else self.sender