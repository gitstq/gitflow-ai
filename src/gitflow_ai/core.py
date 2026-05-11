"""
GitFlow AI Core Module
核心功能模块 - 零依赖实现
"""

import subprocess
import re
import os
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class ChangeType(Enum):
    """变更类型枚举"""
    FEATURE = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    TEST = "test"
    CHORE = "chore"
    PERF = "perf"
    CI = "ci"
    BUILD = "build"
    REVERT = "revert"


@dataclass
class FileChange:
    """文件变更数据类"""
    path: str
    change_type: str  # added, modified, deleted, renamed
    additions: int = 0
    deletions: int = 0


@dataclass
class CommitSuggestion:
    """提交建议数据类"""
    message: str
    change_type: ChangeType
    scope: Optional[str]
    description: str
    breaking: bool
    score: float  # 质量评分 0-100


class GitFlowCore:
    """GitFlow AI 核心类"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self._check_git_repo()

    def _check_git_repo(self) -> None:
        """检查是否为Git仓库"""
        git_dir = os.path.join(self.repo_path, ".git")
        if not os.path.exists(git_dir):
            raise GitFlowError(f"'{self.repo_path}' 不是一个有效的Git仓库")

    def _run_git(self, args: List[str]) -> Tuple[str, str, int]:
        """运行Git命令"""
        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            return result.stdout, result.stderr, result.returncode
        except FileNotFoundError:
            raise GitFlowError("Git命令未找到，请确保Git已安装并添加到PATH")

    def get_repo_info(self) -> Dict[str, Any]:
        """获取仓库基本信息"""
        stdout, _, code = self._run_git(["remote", "-v"])
        remotes = {}
        if code == 0:
            for line in stdout.strip().split("\n"):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        remotes[parts[0]] = parts[1]

        stdout, _, _ = self._run_git(["branch", "--show-current"])
        current_branch = stdout.strip()

        stdout, _, _ = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        head = stdout.strip()

        stdout, _, _ = self._run_git(["log", "--oneline", "-1"])
        latest_commit = stdout.strip() if stdout.strip() else "No commits yet"

        return {
            "path": self.repo_path,
            "current_branch": current_branch,
            "head": head,
            "latest_commit": latest_commit,
            "remotes": remotes,
        }

    def get_status(self) -> Dict[str, Any]:
        """获取仓库状态"""
        stdout, _, _ = self._run_git(["status", "--porcelain", "-b"])
        lines = stdout.strip().split("\n") if stdout.strip() else []

        branch_info = ""
        staged = []
        unstaged = []
        untracked = []

        for line in lines:
            if line.startswith("##"):
                branch_info = line[3:].strip()
            elif line.startswith("??"):
                untracked.append(line[3:])
            elif line.startswith(" M") or line.startswith(" D"):
                unstaged.append(line[3:])
            elif line.startswith("M ") or line.startswith("A ") or line.startswith("D "):
                staged.append(line[3:])
            elif line.startswith("MM"):
                staged.append(line[3:])
                unstaged.append(line[3:])

        return {
            "branch_info": branch_info,
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked,
            "is_clean": not (staged or unstaged or untracked),
        }

    def get_staged_diff(self) -> str:
        """获取暂存区差异"""
        stdout, _, code = self._run_git(["diff", "--cached"])
        if code != 0:
            return ""
        return stdout

    def get_unstaged_diff(self) -> str:
        """获取未暂存差异"""
        stdout, _, code = self._run_git(["diff"])
        if code != 0:
            return ""
        return stdout

    def get_staged_files(self) -> List[FileChange]:
        """获取暂存区文件列表"""
        stdout, _, _ = self._run_git(["diff", "--cached", "--numstat"])
        files = []

        for line in stdout.strip().split("\n"):
            if line:
                parts = line.split("\t")
                if len(parts) >= 3:
                    try:
                        additions = int(parts[0]) if parts[0] != "-" else 0
                        deletions = int(parts[1]) if parts[1] != "-" else 0
                        path = parts[2]
                        files.append(FileChange(
                            path=path,
                            change_type="modified",
                            additions=additions,
                            deletions=deletions
                        ))
                    except ValueError:
                        continue

        # 获取新增文件
        stdout, _, _ = self._run_git(["diff", "--cached", "--name-status", "--diff-filter=A"])
        for line in stdout.strip().split("\n"):
            if line.startswith("A\t"):
                path = line[2:]
                if not any(f.path == path for f in files):
                    files.append(FileChange(path=path, change_type="added"))

        # 获取删除文件
        stdout, _, _ = self._run_git(["diff", "--cached", "--name-status", "--diff-filter=D"])
        for line in stdout.strip().split("\n"):
            if line.startswith("D\t"):
                path = line[2:]
                if not any(f.path == path for f in files):
                    files.append(FileChange(path=path, change_type="deleted"))

        return files

    def analyze_diff_patterns(self, diff: str) -> Dict[str, Any]:
        """分析差异模式"""
        patterns = {
            "test_files": [],
            "config_files": [],
            "doc_files": [],
            "source_files": [],
            "total_additions": 0,
            "total_deletions": 0,
            "files_changed": 0,
        }

        # 统计文件变更
        file_pattern = re.compile(r'^diff --git a/(.+) b/(.+)$', re.MULTILINE)
        files = file_pattern.findall(diff)
        patterns["files_changed"] = len(files)

        # 统计行数
        addition_pattern = re.compile(r'^\+[^+]', re.MULTILINE)
        deletion_pattern = re.compile(r'^-[^-]', re.MULTILINE)
        patterns["total_additions"] = len(addition_pattern.findall(diff))
        patterns["total_deletions"] = len(deletion_pattern.findall(diff))

        # 分类文件
        for _, filepath in files:
            if any(filepath.endswith(ext) for ext in ['_test.py', '.test.js', '.spec.ts', '_test.go']):
                patterns["test_files"].append(filepath)
            elif any(filepath.endswith(ext) for ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']):
                patterns["config_files"].append(filepath)
            elif any(filepath.endswith(ext) for ext in ['.md', '.rst', '.txt', 'README', 'CHANGELOG']):
                patterns["doc_files"].append(filepath)
            else:
                patterns["source_files"].append(filepath)

        return patterns

    def get_branch_list(self) -> List[Dict[str, str]]:
        """获取分支列表"""
        stdout, _, _ = self._run_git(["branch", "-a", "--format=%(refname:short)|%(upstream:short)|%(upstream:track)"])
        branches = []

        for line in stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                name = parts[0]
                upstream = parts[1] if len(parts) > 1 else ""
                track = parts[2] if len(parts) > 2 else ""

                is_current = name.startswith("* ")
                if is_current:
                    name = name[2:]

                branches.append({
                    "name": name,
                    "is_current": is_current,
                    "upstream": upstream,
                    "track": track,
                })

        return branches

    def get_commit_history(self, count: int = 10) -> List[Dict[str, str]]:
        """获取提交历史"""
        format_str = "%H|%s|%an|%ad|%D"
        stdout, _, _ = self._run_git(["log", f"--format={format_str}", f"-n{count}", "--date=short"])

        commits = []
        for line in stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                if len(parts) >= 4:
                    commits.append({
                        "hash": parts[0][:7],
                        "full_hash": parts[0],
                        "message": parts[1],
                        "author": parts[2],
                        "date": parts[3],
                        "refs": parts[4] if len(parts) > 4 else "",
                    })

        return commits

    def stage_files(self, files: Optional[List[str]] = None) -> bool:
        """暂存文件"""
        if files:
            args = ["add"] + files
        else:
            args = ["add", "."]

        _, stderr, code = self._run_git(args)
        return code == 0

    def commit(self, message: str, allow_empty: bool = False) -> bool:
        """提交更改"""
        args = ["commit", "-m", message]
        if allow_empty:
            args.append("--allow-empty")

        _, stderr, code = self._run_git(args)
        return code == 0

    def push(self, remote: str = "origin", branch: Optional[str] = None) -> Tuple[bool, str]:
        """推送代码"""
        if not branch:
            stdout, _, _ = self._run_git(["branch", "--show-current"])
            branch = stdout.strip()

        args = ["push", remote, branch]
        stdout, stderr, code = self._run_git(args)

        if code == 0:
            return True, stdout
        else:
            return False, stderr


class GitFlowError(Exception):
    """GitFlow AI 自定义异常"""
    pass
