


class DockerMixIn:
    def get_container_ids(self, keyword):
        cmd = f"docker ps | grep {keyword} | awk '{{print $1}}'"
        return self.run(cmd)

    def docker_stop(self, container_id: str = None, keyword=None):
        if container_id:
            result = self.run("docker stop %s" % container_id)
        elif keyword:
            result = self.run(f"docker stop `docker ps | grep {keyword} | awk '{{print $1}}'`")
        return result

    def docker_start(self, container_id: str):
        result = self.run("docker start %s" % container_id)
        print(result)

    def docker_restart(self, container_id: str):
        result = self.run("docker restart %s" % container_id)
        print(result)


