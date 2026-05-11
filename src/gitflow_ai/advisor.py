"""
Branch Advisor Module
分支策略顾问 - 提供分支管理策略建议
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from .core import GitFlowCore


class WorkflowType(Enum):
    """工作流类型枚举"""
    GIT_FLOW = "Git Flow"
    GITHUB_FLOW = "GitHub Flow"
    GITLAB_FLOW = "GitLab Flow"
    TRUNK_BASED = "Trunk-Based Development"
    SIMPLE = "Simple Workflow"


@dataclass
class BranchStrategy:
    """分支策略数据类"""
    name: str
    description: str
    main_branches: List[str]
    feature_pattern: str
    release_pattern: Optional[str]
    hotfix_pattern: Optional[str]
    pros: List[str]
    cons: List[str]
    recommended_for: List[str]


@dataclass
class ConflictRisk:
    """冲突风险数据类"""
    level: str  # low, medium, high
    score: float  # 0-100
    reasons: List[str]
    recommendations: List[str]


class BranchAdvisor:
    """分支策略顾问类"""

    STRATEGIES = {
        WorkflowType.GIT_FLOW: BranchStrategy(
            name="Git Flow",
            description="经典的分支管理模型，适合有版本发布周期的项目",
            main_branches=["main", "develop"],
            feature_pattern="feature/*",
            release_pattern="release/*",
            hotfix_pattern="hotfix/*",
            pros=[
                "清晰的分支职责分离",
                "支持并行开发",
                "适合版本发布管理",
                "hotfix流程完善"
            ],
            cons=[
                "分支较多，管理复杂",
                "合并操作频繁",
                "不适合持续部署"
            ],
            recommended_for=[
                "有明确版本发布计划的项目",
                "中大型团队",
                "需要支持多版本维护的项目"
            ]
        ),
        WorkflowType.GITHUB_FLOW: BranchStrategy(
            name="GitHub Flow",
            description="简化的分支模型，适合持续部署的项目",
            main_branches=["main"],
            feature_pattern="feature-*",
            release_pattern=None,
            hotfix_pattern=None,
            pros=[
                "简单易懂",
                "适合持续部署",
                "代码审查流程清晰",
                "部署频率高"
            ],
            cons=[
                "不适合多版本维护",
                "main分支需要保持稳定",
                "缺乏发布分支管理"
            ],
            recommended_for=[
                "Web应用",
                "SaaS产品",
                "持续部署环境",
                "小型到中型团队"
            ]
        ),
        WorkflowType.GITLAB_FLOW: BranchStrategy(
            name="GitLab Flow",
            description="结合Git Flow和GitHub Flow优点的混合模型",
            main_branches=["main", "production"],
            feature_pattern="feature/*",
            release_pattern="release/*",
            hotfix_pattern=None,
            pros=[
                "灵活的分支策略",
                "支持环境部署",
                "适合多环境管理",
                "发布控制灵活"
            ],
            cons=[
                "需要理解多种模式",
                "配置相对复杂",
                "团队需要培训"
            ],
            recommended_for=[
                "需要多环境部署的项目",
                "有预发布环境的产品",
                "中型团队"
            ]
        ),
        WorkflowType.TRUNK_BASED: BranchStrategy(
            name="Trunk-Based Development",
            description="基于主干开发的模式，分支生命周期极短",
            main_branches=["main"],
            feature_pattern="short-lived-branch",
            release_pattern=None,
            hotfix_pattern=None,
            pros=[
                "极快的集成速度",
                "减少合并冲突",
                "适合持续集成",
                "代码始终可发布"
            ],
            cons=[
                "需要完善的CI/CD",
                "不适合大型功能开发",
                "需要功能开关支持",
                "团队纪律要求高"
            ],
            recommended_for=[
                "高频率部署团队",
                "有完善自动化测试的项目",
                "Google/Facebook式的大团队"
            ]
        ),
        WorkflowType.SIMPLE: BranchStrategy(
            name="Simple Workflow",
            description="最简单的分支模型，适合个人或小型项目",
            main_branches=["main"],
            feature_pattern="any-branch-name",
            release_pattern=None,
            hotfix_pattern=None,
            pros=[
                "极简操作",
                "零学习成本",
                "适合个人项目",
                "快速迭代"
            ],
            cons=[
                "缺乏流程规范",
                "不适合协作",
                "难以管理复杂功能"
            ],
            recommended_for=[
                "个人项目",
                "小型原型项目",
                "学习练习",
                "文档项目"
            ]
        ),
    }

    def __init__(self, core: GitFlowCore):
        self.core = core

    def detect_current_workflow(self) -> Tuple[WorkflowType, float]:
        """检测当前使用的工作流类型"""
        branches = self.core.get_branch_list()
        branch_names = [b["name"] for b in branches]

        scores = {wt: 0.0 for wt in WorkflowType}

        # Git Flow 检测
        if "develop" in branch_names or "dev" in branch_names:
            scores[WorkflowType.GIT_FLOW] += 30
        if any("feature/" in b for b in branch_names):
            scores[WorkflowType.GIT_FLOW] += 20
        if any("release/" in b for b in branch_names):
            scores[WorkflowType.GIT_FLOW] += 20
        if any("hotfix/" in b for b in branch_names):
            scores[WorkflowType.GIT_FLOW] += 20

        # GitHub Flow 检测
        if "main" in branch_names or "master" in branch_names:
            scores[WorkflowType.GITHUB_FLOW] += 20
            if "develop" not in branch_names:
                scores[WorkflowType.GITHUB_FLOW] += 20

        # GitLab Flow 检测
        if "production" in branch_names or "pre-production" in branch_names:
            scores[WorkflowType.GITLAB_FLOW] += 40

        # Trunk-Based 检测
        commits = self.core.get_commit_history(50)
        if len(commits) > 10:
            # 检查分支合并频率
            merge_commits = [c for c in commits if "Merge" in c["message"]]
            if len(merge_commits) < 3:
                scores[WorkflowType.TRUNK_BASED] += 30

        # Simple Workflow 检测
        if len(branch_names) <= 3:
            scores[WorkflowType.SIMPLE] += 30

        # 找出得分最高的
        detected = max(scores, key=scores.get)
        confidence = min(100, scores[detected])

        return detected, confidence

    def recommend_workflow(self) -> Tuple[WorkflowType, List[str]]:
        """推荐适合的工作流"""
        repo_info = self.core.get_repo_info()
        branches = self.core.get_branch_list()
        commits = self.core.get_commit_history(30)

        reasons = []

        # 分析项目特征
        branch_count = len(branches)
        commit_count = len(commits)

        # 检查远程仓库
        has_remote = bool(repo_info.get("remotes"))

        # 检查团队规模（通过提交者数量估算）
        authors = set(c["author"] for c in commits)
        team_size = len(authors)

        # 决策逻辑
        if team_size == 1 and branch_count <= 3:
            recommended = WorkflowType.SIMPLE
            reasons.append("个人项目，推荐使用简单工作流")

        elif not has_remote:
            recommended = WorkflowType.SIMPLE
            reasons.append("本地项目，无需复杂分支策略")

        elif team_size >= 10:
            recommended = WorkflowType.TRUNK_BASED
            reasons.append(f"大团队({team_size}人)，适合主干开发模式")
            reasons.append("高频集成可减少合并冲突")

        elif any("release" in b["name"].lower() for b in branches):
            recommended = WorkflowType.GIT_FLOW
            reasons.append("检测到发布分支，适合Git Flow")

        elif "production" in [b["name"] for b in branches]:
            recommended = WorkflowType.GITLAB_FLOW
            reasons.append("检测到生产环境分支，适合GitLab Flow")

        elif commit_count > 20 and team_size <= 5:
            recommended = WorkflowType.GITHUB_FLOW
            reasons.append("活跃的小型团队，适合GitHub Flow")
            reasons.append("简化流程可提高部署频率")

        else:
            recommended = WorkflowType.GITHUB_FLOW
            reasons.append("默认推荐GitHub Flow，简单高效")

        return recommended, reasons

    def get_strategy_details(self, workflow_type: WorkflowType) -> BranchStrategy:
        """获取策略详情"""
        return self.STRATEGIES[workflow_type]

    def suggest_branch_name(self, feature_description: str) -> List[str]:
        """根据功能描述建议分支名"""
        # 清理描述
        cleaned = re.sub(r'[^\w\s-]', '', feature_description.lower())
        words = cleaned.split()

        suggestions = []

        # Git Flow 风格
        if len(words) >= 2:
            feature_name = "-".join(words[:4])
            suggestions.append(f"feature/{feature_name}")

        # GitHub Flow 风格
        if len(words) >= 2:
            feature_name = "-".join(words[:3])
            suggestions.append(f"feature-{feature_name}")

        # 简洁风格
        if words:
            short_name = words[0]
            if len(words) > 1:
                short_name += f"-{words[1]}"
            suggestions.append(short_name)

        # 使用动词开头
        verbs = ["add", "fix", "update", "refactor", "implement", "remove"]
        for verb in verbs:
            if any(word.startswith(verb) for word in words):
                rest = "-".join([w for w in words if not w.startswith(verb)][:3])
                if rest:
                    suggestions.append(f"{verb}-{rest}")
                break

        return list(dict.fromkeys(suggestions))  # 去重保持顺序

    def analyze_conflict_risk(self) -> ConflictRisk:
        """分析冲突风险"""
        branches = self.core.get_branch_list()
        current_branch = next((b for b in branches if b["is_current"]), None)

        if not current_branch:
            return ConflictRisk("unknown", 0, ["无法获取当前分支信息"], [])

        reasons = []
        recommendations = []
        score = 0

        # 检查分支是否落后于远程
        if current_branch.get("track"):
            track = current_branch["track"]
            if "behind" in track:
                behind_count = self._extract_number(track, "behind")
                if behind_count > 10:
                    score += 30
                    reasons.append(f"分支落后于远程 {behind_count} 个提交")
                    recommendations.append("建议先执行 'git pull' 同步远程变更")
                elif behind_count > 0:
                    score += 10
                    reasons.append(f"分支落后于远程 {behind_count} 个提交")

        # 检查是否有其他活跃分支
        active_branches = [b for b in branches if not b["name"].startswith("remotes/")]
        if len(active_branches) > 5:
            score += 15
            reasons.append(f"存在 {len(active_branches)} 个本地分支，可能产生冲突")
            recommendations.append("建议清理已合并的分支")

        # 检查未推送的提交
        stdout, _, _ = self.core._run_git(["log", "@{u}..", "--oneline"])
        unpushed = len([l for l in stdout.strip().split("\n") if l])
        if unpushed > 10:
            score += 20
            reasons.append(f"有 {unpushed} 个未推送的提交")
            recommendations.append("建议及时推送代码，减少冲突风险")

        # 检查暂存区
        status = self.core.get_status()
        if status["unstaged"]:
            score += 5
            reasons.append("存在未暂存的变更")

        # 确定风险等级
        if score >= 50:
            level = "high"
        elif score >= 25:
            level = "medium"
        else:
            level = "low"

        if not recommendations and level != "low":
            recommendations.append("建议定期同步远程分支")
            recommendations.append("推送前检查是否有冲突")

        return ConflictRisk(level, score, reasons, recommendations)

    def _extract_number(self, text: str, keyword: str) -> int:
        """从文本中提取数字"""
        pattern = rf'{keyword}\s+(\d+)'
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
        return 0

    def get_workflow_comparison(self) -> List[Dict[str, Any]]:
        """获取工作流对比信息"""
        comparison = []

        for workflow_type, strategy in self.STRATEGIES.items():
            comparison.append({
                "name": strategy.name,
                "description": strategy.description,
                "complexity": self._rate_complexity(strategy),
                "team_size": self._rate_team_size(strategy),
                "deployment": self._rate_deployment(strategy),
            })

        return comparison

    def _rate_complexity(self, strategy: BranchStrategy) -> str:
        """评估复杂度"""
        if strategy.name in ["Simple Workflow"]:
            return "⭐ 简单"
        elif strategy.name in ["GitHub Flow", "Trunk-Based Development"]:
            return "⭐⭐ 中等"
        else:
            return "⭐⭐⭐ 复杂"

    def _rate_team_size(self, strategy: BranchStrategy) -> str:
        """评估适合团队规模"""
        if "个人" in str(strategy.recommended_for):
            return "1人"
        elif "小型" in str(strategy.recommended_for):
            return "1-5人"
        elif "中型" in str(strategy.recommended_for):
            return "5-20人"
        else:
            return "20+人"

    def _rate_deployment(self, strategy: BranchStrategy) -> str:
        """评估部署频率"""
        if strategy.name == "Trunk-Based Development":
            return "持续部署"
        elif strategy.name == "GitHub Flow":
            return "频繁部署"
        elif strategy.name == "Git Flow":
            return "版本发布"
        else:
            return "按需部署"
