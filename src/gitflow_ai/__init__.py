"""
GitFlow AI - AI驱动的终端Git工作流智能助手

🚀 AI-Powered Terminal Git Workflow Assistant
🤖 Smart commit analysis, branch strategy advisor, conflict prevention
📝 Zero dependencies core, local-first design

Author: GitFlow AI Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "GitFlow AI Team"
__license__ = "MIT"

from .core import GitFlowCore
from .analyzer import CommitAnalyzer
from .advisor import BranchAdvisor

__all__ = ["GitFlowCore", "CommitAnalyzer", "BranchAdvisor"]
