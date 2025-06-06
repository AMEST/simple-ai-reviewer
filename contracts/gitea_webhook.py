from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

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

    def __post_init__(self):
        self.merged_at = self.merged_at if self.merged_at else None

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
class InternalTracker:
    enable_time_tracker: bool
    allow_only_contributors_to_track_time: bool
    enable_issue_dependencies: bool

@dataclass
class Repository:
    id: int
    owner: Union[User,str]
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
    permissions: Union[Permissions,str]
    has_issues: bool
    internal_tracker: Union[InternalTracker,str]
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
        self.owner = User(**self.owner) if isinstance(self.owner, dict) else self.owner
        self.permissions = Permissions(**self.permissions)
        self.internal_tracker = InternalTracker(**self.internal_tracker)
        self.parent = self.parent if self.parent else None
        self.repo_transfer = self.repo_transfer if self.repo_transfer else None

@dataclass
class Comment:
    id: int
    html_url: str
    pull_request_url: str
    issue_url: str
    user: Union[User,str]
    original_author: str
    original_author_id: int
    body: str
    created_at: str
    updated_at: str

    def __post_init__(self):
        self.user = User(**self.user) if isinstance(self.user, dict) else self.user

@dataclass
class Issue:
    id: int
    url: str
    html_url: str
    number: int
    user: User
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
    pull_request: Union[PullRequest,str]
    repository: Union[RepoInIssue,str]

    def __post_init__(self):
        self.user = User(**self.user) if isinstance(self.user, dict) else self.user
        self.pull_request = PullRequest(**self.pull_request)
        self.repository = RepoInIssue(**self.repository)
        self.milestone = self.milestone if self.milestone else None
        self.assignee = self.assignee if self.assignee else None
        self.assignees = self.assignees if self.assignees else None
        self.closed_at = self.closed_at if self.closed_at else None
        self.due_date = self.due_date if self.due_date else None

@dataclass
class GiteaWebhook:
    action: str
    issue: Union[Issue,str]
    comment: Union[Comment,str]
    repository: Union[Repository,str]
    sender: Union[User,str]
    is_pull: bool

    def __post_init__(self):
        self.issue = Issue(**self.issue)
        self.comment = Comment(**self.comment)
        self.repository = Repository(**self.repository)
        self.sender = User(**self.sender) if isinstance(self.sender, dict) else self.sender