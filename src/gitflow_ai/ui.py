"""
Terminal UI Module
终端UI模块 - 美化终端输出
"""

import sys
from typing import Optional


class TerminalUI:
    """终端UI类"""

    # ANSI颜色代码
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "gray": "\033[90m",
    }

    # 表情符号
    EMOJIS = {
        "rocket": "🚀",
        "check": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️",
        "bulb": "💡",
        "star": "⭐",
        "fire": "🔥",
        "gear": "⚙️",
        "memo": "📝",
        "chart": "📊",
        "branch": "🌿",
        "robot": "🤖",
        "search": "🔍",
        "lock": "🔒",
        "unlock": "🔓",
    }

    def __init__(self, no_color: bool = False):
        self.no_color = no_color or not sys.stdout.isatty()

    def _color(self, text: str, color: str) -> str:
        """添加颜色"""
        if self.no_color:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def _bold(self, text: str) -> str:
        """加粗"""
        if self.no_color:
            return text
        return f"{self.COLORS['bold']}{text}{self.COLORS['reset']}"

    def print(self, text: str = ""):
        """打印文本"""
        print(text)

    def print_header(self, title: str):
        """打印标题"""
        print()
        print(self._bold(self._color(f"╔══════════════════════════════════════╗", "cyan")))
        print(self._bold(self._color(f"║  {title:^34}  ║", "cyan")))
        print(self._bold(self._color(f"╚══════════════════════════════════════╝", "cyan")))
        print()

    def print_section(self, title: str):
        """打印章节标题"""
        print()
        print(self._bold(self._color(f"▶ {title}", "blue")))
        print(self._color("─" * 40, "gray"))

    def print_kv(self, key: str, value: str, value_color: Optional[str] = None):
        """打印键值对"""
        key_str = self._bold(f"{key}:")
        if value_color:
            value_str = self._color(value, value_color)
        else:
            value_str = value
        print(f"  {key_str} {value_str}")

    def print_bullet(self, text: str, color: Optional[str] = None):
        """打印列表项"""
        bullet = "•"
        if color:
            text = self._color(text, color)
        print(f"    {bullet} {text}")

    def print_success(self, message: str):
        """打印成功消息"""
        print(f"  {self.EMOJIS['check']} {self._color(message, 'green')}")

    def print_warning(self, message: str):
        """打印警告消息"""
        print(f"  {self.EMOJIS['warning']} {self._color(message, 'yellow')}")

    def print_error(self, message: str):
        """打印错误消息"""
        print(f"  {self.EMOJIS['error']} {self._color(message, 'red')}", file=sys.stderr)

    def print_info(self, message: str):
        """打印信息消息"""
        print(f"  {self.EMOJIS['info']} {message}")

    def print_code(self, code: str):
        """打印代码块"""
        print()
        lines = code.strip().split("\n")
        max_len = max(len(line) for line in lines) if lines else 0
        print(self._color(f"  ┌{'─' * (max_len + 2)}┐", "gray"))
        for line in lines:
            print(self._color(f"  │ {line:<{max_len}} │", "gray"))
        print(self._color(f"  └{'─' * (max_len + 2)}┘", "gray"))
        print()

    def print_suggestion(self, index: int, message: str, score: float):
        """打印建议"""
        score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        score_str = self._color(f"[{score:.0f}%]", score_color)
        print(f"  {self._bold(str(index))}. {message} {score_str}")

    def print_score(self, score: float):
        """打印评分"""
        bar_length = 20
        filled = int(score / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        if score >= 80:
            color = "green"
            label = "优秀"
        elif score >= 60:
            color = "yellow"
            label = "良好"
        else:
            color = "red"
            label = "需改进"

        print(f"  {self._color(bar, color)} {score:.0f}/100 ({label})")

    def print_risk(self, risk):
        """打印风险信息"""
        level_colors = {
            "low": "green",
            "medium": "yellow",
            "high": "red",
            "unknown": "gray",
        }
        color = level_colors.get(risk.level, "gray")

        level_names = {
            "low": "低风险",
            "medium": "中等风险",
            "high": "高风险",
            "unknown": "未知",
        }

        print(f"  风险等级: {self._color(level_names.get(risk.level, risk.level), color)}")
        print(f"  风险评分: {risk.score:.0f}/100")

        if risk.reasons:
            print()
            print(self._bold("  风险原因:"))
            for reason in risk.reasons:
                print(f"    {self.EMOJIS['warning']} {reason}")

        if risk.recommendations:
            print()
            print(self._bold("  建议措施:"))
            for rec in risk.recommendations:
                print(f"    {self.EMOJIS['bulb']} {rec}")

    def print_strategy(self, strategy):
        """打印策略详情"""
        print(self._bold(f"  {strategy.name}"))
        print(f"  {strategy.description}")
        print()

        print(self._bold("  主分支:"))
        for branch in strategy.main_branches:
            print(f"    {self.EMOJIS['branch']} {branch}")

        print()
        print(self._bold("  分支命名规范:"))
        print(f"    功能分支: {strategy.feature_pattern}")
        if strategy.release_pattern:
            print(f"    发布分支: {strategy.release_pattern}")
        if strategy.hotfix_pattern:
            print(f"    热修复分支: {strategy.hotfix_pattern}")

        print()
        print(self._bold("  优点:"))
        for pro in strategy.pros:
            print(f"    {self.EMOJIS['check']} {pro}")

        print()
        print(self._bold("  缺点:"))
        for con in strategy.cons:
            print(f"    {self.EMOJIS['warning']} {con}")

        print()
        print(self._bold("  适用场景:"))
        for rec in strategy.recommended_for:
            print(f"    {self.EMOJIS['bulb']} {rec}")

    def print_workflow_item(self, item):
        """打印工作流对比项"""
        print()
        print(self._bold(self._color(f"  {item['name']}", "cyan")))
        print(f"  {item['description']}")
        print(f"  复杂度: {item['complexity']}")
        print(f"  适合团队: {item['team_size']}")
        print(f"  部署频率: {item['deployment']}")
