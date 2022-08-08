class SedMixIn:
    def sed_delete(self, match_str, file_path):
        cmd = f"sed -i '/{match_str}/d' {file_path}"
        return self.run(cmd)

    def sed_add(self, match_str, new_str, file_path):
        cmd = rf"sed -i '/{match_str}/a\{new_str}' {file_path}"
        return self.run(cmd)

    def sed_insert(self, match_str, new_str, file_path):
        cmd = rf"sed -i '/{match_str}/i\{new_str}' {file_path}"
        return self.run(cmd)

    def sed_replace(self, match_str, new_str, file_path):
        cmd = f"sed -i 's%{match_str}%{new_str}%g' {file_path}"
        return self.run(cmd)

