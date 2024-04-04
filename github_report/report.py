#!/usr/bin/env python
import github
def m_get_events(self, public=github.GithubObject.NotSet):
        """
        :calls: `GET /users/{user}/events{/privacy} <https://docs.github.com/en/rest/reference/activity#list-events-for-the-authenticated-user>`_
        :param public: bool
        :rtype: :class:`github.PaginatedList.PaginatedList` of :class:`github.Event.Event`
        """
        assert public is github.GithubObject.NotSet or isinstance(public, bool), public
        if public is not github.GithubObject.NotSet and public is True:
            privacy = "/public"
        else:
            privacy = ""

        return github.PaginatedList.PaginatedList(
            github.Event.Event,
            self._requester,
            f"/users/{self.login}/events{privacy}",
            None,
        )
# Monkey patch the get_events to get user events, not global GH events
# (see https://github.com/PyGithub/PyGithub/pull/2172)

#github.AuthenticatedUser.get_events = m_get_events

from github import Github, GithubRetry
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass



_repo_types = ['public', 'private', 'all']

def get_user_meta():
    """_summary_
    """

"""
    TODO:  Make these functions return constituent parts like when, repo, url, summary
    then put into a dataframe to handle time slicing, groupby, duplicates, ect.
"""

_review_events = {}
#If you want timestamps, use this template
#template = '\t*\t{when}: {repo} -- #{num} {title} ({url})'
template = '\t*\t{repo} -- #{num} {title} ({url})'
def process_pull_request_review_event(event: github.Event.Event, date: datetime = datetime.now() ) -> str:
    """_summary_

    Args:
        event (github.Event.Event): _description_

    Returns:
        str: _description_
    """
    #can have multiple reviews of the same PR, only need to report one if it was in the time period
    when = datetime.strptime( event.payload['review']['submitted_at'], "%Y-%m-%dT%H:%M:%S%z" )
    if date.month == when.month and date.year == when.year:
        repo = event.repo.name
        num = event.payload['pull_request']['number']
        if _review_events.get(repo, None) is None:
            _review_events[repo] = {}
        if _review_events[repo].get(num, None) is None:
            _review_events[repo][num] = True
            title = event.payload['pull_request']['title']
            url = event.payload['pull_request']['html_url']
            #return f'\t*\t{when}: {repo} -- #{num} {title} ({url})'
            return template.format(when=when, repo=repo, num=num, title=title, url=url)

def process_pull_request_event(event: github.Event.Event, date: datetime = datetime.now()) -> str:
    """_summary_

    Args:
        event (github.Event.Event): _description_

    Returns:
        str: _description_
    """
    when = datetime.strptime( event.payload['pull_request']['created_at'], "%Y-%m-%dT%H:%M:%S%z" )
    if date.month == when.month and date.year == when.year:
        if event.payload['action'] == "opened":
            num = event.payload['pull_request']['number']
            # when = event.payload['pull_request']['created_at']
            title = event.payload['pull_request']['title']
            url = event.payload['pull_request']['html_url']
            repo = event.repo.name
            #return f'\t*\t{when}: {repo} -- #{num} {title} ({url})'
            return template.format(when=when, repo=repo, num=num, title=title, url=url)

def process_release_event(event: github.Event.Event, date: datetime = datetime.now() ) -> str:
    """_summary_

    Args:
        event (github.Event.Event): _description_
        date (datetime, optional): _description_. Defaults to datetime.now().

    Returns:
        str: _description_
    """
    when = datetime.strptime( event.payload['release']['created_at'], "%Y-%m-%dT%H:%M:%S%z" )
    if date.month == when.month and date.year == when.year:
        if event.payload['action'] == "published":
            num = event.payload['release']['tag_name']
            title = event.payload['release']['name']
            url = event.payload['release']['html_url']
            repo = event.repo.name
            return template.format(when=when, repo=repo, num='', title="Release "+title, url=url).replace('# ', '')
            return f'\t*\t{when}: {repo} -- Release {title} ({url})'
    
def process_issue_event(event: github.Event.Event, date: datetime = datetime.now() ) -> str:
    """_summary_

    Args:
        event (github.Event.Event): _description_
        date (datetime, optional): _description_. Defaults to datetime.now().

    Returns:
        str: _description_
    """
    when = datetime.strptime( event.payload['issue']['created_at'], "%Y-%m-%dT%H:%M:%S%z" )
    if date.month == when.month and date.year == when.year:
        if event.payload['action'] == "opened":
            num = event.payload['issue']['number']
            title = event.payload['issue']['title']
            url = event.payload['issue']['html_url']
            repo = event.repo.name
            return template.format(when=when, repo=repo, num=num, title=title, url=url)

def make_report(organization: str, api_token: str, destination: Path, type: str = 'public', date: datetime = datetime.now(), user: str = ''):
    """
        Find all user meta data in the given organization and use the api_token to scrape data

        Parameters
        ----------
        organization    str containing the organization name, i.e. NOAA-OWP

        api_token       API token with approriate access permissions for the requested type of repos to archive

        destination     Path to the output location to store the report

        type            the type of repositories to record activity for, may be 'all', 'public', 'private'

	"""
    #Rate limit retries 
    gh = Github(api_token, retry=GithubRetry(total=11))

    org = gh.get_organization(organization)
    user = gh.get_user(login=user) if user else gh.get_user()
    events = m_get_events(user)
    #print(events.totalCount)
    #Process PullRequestReviewEvent (action created), IssueEvent (action created), PullRequestEvent (action created), ReleaseEvent (action published)
    prs = []
    reviews = []
    releases = []
    issues = []
    for e in events:
        if e.type == "PullRequestReviewEvent":
            data = process_pull_request_review_event(e, date)
            if(data):
                reviews.append(data)
        elif e.type == "PullRequestEvent":
            data = process_pull_request_event(e, date)
            if(data):
                prs.append(data)
        elif e.type == "ReleaseEvent":
            data = process_release_event(e, date)
            if(data):
                releases.append(data)
        elif e.type == "IssuesEvent":
            data = process_issue_event(e, date)
            if(data):
                issues.append(data)

    print("Features and Bug Fixes Implemented: ")
    for pr in prs:
        print(pr)
    print()
    print("Code Review: ")
    for r in reviews:
        print(r)
    print()
    print("Releases:")
    for r in releases:
        print(r)
    print()
    print("Bugs and Issues identified:")
    for i in issues:
        print(i)
if __name__ == "__main__":
    raise RuntimeError('Module {} called directly; use main package entrypoint instead')
