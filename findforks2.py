#!/usr/bin/python3
import time
import argparse
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request

#import requests_cache

    
def find_forks(remote):
    """
    Query the GitHub API for all forks of a repository.
    """
    resp_json = []

    repo_url = subprocess.run(
        ["git", "remote", "get-url", remote],
        stdout=subprocess.PIPE
    )

    repo_url_stdout = repo_url.stdout.decode()

    (username, project) = parse_git_remote_output(repo_url_stdout)

    for page in range(1,1000):

        datafile = f"data/{username}{project}{page}.json"
        GITHUB_FORK_URL = u"https://api.github.com/repos/{username}/{project}/forks?page={page}"
        if os.path.exists(datafile):
            with open(datafile) as fi:
                data = json.load(fi)
                #print(data)
        else:
            try:
                url = GITHUB_FORK_URL.format(username=username, project=project,page=page)
                print(url)
                time.sleep(3)
                resp = urllib.request.urlopen(url)
                jsond = resp.read().decode("utf8")
                #resp_json = json.loads(jsond)
                if len(jsond) ==0: # empty array
                    raise StopIteration
                with open(datafile,"w") as fo:
                    fo.write(jsond)
        #for fork in resp_json:
        #    print(fork)
        #    yield (fork['owner']['login'], fork['ssh_url'])

            except urllib.error.HTTPError as e:
                if e.code == 404:
                    raise StopIteration
                else:
                    print(e)




def parse_git_remote_output(repo_url):
    """
    Given a repository URL, split it into its component parts.

    convert git@github.com:akumria/all_forks.git to
        service: git@github.com
        username: akumria
        project = all_forks

    convert https://github.com/akumria/all_forks.git to
        service: git@github.com
        username: akumria
        project = all_forks
    """

    if repo_url.startswith("git@github.com"):
        (service, repo) = repo_url.split(":")
        (username, project_git) = repo.split("/")
        project = project_git[:project_git.find(".")]
        return (username, project)

    if repo_url.startswith("http"):
        o = urllib.parse.urlparse(repo_url)
        
        data = o.path.split("/")
        #print("DATA",data)
        #print(data[1:3])
        (username, project_git) = data[1:3]
        # also handle the case where there is no '.git'
        if project_git.find(".") < 0:
            project = project_git
        else:
            project = project_git[:project_git.find(".")]
        return (username, project)


def setup_remote(remote, repository_url):
    """
    Configure a remote with a specific repository.
    """
    print("{}: {}".format(remote, repository_url))
    subprocess.run(["git", "remote", "add", remote, repository_url])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote", help="Which remote to use", default="origin")
    args = parser.parse_args()

    for (remote, repository) in find_forks(args.remote):
        setup_remote(remote, repository)


if __name__ == "__main__":
    main()
