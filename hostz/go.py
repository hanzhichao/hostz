


class GoMixIn:
    def go_clean_mod_cache(self):
        return self.run(f'go clean -modcache')

    def go_mod_tidy(self, path='.'):
        return self.run(f'cd {path} && go mod tidy')

    def go_build(self, path='.'):
        """运行go build"""
        return self.run(f'cd {path} && go build')

