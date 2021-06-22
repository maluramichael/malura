import os

from diskcache import Cache
import twitter


# cache = Cache("_cache")
#
# for variable in [
#     'TWITTER_CONSUMER_KEY',
#     'TWITTER_CONSUMER_SECRET',
#     'TWITTER_ACCESS_TOKEN_KEY',
#     'TWITTER_ACCESS_TOKEN_SECRET'
# ]:
#     if variable not in os.environ:
#         raise EnvironmentError(f'{variable} environment variable not defined')
#
#
# # @cache.memoize(expire=60 * 60 * 24 * 7)
# async def get_followers():
#     print('Get followers')
#     return 0


def get_twitter_infos():
    print('Get twitter infos')
    # api = twitter.Api(consumer_key=os.environ.get('TWITTER_CONSUMER_KEY'),
    #                   consumer_secret=os.environ.get('TWITTER_CONSUMER_SECRET'),
    #                   access_token_key=os.environ.get('TWITTER_ACCESS_TOKEN_KEY'),
    #                   access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'))
    #
    # user = api.GetUser(user_id='devnetik')
    return {
        'followers': 0
    }
