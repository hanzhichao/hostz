import os

from hostz._base_shell import BaseShell


class _Git(BaseShell):
    def git_pull(self, branch=None, reset=True, workspace=None):
        """调用git pull更新代码"""
        cmd = 'git pull'
        if branch is not None:
            cmd = f'git checkout {branch} && {cmd}'
        if reset is True:
            cmd = f'git reset --hard && {cmd}'
        return self.execute(cmd, workspace=workspace)

    def git_checkout(self, branch, workspace=None):
        """调用git checkout 更新分支"""
        return self.execute(f'git stash && git checkout {branch} && git pull', workspace=workspace)

    def get_commit_id(self, short=False, workspace=None):
        """获取当前commit_id"""
        cmd = 'git rev-parse --short HEAD' if short is True else 'git rev-parse HEAD'
        return self.execute(cmd, workspace=workspace)

    def get_branch(self, workspace=None):
        """获取当前分支"""
        return self.execute("git branch | sed -n '/\* /s///p'", workspace=workspace)

    def clone_or_update(self, repo: str, branch: str = 'master', workspace: str = None):
        project_name = repo.split('/')[-1].rstrip('.git')
        if not self.exists(f'{self.workspace}/{project_name}'):
            print(f'[{self.host}]克隆{project_name}')
            result = self.execute(f'cd {self.workspace} && git clone --recursive -b {branch} {repo}')
            assert result is not False, f'克隆{project_name}失败'
            self.host.execute(f'git submodule update --recursive  --init', workspace=workspace)
        else:
            print(f'[{self.host}]更新{project_name}')
            result = self.git_pull(branch, workspace=workspace)
            return result

    def git_stat_commit_lines(self, since: str = '2017-01-01', workspace=None):   # todo fixme
        """按用户统计提交行数"""
        cmd = f'''git log --format='%aN' | sort -u | while read name; do echo -en "$name\\t"; git log --author="$name" \
--since='{since}' --pretty=tformat: --numstat | awk '{{ add += $1; subs += $2; loc += $1 - $2 }} \
END {{ printf "added lines: %s, removed lines: %s, total lines: %s\\n", add, subs, loc }}' -; done
'''
        result = self.execute(cmd, workspace=workspace)
        print(result)
        return [item.split('\t') for item in result.split('\n')]

    def git_stat_commits(self, since: str = '2017-01-01', workspace=None):  # todo fixme
        """按用户统计提交数量"""
        cmd = f'''git log --format='%aN' | sort -u | while read name; do echo -en "$name\t"; \
git log --author="$name" --no-merges --since='%s' |  grep -e 'commit [a-zA-Z0-9]*' | wc -l;done''' % since
        result = self.execute(cmd, workspace=workspace)
        return [item.split('\t') for item in result.split('\n')]
