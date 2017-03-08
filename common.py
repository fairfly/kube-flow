import os
import argparse
import subprocess

KUBECTL_CMD_PATH = os.environ.get("KUBECTL_CMD_PATH", '/usr/local/bin/kubectl')
KUBETAIL_CMD_PATH = os.environ.get("KUBETAIL_CMD_PATH", '/usr/local/bin/kubetail')


class KService:
    def __init__(self, type, name, age, status):
        self.type = type
        self.name = name
        self.age = age
        self.status = status


def get_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?', default="")
    return parser.parse_args(args)


def get_pods():
    res = []

    pods = subprocess.Popen("%s get pods" % KUBECTL_CMD_PATH, shell=True, stdout=subprocess.PIPE).stdout.read().split(
        '\n')[
           1:-1]
    for pod_str in pods:
        dep_name, _, status, _, age = " ".join(pod_str.split()).split(' ')
        res.append(KService("Pod", dep_name, age, status))
    return res


def get_deployments():
    res = []

    deps = subprocess.Popen("%s get deploy" % KUBECTL_CMD_PATH, shell=True, stdout=subprocess.PIPE).stdout.read().split(
        '\n')[1:-1]
    for dep_str in deps:
        dep_name, _, current, _, _, age = " ".join(dep_str.split()).split(' ')

        res.append(KService("Deploy", dep_name, age, current))
    return res


def get_services():
    res = []
    res += get_pods()
    res += get_deployments()
    return res


def search_key_for_service(service):
    return u' '.join([
        service.name
    ])


def process_and_feedback(wf, wf_cached_data_key, data_func, icon):
    args = get_args(wf.args)
    data = wf.cached_data(wf_cached_data_key, data_func, max_age=60)

    query = args.query.strip()
    if query:
        data = wf.filter(query, data, key=search_key_for_service, min_score=20)

    for d in data:
        wf.add_item(title=d.name,
                    subtitle="%s - Age: %s | Extra: %s" % (d.type, d.age, d.status),
                    arg=d.name,
                    valid=True,
                    icon=icon)

    wf.send_feedback()