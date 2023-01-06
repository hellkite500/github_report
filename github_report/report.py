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
        print(f"HERE: /users/{self.login}/events{privacy}")
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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass



_repo_types = ['public', 'private', 'all']

def get_user_meta():
    """_summary_
    """

def make_report(organization: str, api_token: str, destination: Path, type: str = 'public'):
    """
        Find all user meta data in the given organization and use the api_token to scrape data

        Parameters
        ----------
        organization    str containing the organization name, i.e. NOAA-OWP

        api_token       API token with approriate access permissions for the requested type of repos to archive

        destination     Path to the output location to store the report

        type            the type of repositories to record activity for, may be 'all', 'public', 'private'

	"""
    gh = Github(api_token, retry=GithubRetry(total=11))
    global _gh
    _gh = gh
    org = gh.get_organization(organization)
    print(org)
    user = gh.get_user()
    print(user)
    events = m_get_events(user)
    print(events.totalCount)
    for e in events:
        if e.type == "PullRequestReviewEvent":
            when = e.payload['review']['submitted_at']
            title = e.payload['pull_request']['title']
            url = e.payload['pull_request']['html_url']
            num = e.payload['pull_request']['number']
            repo = e.repo.name
            print(f'{when}: {repo} -- #{num} {title} ({url})')

if __name__ == "__main__":
    raise RuntimeError('Module {} called directly; use main package entrypoint instead')
