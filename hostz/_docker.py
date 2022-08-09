from hostz._base_shell import BaseShell


class _Docker(BaseShell):
    def get_container_ids(self, keyword):
        cmd = f"docker ps | grep {keyword} | awk '{{print $1}}'"
        return self.execute(cmd)

    def docker_stop(self, container_id: str = None, keyword=None):
        if container_id:
            result = self.execute("docker stop %s" % container_id)
        elif keyword:
            result = self.execute(f"docker stop `docker ps | grep {keyword} | awk '{{print $1}}'`")
        return result

    def docker_start(self, container_id: str):
        result = self.execute("docker start %s" % container_id)
        print(result)

    def docker_restart(self, container_id: str):
        result = self.execute("docker restart %s" % container_id)
        print(result)


