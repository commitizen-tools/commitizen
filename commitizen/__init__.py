import logging
import logging.config
from commitizen.cz import registry
from commitizen.cz.cz_base import BaseCommitizen  # noqa


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'commitizen': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def registered(*args, **kwargs):
    _r = '\n'.join(registry.keys())
    logger.info(_r)


def commiter(name=None):
    """Loaded commitizen.

    :rtype: instance of implemented BaseCommitizen
    """
    if name is None:
        logger.debug('Loading default commitizen')
        name = 'cz_angular'

    return registry[name]()


def run(args):
    _commiter = commiter(name=args.use_cz)
    _commiter.run()
