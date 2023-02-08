from hostz._base_shell import BaseShell


class _Sed(BaseShell):
    def sed_delete(self, match_str, file_path, after_line_cnt: int = None):
        match_str = match_str.replace('/', '\/')
        if after_line_cnt is None:
            cmd = f"sed -i '/{match_str}/d' {file_path}"
        else:
            cmd = f"sed -i '/{match_str}/,+{after_line_cnt}d' {file_path}"
        return self.execute(cmd)

    def sed_add(self, match_str, new_str, file_path):
        cmd = rf"sed -i '/{match_str}/a\{new_str}' {file_path}"
        return self.execute(cmd)

    def sed_insert(self, match_str, new_str, file_path):
        cmd = rf"sed -i '/{match_str}/i\{new_str}' {file_path}"
        return self.execute(cmd)

    def sed_replace(self, match_str, new_str, file_path):
        cmd = f"sed -i 's%{match_str}%{new_str}%g' {file_path}"
        return self.execute(cmd)
