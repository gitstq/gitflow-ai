"""
Commit Analyzer Module
提交分析器 - 智能分析代码变更并生成提交建议
"""

import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from .core import GitFlowCore, ChangeType, FileChange, CommitSuggestion


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    suggestions: List[CommitSuggestion]
    patterns: Dict[str, Any]
    quality_score: float
    warnings: List[str]
    recommendations: List[str]


class CommitAnalyzer:
    """提交分析器类"""

    # 文件扩展名到类型的映射
    FILE_PATTERNS = {
        "test": ["_test.py", ".test.js", ".spec.ts", "_test.go", ".test.java", "_spec.rb", "Test.cs"],
        "doc": [".md", ".rst", ".txt", "README", "CHANGELOG", "LICENSE", "CONTRIBUTING"],
        "config": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env", ".conf"],
        "style": [".css", ".scss", ".sass", ".less", ".styl"],
        "frontend": [".html", ".jsx", ".tsx", ".vue", ".svelte"],
        "backend": [".py", ".js", ".ts", ".go", ".java", ".rb", ".php", ".cs", ".rs"],
    }

    # 关键词到变更类型的映射
    KEYWORD_PATTERNS = {
        ChangeType.FIX: [
            "fix", "bug", "修复", "解决", "修正", "补丁", "patch",
            "error", "exception", "crash", "broken", "issue"
        ],
        ChangeType.FEATURE: [
            "feat", "feature", "add", "new", "功能", "新增", "添加", "实现",
            "support", "enable", "introduce"
        ],
        ChangeType.DOCS: [
            "doc", "docs", "document", "readme", "注释", "文档", "说明",
            "comment", "guide", "tutorial"
        ],
        ChangeType.REFACTOR: [
            "refactor", "重构", "优化", "改进", "clean", "cleanup",
            "restructure", "redesign", "simplify"
        ],
        ChangeType.TEST: [
            "test", "tests", "testing", "spec", "测试", "用例", "coverage",
            "unittest", "jest", "pytest"
        ],
        ChangeType.STYLE: [
            "style", "format", "lint", "样式", "格式", "美化",
            "formatting", "whitespace", "indent"
        ],
        ChangeType.PERF: [
            "perf", "performance", "优化", "加速", "性能", "提速",
            "optimize", "speed", "fast", "improve", "cache"
        ],
        ChangeType.CI: [
            "ci", "workflow", "action", "pipeline", "构建", "部署",
            "github", "gitlab", "jenkins", "travis"
        ],
        ChangeType.CHORE: [
            "chore", "deps", "dependency", "update", "升级", "依赖",
            "bump", "upgrade", "maintenance", "routine"
        ],
    }

    def __init__(self, core: GitFlowCore):
        self.core = core

    def analyze(self) -> AnalysisResult:
        """执行完整分析"""
        diff = self.core.get_staged_diff()
        if not diff.strip():
            return AnalysisResult(
                suggestions=[],
                patterns={},
                quality_score=0,
                warnings=["暂存区为空，没有可分析的变更"],
                recommendations=["请使用 'git add' 添加文件到暂存区"]
            )

        patterns = self.core.analyze_diff_patterns(diff)
        files = self.core.get_staged_files()

        warnings = self._detect_warnings(patterns, files)
        recommendations = self._generate_recommendations(patterns, files)

        suggestions = self._generate_suggestions(diff, patterns, files)
        quality_score = self._calculate_quality_score(patterns, files, warnings)

        return AnalysisResult(
            suggestions=suggestions,
            patterns=patterns,
            quality_score=quality_score,
            warnings=warnings,
            recommendations=recommendations
        )

    def _detect_warnings(self, patterns: Dict[str, Any], files: List[FileChange]) -> List[str]:
        """检测潜在问题"""
        warnings = []

        # 检查大文件变更
        total_lines = patterns.get("total_additions", 0) + patterns.get("total_deletions", 0)
        if total_lines > 500:
            warnings.append(f"⚠️ 变更行数较多 ({total_lines} 行)，建议拆分为多个提交")

        # 检查文件数量
        if patterns.get("files_changed", 0) > 20:
            warnings.append(f"⚠️ 变更文件较多 ({patterns['files_changed']} 个)，可能包含不相关的修改")

        # 检查敏感文件
        sensitive_patterns = [".env", "password", "secret", "key", "token", "credential"]
        for file in files:
            if any(pattern in file.path.lower() for pattern in sensitive_patterns):
                warnings.append(f"⚠️ 检测到可能包含敏感信息的文件: {file.path}")

        # 检查测试覆盖
        has_source = bool(patterns.get("source_files"))
        has_tests = bool(patterns.get("test_files"))
        if has_source and not has_tests:
            warnings.append("⚠️ 修改了源代码但未包含测试文件，建议添加相应测试")

        # 检查配置文件变更
        if patterns.get("config_files"):
            warnings.append(f"⚠️ 配置文件变更 ({len(patterns['config_files'])} 个)，请确保配置正确")

        return warnings

    def _generate_recommendations(self, patterns: Dict[str, Any], files: List[FileChange]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 提交粒度建议
        file_count = patterns.get("files_changed", 0)
        if file_count <= 3:
            recommendations.append("✅ 提交粒度适中，便于代码审查")
        elif file_count <= 10:
            recommendations.append("💡 提交粒度较大，建议确保变更逻辑相关")
        else:
            recommendations.append("💡 建议将不相关的变更拆分为多个提交")

        # 文档更新建议
        if patterns.get("source_files") and not patterns.get("doc_files"):
            # 检查是否是公开API变更
            recommendations.append("💡 如果包含API变更，建议同步更新文档")

        # 提交信息建议
        recommendations.append("💡 使用 Conventional Commits 规范编写提交信息")
        recommendations.append("💡 提交信息应清晰描述'做了什么'和'为什么'")

        return recommendations

    def _generate_suggestions(
        self,
        diff: str,
        patterns: Dict[str, Any],
        files: List[FileChange]
    ) -> List[CommitSuggestion]:
        """生成提交建议"""
        suggestions = []

        # 分析变更类型
        change_type = self._detect_change_type(diff, patterns, files)

        # 推断作用域
        scope = self._detect_scope(files)

        # 生成描述
        description = self._generate_description(patterns, files, change_type)

        # 检查是否为破坏性变更
        breaking = self._is_breaking_change(diff)

        # 生成不同风格的提交信息
        # 1. 标准 Conventional Commit
        msg1 = self._format_commit_message(change_type, scope, description, breaking)
        suggestions.append(CommitSuggestion(
            message=msg1,
            change_type=change_type,
            scope=scope,
            description=description,
            breaking=breaking,
            score=90.0
        ))

        # 2. 简洁版本
        short_desc = self._shorten_description(description)
        msg2 = self._format_commit_message(change_type, scope, short_desc, breaking)
        if msg2 != msg1:
            suggestions.append(CommitSuggestion(
                message=msg2,
                change_type=change_type,
                scope=scope,
                description=short_desc,
                breaking=breaking,
                score=85.0
            ))

        # 3. 详细版本（包含文件列表）
        detailed_desc = self._generate_detailed_description(patterns, files)
        msg3 = self._format_commit_message(change_type, scope, detailed_desc, breaking)
        if msg3 != msg1:
            suggestions.append(CommitSuggestion(
                message=msg3,
                change_type=change_type,
                scope=scope,
                description=detailed_desc,
                breaking=breaking,
                score=80.0
            ))

        # 按分数排序
        suggestions.sort(key=lambda x: x.score, reverse=True)
        return suggestions

    def _detect_change_type(
        self,
        diff: str,
        patterns: Dict[str, Any],
        files: List[FileChange]
    ) -> ChangeType:
        """检测变更类型"""
        diff_lower = diff.lower()

        # 根据文件类型判断
        if patterns.get("test_files") and not patterns.get("source_files"):
            return ChangeType.TEST

        if patterns.get("doc_files") and not patterns.get("source_files"):
            return ChangeType.DOCS

        if patterns.get("config_files") and len(patterns.get("config_files", [])) == patterns.get("files_changed", 0):
            return ChangeType.CHORE

        # 根据关键词判断
        scores = {ct: 0 for ct in ChangeType}
        for change_type, keywords in self.KEYWORD_PATTERNS.items():
            for keyword in keywords:
                scores[change_type] += diff_lower.count(keyword.lower())

        # 根据代码特征判断
        if re.search(r'\bdef\s+test_|\bit\s*\(|\bdescribe\s*\(', diff_lower):
            scores[ChangeType.TEST] += 3

        if re.search(r'class.*Test|@pytest|@unittest', diff_lower):
            scores[ChangeType.TEST] += 3

        # 返回得分最高的类型
        return max(scores, key=scores.get) if max(scores.values()) > 0 else ChangeType.CHORE

    def _detect_scope(self, files: List[FileChange]) -> Optional[str]:
        """检测作用域"""
        if not files:
            return None

        # 提取共同目录
        paths = [f.path for f in files]
        if len(paths) == 1:
            # 单个文件，使用文件名或父目录
            parts = paths[0].split("/")
            if len(parts) > 1:
                return parts[0]
            return paths[0].split(".")[0] if "." in paths[0] else paths[0]

        # 多个文件，找共同前缀
        common = paths[0]
        for path in paths[1:]:
            while not path.startswith(common):
                common = common.rsplit("/", 1)[0] if "/" in common else ""
                if not common:
                    break

        if common:
            return common.split("/")[0] if "/" in common else common

        # 根据文件类型推断
        extensions = set()
        for f in files:
            if "." in f.path:
                ext = f.path.rsplit(".", 1)[-1]
                extensions.add(ext)

        if len(extensions) == 1:
            ext = list(extensions)[0]
            scope_map = {
                "py": "python",
                "js": "js",
                "ts": "ts",
                "go": "go",
                "java": "java",
                "rs": "rust",
            }
            return scope_map.get(ext)

        return None

    def _generate_description(self, patterns: Dict[str, Any], files: List[FileChange], change_type: ChangeType) -> str:
        """生成描述"""
        descriptions = []

        # 根据变更类型生成基础描述
        type_desc = {
            ChangeType.FEATURE: "add new functionality",
            ChangeType.FIX: "fix issues",
            ChangeType.DOCS: "update documentation",
            ChangeType.STYLE: "improve code style",
            ChangeType.REFACTOR: "refactor code",
            ChangeType.TEST: "add or update tests",
            ChangeType.CHORE: "update dependencies or configuration",
            ChangeType.PERF: "improve performance",
            ChangeType.CI: "update CI/CD configuration",
            ChangeType.BUILD: "update build configuration",
            ChangeType.REVERT: "revert previous changes",
        }

        base_desc = type_desc.get(change_type, "make changes")

        # 添加文件信息
        file_count = patterns.get("files_changed", 0)
        if file_count == 1:
            base_desc += f" to {files[0].path}"
        elif file_count <= 5:
            file_names = [f.path.split("/")[-1] for f in files[:3]]
            base_desc += f" to {', '.join(file_names)}"
            if file_count > 3:
                base_desc += f" and {file_count - 3} more files"
        else:
            base_desc += f" to {file_count} files"

        return base_desc

    def _shorten_description(self, description: str) -> str:
        """缩短描述"""
        # 移除文件列表，保留核心动作
        if " to " in description:
            return description.split(" to ")[0]
        return description

    def _generate_detailed_description(self, patterns: Dict[str, Any], files: List[FileChange]) -> str:
        """生成详细描述"""
        parts = []

        if patterns.get("total_additions", 0) > 0:
            parts.append(f"+{patterns['total_additions']} lines")
        if patterns.get("total_deletions", 0) > 0:
            parts.append(f"-{patterns['total_deletions']} lines")

        file_info = f"{patterns.get('files_changed', 0)} files"
        parts.append(file_info)

        return f"update ({', '.join(parts)})"

    def _is_breaking_change(self, diff: str) -> bool:
        """检测是否为破坏性变更"""
        breaking_patterns = [
            r'BREAKING CHANGE',
            r'@deprecated',
            r'remove.*function',
            r'delete.*method',
            r'rename.*api',
            r'change.*signature',
        ]

        diff_upper = diff.upper()
        for pattern in breaking_patterns:
            if re.search(pattern, diff_upper):
                return True

        return False

    def _format_commit_message(
        self,
        change_type: ChangeType,
        scope: Optional[str],
        description: str,
        breaking: bool
    ) -> str:
        """格式化提交信息"""
        msg = change_type.value

        if scope:
            msg += f"({scope})"

        if breaking:
            msg += "!"

        msg += f": {description}"

        return msg

    def _calculate_quality_score(
        self,
        patterns: Dict[str, Any],
        files: List[FileChange],
        warnings: List[str]
    ) -> float:
        """计算质量评分"""
        score = 100.0

        # 根据警告扣分
        score -= len(warnings) * 5

        # 根据文件数量评分
        file_count = patterns.get("files_changed", 0)
        if file_count <= 5:
            score += 5
        elif file_count > 20:
            score -= 10

        # 根据测试覆盖评分
        if patterns.get("test_files"):
            score += 5

        # 根据文档更新评分
        if patterns.get("doc_files"):
            score += 3

        return max(0, min(100, score))

    def get_quick_suggestion(self) -> Optional[CommitSuggestion]:
        """获取快速建议（用于非交互式场景）"""
        result = self.analyze()
        if result.suggestions:
            return result.suggestions[0]
        return None
