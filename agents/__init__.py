# Root Cause Investigation System Agents
# Import agents as they are created

from .overview_agent import OverviewAgent
from .assessment_agent import AssessmentAgent

# V3.1 with fallback to V2
try:
    from .rootcause_agent_v3_1 import RootCauseAgentV3_1
    from .rootcause_agent_v3_1 import RootCauseAgentV3_1 as RootCauseAgent
    _v31_available = True
except Exception as e:
    # Catch ALL errors (ImportError, NameError, AttributeError, etc.)
    # Falls back to V2 if ANY dependency issue occurs
    print(f"⚠️  V3.1 import failed: {type(e).__name__}: {str(e)[:100]}")
    from .rootcause_agent_v2 import RootCauseAgentV2 as RootCauseAgent
    RootCauseAgentV3_1 = None
    _v31_available = False

from .rootcause_agent_v2 import RootCauseAgentV2
from .orchestrator import RootCauseOrchestrator
from .skillbased_docx_agent import SkillBasedDocxAgent

# TODO: Add remaining agents
# from .investigation_agent import InvestigationAgent
# from .recommendation_agent import RecommendationAgent
# from .actionplan_agent import ActionPlanAgent

__all__ = [
    'OverviewAgent',
    'AssessmentAgent',
    'RootCauseAgent',
    'RootCauseAgentV2',
    'RootCauseAgentV3_1',
    'RootCauseOrchestrator',
    'SkillBasedDocxAgent',
    # 'InvestigationAgent',
    # 'RecommendationAgent',
    # 'ActionPlanAgent',
]
