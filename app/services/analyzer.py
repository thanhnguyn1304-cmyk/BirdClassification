from birdnetlib.analyzer import Analyzer
from ..logging_config import get_logger

logger = get_logger("analyzer")

logger.info("Loading BirdNET Model...")
analyzer = Analyzer()
logger.info("BirdNET Model ready.")
