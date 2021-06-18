from github import Github
import os
from diskcache import Cache

cache = Cache("_cache")
token = os.environ.get('TOKEN')

g = None
if token:
    g = Github(token)


@cache.memoize()
def get_repos():
    if g:
        user = g.get_user()
        repos = [repo for repo in user.get_repos(type='sources') if repo.owner.login == user.login and not repo.fork]
        return repos
    else:
        return []


def get_github_infos():
    repos = get_repos()
    return {
        'repos': repos,
        'repo_count': len(repos),
        'star_count': sum([repo.stargazers_count for repo in repos]),
        'fork_count': sum([repo.forks for repo in repos]),
    }
