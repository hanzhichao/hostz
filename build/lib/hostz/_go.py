from hostz._base_shell import BaseShell


class _Go(BaseShell):
    def go_clean_mod_cache(self):
        return self.execute(f'go clean -modcache')

    def go_mod_tidy(self, path='.'):
        return self.execute(f'cd {path} && go mod tidy')

    def go_build(self, path='.'):
        """运行go build"""
        return self.execute(f'cd {path} && go build')

