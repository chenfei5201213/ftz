"""
WSGI config for server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from skywalking import agent, config


from server.settings import AGENT_LOGGING_LEVEL, AGENT_NAME, AGENT_COLLECTOR_BACKEND_SERVICES, AGENT_AUTHENTICATION
config.init(
    agent_collector_backend_services=AGENT_COLLECTOR_BACKEND_SERVICES,
    agent_name=AGENT_NAME,  # 此处可自定义应用名称
    agent_authentication=AGENT_AUTHENTICATION,  # 此处替换成步骤1中获得的Token
    agent_logging_level=AGENT_LOGGING_LEVEL)
agent.start()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

application = get_wsgi_application()
