from tastytools.api import Api
from apps.front.api import resources

api = Api(api_name='v1')
api.register(modules=[resources])
