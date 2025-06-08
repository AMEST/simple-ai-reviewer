from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union, Type

@dataclass
class User:
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    user_view_type: str
    site_admin: bool

@dataclass
class Label:
    id: int
    node_id: str
    url: str
    name: str
    color: str
    default: bool
    description: str

@dataclass
class PullRequest:
    url: str
    html_url: str
    diff_url: str
    patch_url: str
    merged_at: Optional[str]

@dataclass
class Issue:
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    id: int
    node_id: str
    number: int
    title: str
    user: Union[User, dict]
    labels: List[Union[Label, dict]]
    state: str
    locked: bool
    assignee: Optional[Union[User, dict]]
    assignees: List[Union[User, dict]]
    milestone: Optional[str]
    comments: int
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    author_association: str
    active_lock_reason: Optional[str]
    draft: bool
    pull_request: Union[PullRequest, dict]
    body: Optional[str]
    reactions: dict
    timeline_url: str
    performed_via_github_app: Optional[str]
    state_reason: Optional[str]

    def __post_init__(self):
        if isinstance(self.user, dict):
            self.user = User(**self.user)
        if isinstance(self.labels, list):
            self.labels = [Label(**label) if isinstance(label, dict) else label for label in self.labels]
        if isinstance(self.assignee, dict):
            self.assignee = User(**self.assignee)
        if isinstance(self.assignees, list):
            self.assignees = [User(**assignee) if isinstance(assignee, dict) else assignee for assignee in self.assignees]
        if isinstance(self.pull_request, dict):
            self.pull_request = PullRequest(**self.pull_request)


@dataclass
class Comment:
    url: str
    html_url: str
    issue_url: str
    id: int
    node_id: str
    user: Union[User, dict]
    created_at: str
    updated_at: str
    author_association: str
    body: str
    reactions: dict
    performed_via_github_app: Optional[str]

    def __post_init__(self):
        if isinstance(self.user, dict):
            self.user = User(**self.user)

@dataclass
class Repository:
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: Union[User, dict]
    html_url: str
    description: str
    fork: bool
    url: str
    forks_url: str
    keys_url: str
    collaborators_url: str
    teams_url: str
    hooks_url: str
    issue_events_url: str
    events_url: str
    assignees_url: str
    branches_url: str
    tags_url: str
    blobs_url: str
    git_tags_url: str
    git_refs_url: str
    trees_url: str
    statuses_url: str
    languages_url: str
    stargazers_url: str
    contributors_url: str
    subscribers_url: str
    subscription_url: str
    commits_url: str
    git_commits_url: str
    comments_url: str
    issue_comment_url: str
    contents_url: str
    compare_url: str
    archive_url: str
    downloads_url: str
    issues_url: str
    pulls_url: str
    milestones_url: str
    notifications_url: str
    labels_url: str
    releases_url: str
    deployments_url: str
    created_at: str
    updated_at: str
    pushed_at: str
    git_url: str
    ssh_url: str
    clone_url: str
    svn_url: str
    homepage: str
    size: int
    stargazers_count: int
    watchers_count: int
    language: str
    has_issues: bool
    has_projects: bool
    has_downloads: bool
    has_wiki: bool
    has_pages: bool
    has_discussions: bool
    forks_count: int
    mirror_url: Optional[str]
    archived: bool
    disabled: bool
    open_issues_count: int
    license: Dict[str, str]
    allow_forking: bool
    is_template: bool
    web_commit_signoff_required: bool
    topics: List[str]
    visibility: str
    forks: int
    open_issues: int
    watchers: int
    default_branch: str
    merges_url: str

    def __post_init__(self):
        if isinstance(self.owner, dict):
            self.owner = User(**self.owner)

@dataclass
class GithubWebhook:
    action: str
    issue: Union[Issue, dict]
    comment: Union[Comment, dict]
    repository: Union[Repository, dict]
    sender: Union[User, dict]

    def __post_init__(self):
        if isinstance(self.issue, dict):
            self.issue = Issue(**self.issue)
        if isinstance(self.comment, dict):
            self.comment = Comment(**self.comment)
        if isinstance(self.repository, dict):
            self.repository = Repository(**self.repository)
        if isinstance(self.sender, dict):
            self.sender = User(**self.sender)
