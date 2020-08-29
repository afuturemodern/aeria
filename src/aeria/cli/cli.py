import logging
import click

from ..version import __version__
from ..core import SerialNumberStruct

logging.basicConfig()
log = logging.getLogger(__name__)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(version=__version__)
def aeria():
    pass
