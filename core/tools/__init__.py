from core.tools.base import Tool
from core.tools.info_database import InfoDatabase
from core.tools.interaction import InteractionRetriever

TOOL_MAP: dict[str, type] = {
    'info': InfoDatabase,
    'interaction': InteractionRetriever,
}