from hostz._base_shell import BaseShell


class _Git(BaseShell):
    def git_pull(self, project_path=None):
        """调用git pull更新代码"""
        project_path = project_path or f'{self.workspace}/chainmaker-go'
        self.execute(f'cd {project_path} && git pull')

    def git_checkout(self, branch, project_path):
        """调用git checkout 更新分支"""
        self.execute(f'cd {project_path} && git stash && git checkout {branch} && git pull')

    def get_commit_id(self, short=True):
        """获取当前commit_id"""
        cmd = 'git rev-parse --short HEAD' if short is True else 'git rev-parse HEAD'
        return self.execute(f'cd {self.workspace}/chainmaker-go && {cmd}')

    def get_branch(self):
        """获取当前分支"""
        return self.execute("git branch | sed -n '/\* /s///p'")

    def clone_or_update(self, repo, branch='master'):
        project_name = repo.split('/')[-1].rstrip('.git')
        if not self.exists(f'{self.workspace}/{project_name}'):
            print(f'[{self.host}]克隆{project_name}')
            result = self.execute(f'cd {self.workspace} && git clone --recursive -b {branch} {repo}')
            assert result is not False, f'克隆{project_name}失败'
            self.host.run(f'cd {self.workspace} && git submodule update --recursive  --init')
        else:
            print(f'[{self.host}]更新{project_name}')
            result = self.execute(
                f'cd {self.workspace}/{project_name} && git reset --hard && git checkout {branch} && git pull')
            return result
