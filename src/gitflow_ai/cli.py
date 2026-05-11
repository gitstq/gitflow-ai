"""
Command Line Interface
命令行界面 - 主入口模块
"""

import sys
import os
import argparse
from typing import Optional, List

from .core import GitFlowCore, GitFlowError
from .analyzer import CommitAnalyzer
from .advisor import BranchAdvisor, WorkflowType
from .ai_backend import AIBackendManager
from .ui import TerminalUI


def create_parser() -> argparse.ArgumentParser:
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        prog="gitflow",
        description="🚀 GitFlow AI - AI驱动的终端Git工作流智能助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  gitflow status              # 查看仓库状态
  gitflow suggest             # 获取提交建议
  gitflow commit              # 智能提交（分析+生成信息+提交）
  gitflow workflow            # 查看分支策略建议
  gitflow ai-commit           # 使用AI生成提交信息

更多信息: https://github.com/yourusername/gitflow-ai
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    parser.add_argument(
        "-C", "--directory",
        help="指定Git仓库目录",
        default="."
    )

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="禁用彩色输出"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # status 命令
    status_parser = subparsers.add_parser(
        "status",
        aliases=["st"],
        help="查看详细的仓库状态"
    )

    # suggest 命令
    suggest_parser = subparsers.add_parser(
        "suggest",
        aliases=["sg"],
        help="分析暂存区并生成提交建议"
    )
    suggest_parser.add_argument(
        "--ai",
        action="store_true",
        help="使用AI生成提交信息"
    )

    # commit 命令
    commit_parser = subparsers.add_parser(
        "commit",
        aliases=["cm"],
        help="智能提交：分析、生成信息并提交"
    )
    commit_parser.add_argument(
        "-m", "--message",
        help="手动指定提交信息"
    )
    commit_parser.add_argument(
        "--ai",
        action="store_true",
        help="使用AI生成提交信息"
    )
    commit_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="自动确认，不提示"
    )

    # ai-commit 命令
    ai_commit_parser = subparsers.add_parser(
        "ai-commit",
        aliases=["aic"],
        help="使用AI生成提交信息并提交"
    )
    ai_commit_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="自动确认，不提示"
    )

    # workflow 命令
    workflow_parser = subparsers.add_parser(
        "workflow",
        aliases=["wf"],
        help="查看分支策略建议和工作流推荐"
    )
    workflow_parser.add_argument(
        "--detect",
        action="store_true",
        help="检测当前使用的工作流"
    )
    workflow_parser.add_argument(
        "--compare",
        action="store_true",
        help="对比不同工作流"
    )

    # branch 命令
    branch_parser = subparsers.add_parser(
        "branch",
        aliases=["br"],
        help="分支相关操作"
    )
    branch_parser.add_argument(
        "--suggest-name",
        metavar="DESCRIPTION",
        help="根据功能描述建议分支名"
    )
    branch_parser.add_argument(
        "--risk",
        action="store_true",
        help="分析冲突风险"
    )

    # analyze 命令
    analyze_parser = subparsers.add_parser(
        "analyze",
        aliases=["an"],
        help="深度分析仓库状态"
    )

    # config 命令
    config_parser = subparsers.add_parser(
        "config",
        help="配置管理"
    )
    config_parser.add_argument(
        "--show",
        action="store_true",
        help="显示当前配置"
    )
    config_parser.add_argument(
        "--set",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="设置配置项"
    )

    # init 命令
    init_parser = subparsers.add_parser(
        "init",
        help="初始化GitFlow AI配置"
    )

    return parser


def cmd_status(core: GitFlowCore, ui: TerminalUI, args) -> int:
    """status命令"""
    try:
        repo_info = core.get_repo_info()
        status = core.get_status()

        ui.print_header("📊 仓库状态")

        ui.print_section("仓库信息")
        ui.print_kv("路径", repo_info["path"])
        ui.print_kv("当前分支", repo_info["current_branch"])
        ui.print_kv("最新提交", repo_info["latest_commit"][:60])

        if repo_info["remotes"]:
            ui.print_section("远程仓库")
            for name, url in repo_info["remotes"].items():
                ui.print_kv(name, url)

        ui.print_section("工作区状态")
        if status["is_clean"]:
            ui.print_success("工作区干净，没有待处理的变更")
        else:
            if status["staged"]:
                ui.print_info(f"已暂存: {len(status['staged'])} 个文件")
                for f in status["staged"][:5]:
                    ui.print_bullet(f, "green")
                if len(status["staged"]) > 5:
                    ui.print_bullet(f"... 还有 {len(status['staged']) - 5} 个文件", "gray")

            if status["unstaged"]:
                ui.print_info(f"\n未暂存: {len(status['unstaged'])} 个文件")
                for f in status["unstaged"][:5]:
                    ui.print_bullet(f, "yellow")
                if len(status["unstaged"]) > 5:
                    ui.print_bullet(f"... 还有 {len(status['unstaged']) - 5} 个文件", "gray")

            if status["untracked"]:
                ui.print_info(f"\n未跟踪: {len(status['untracked'])} 个文件")
                for f in status["untracked"][:5]:
                    ui.print_bullet(f, "red")
                if len(status["untracked"]) > 5:
                    ui.print_bullet(f"... 还有 {len(status['untracked']) - 5} 个文件", "gray")

        return 0
    except GitFlowError as e:
        ui.print_error(str(e))
        return 1


def cmd_suggest(core: GitFlowCore, ui: TerminalUI, args) -> int:
    """suggest命令"""
    try:
        analyzer = CommitAnalyzer(core)

        ui.print_header("🤖 提交建议分析")

        # 检查暂存区
        status = core.get_status()
        if not status["staged"]:
            ui.print_warning("暂存区为空，请先使用 'git add' 添加文件")
            return 1

        # 执行分析
        result = analyzer.analyze()

        # 显示分析结果
        ui.print_section("📈 变更统计")
        patterns = result.patterns
        ui.print_kv("变更文件", str(patterns.get("files_changed", 0)))
        ui.print_kv("新增行数", f"+{patterns.get('total_additions', 0)}", "green")
        ui.print_kv("删除行数", f"-{patterns.get('total_deletions', 0)}", "red")

        # 显示文件分类
        if patterns.get("source_files"):
            ui.print_info(f"\n源代码文件: {len(patterns['source_files'])} 个")
        if patterns.get("test_files"):
            ui.print_info(f"测试文件: {len(patterns['test_files'])} 个")
        if patterns.get("doc_files"):
            ui.print_info(f"文档文件: {len(patterns['doc_files'])} 个")
        if patterns.get("config_files"):
            ui.print_info(f"配置文件: {len(patterns['config_files'])} 个")

        # 显示警告
        if result.warnings:
            ui.print_section("⚠️  警告")
            for warning in result.warnings:
                ui.print_warning(warning)

        # 显示建议
        if result.recommendations:
            ui.print_section("💡 建议")
            for rec in result.recommendations:
                ui.print_info(rec)

        # 显示提交建议
        ui.print_section("📝 提交信息建议")
        for i, suggestion in enumerate(result.suggestions[:3], 1):
            ui.print_suggestion(i, suggestion.message, suggestion.score)

        # 质量评分
        ui.print_section("📊 质量评分")
        ui.print_score(result.quality_score)

        # 如果需要AI生成
        if args.ai:
            ui.print_section("🤖 AI生成")
            manager = AIBackendManager()
            available = manager.get_available_backends()

            if not available:
                ui.print_warning("没有可用的AI后端，请配置API密钥或启动Ollama")
                ui.print_info("支持的后端: OpenAI, Anthropic, DeepSeek, Ollama")
            else:
                ui.print_info(f"检测到 {len(available)} 个可用后端")
                diff = core.get_staged_diff()
                ai_message = manager.generate_with_fallback(diff, patterns)

                if ai_message:
                    ui.print_success("AI生成的提交信息:")
                    ui.print_code(ai_message)
                else:
                    ui.print_error("AI生成失败，请检查配置")

        return 0
    except GitFlowError as e:
        ui.print_error(str(e))
        return 1


def cmd_commit(core: GitFlowCore, ui: TerminalUI, args) -> int:
    """commit命令"""
    try:
        status = core.get_status()
        if not status["staged"]:
            ui.print_warning("暂存区为空，请先使用 'git add' 添加文件")
            return 1

        # 如果手动指定了消息
        if args.message:
            message = args.message
        else:
            # 生成建议
            analyzer = CommitAnalyzer(core)
            suggestion = analyzer.get_quick_suggestion()

            if suggestion:
                message = suggestion.message
            else:
                message = "chore: update files"

            # 如果需要AI生成
            if args.ai:
                manager = AIBackendManager()
                diff = core.get_staged_diff()
                patterns = analyzer.core.analyze_diff_patterns(diff)
                ai_message = manager.generate_with_fallback(diff, patterns)
                if ai_message:
                    message = ai_message

            # 如果不是自动确认，询问用户
            if not args.yes:
                ui.print_info(f"建议的提交信息: {message}")
                response = input("是否使用此提交信息? [Y/n/edit]: ").strip().lower()
                if response == "n":
                    ui.print_info("已取消提交")
                    return 0
                elif response == "edit":
                    message = input("请输入提交信息: ").strip()

        # 执行提交
        if core.commit(message):
            ui.print_success(f"✅ 提交成功: {message}")
            return 0
        else:
            ui.print_error("❌ 提交失败")
            return 1

    except GitFlowError as e:
        ui.print_error(str(e))
        return 1


def cmd_ai_commit(core: GitFlowCore, ui: TerminalUI, args) -> int:
    """ai-commit命令"""
    args.ai = True
    return cmd_commit(core, ui, args)


def cmd_workflow(core: GitFlowCore, ui: TerminalUI, args) -> int:
    """workflow命令"""
    try:
        advisor = BranchAdvisor(core)

        ui.print_header("🌿 分支工作流顾问")

        if args.compare:
            ui.print_section("工作流对比")
            comparison = advisor.get_workflow_comparison()
            for item in comparison:
                ui.print_workflow_item(item)
            return 0

        # 检测当前工作流
        detected, confidence = advisor.detect_current_workflow()
        ui.print_section("当前工作流检测")
        ui.print_kv("检测到", detected.value)
        ui.print_kv("置信度", f"{confidence:.1f}%")

        # 推荐工作流
        recommended, reasons = advisor.recommend_workflow()
        ui.print_section("💡 推荐工作流")
        ui.print_kv("推荐", recommended.value)
        ui.print_info("推荐理由:")
        for reason in reasons:
            ui.print_bullet(reason)

        # 显示策略详情
        if args.detect or detected != recommended:
            ui.print_section("📋 策略详情")
            strategy = advisor.get_strategy_details(recommended)
            ui.print_strategy(strategy)

        return 0
    except GitFlowError as e:
        ui.print_error(str(e))
        return 1


def cmd_branch(core: GitFlowCore, ui: TerminalUI, args) -> int:
    """branch命令"""
    try:
        advisor = BranchAdvisor(core)

        if args.suggest_name:
            ui.print_header("🌿 分支名建议")
            suggestions = advisor.suggest_branch_name(args.suggest_name)
            ui.print_info(f"功能描述: {args.suggest_name}")
            ui.print_info("建议的分支名:")
            for i, name in enumerate(suggestions, 1):
                ui.print_bullet(f"{name}", "cyan")
            return 0

        if args.risk:
            ui.print_header("⚠️  冲突风险分析")
            risk = advisor.analyze_conflict_risk()
            ui.print_risk(risk)
            return 0

        # 默认显示分支列表
        ui.print_header("🌿 分支列表")
        branches = core.get_branch_list()
        for branch in branches:
            prefix = "* " if branch["is_current"] else "  "
            name = branch["name"]
            if branch["is_current"]:
                ui.print_bullet(f"{prefix}{name}", "green")
            else:
                ui.print_bullet(f"{prefix}{name}")

        return 0
    except GitFlowError as e:
        ui.print_error(str(e))
        return 1


def cmd_analyze(core: GitFlowCore, ui: TerminalUI, args) -> int:
    """analyze命令"""
    try:
        ui.print_header("🔍 深度仓库分析")

        # 仓库信息
        repo_info = core.get_repo_info()
        ui.print_section("仓库概览")
        ui.print_kv("路径", repo_info["path"])
        ui.print_kv("当前分支", repo_info["current_branch"])

        # 提交历史分析
        commits = core.get_commit_history(20)
        if commits:
            ui.print_section("📊 近期提交统计")
            authors = {}
            for commit in commits:
                author = commit["author"]
                authors[author] = authors.get(author, 0) + 1

            ui.print_info("提交者分布:")
            for author, count in sorted(authors.items(), key=lambda x: -x[1]):
                ui.print_bullet(f"{author}: {count} 次提交")

        # 分支分析
        branches = core.get_branch_list()
        ui.print_section("🌿 分支统计")
        local_branches = [b for b in branches if not b["name"].startswith("remotes/")]
        remote_branches = [b for b in branches if b["name"].startswith("remotes/")]
        ui.print_kv("本地分支", str(len(local_branches)))
        ui.print_kv("远程分支", str(len(remote_branches)))

        # 工作流建议
        advisor = BranchAdvisor(core)
        detected, _ = advisor.detect_current_workflow()
        recommended, _ = advisor.recommend_workflow()
        ui.print_section("💡 工作流分析")
        ui.print_kv("当前工作流", detected.value)
        ui.print_kv("推荐工作流", recommended.value)

        return 0
    except GitFlowError as e:
        ui.print_error(str(e))
        return 1


def cmd_init(core: GitFlowCore, ui: TerminalUI, args) -> int:
    """init命令"""
    ui.print_header("🚀 初始化 GitFlow AI")

    config_dir = os.path.expanduser("~/.config/gitflow-ai")
    os.makedirs(config_dir, exist_ok=True)

    ui.print_success(f"配置目录已创建: {config_dir}")
    ui.print_info("请设置以下环境变量以启用AI功能:")
    ui.print_code("""export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
export DEEPSEEK_API_KEY="your-key-here"
# 或使用本地Ollama（无需API Key）""")

    ui.print_info("\n快速开始:")
    ui.print_bullet("gitflow status    - 查看仓库状态")
    ui.print_bullet("gitflow suggest   - 获取提交建议")
    ui.print_bullet("gitflow workflow  - 查看工作流建议")

    return 0


def main(args: Optional[List[str]] = None) -> int:
    """主入口函数"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # 创建UI
    ui = TerminalUI(no_color=parsed_args.no_color)

    # 如果没有命令，显示帮助
    if not parsed_args.command:
        parser.print_help()
        return 0

    # 初始化核心（init命令除外）
    if parsed_args.command != "init":
        try:
            core = GitFlowCore(parsed_args.directory)
        except GitFlowError as e:
            ui.print_error(str(e))
            return 1
    else:
        core = None

    # 路由到对应命令
    commands = {
        "status": cmd_status,
        "st": cmd_status,
        "suggest": cmd_suggest,
        "sg": cmd_suggest,
        "commit": cmd_commit,
        "cm": cmd_commit,
        "ai-commit": cmd_ai_commit,
        "aic": cmd_ai_commit,
        "workflow": cmd_workflow,
        "wf": cmd_workflow,
        "branch": cmd_branch,
        "br": cmd_branch,
        "analyze": cmd_analyze,
        "an": cmd_analyze,
        "init": cmd_init,
    }

    cmd_func = commands.get(parsed_args.command)
    if cmd_func:
        return cmd_func(core, ui, parsed_args)
    else:
        ui.print_error(f"未知命令: {parsed_args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
