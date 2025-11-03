from github import Github
import os
from diskcache import Cache

cache = Cache("_cache")

if 'PAT' not in os.environ:
    raise EnvironmentError('PAT environment variable not defined')

token = os.environ.get('PAT')
g = Github(token)


@cache.memoize(expire=60 * 60 * 24 * 7)
def get_repos():
    print('Get github repos')
    user = g.get_user()
    repos = [repo for repo in user.get_repos(type='sources') if repo.owner.login == user.login and not repo.fork and not repo.private]
    # Sort by stars (descending)
    repos.sort(key=lambda repo: repo.stargazers_count, reverse=True)
    return repos


def get_github_infos():
    print('Get github infos')
    repos = get_repos()
    return {
        'repos': repos,
        'repo_count': len(repos),
        'star_count': sum([repo.stargazers_count for repo in repos]),
        'fork_count': sum([repo.forks for repo in repos]),
    }
