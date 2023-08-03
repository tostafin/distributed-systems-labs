import subprocess

import kazoo.exceptions
from kazoo.client import KazooClient

zk = KazooClient(hosts="127.0.0.1:2183")  # 2181, 2182 reserved for zkCli

pid = -1


def create_z_znode():
    if not zk.exists("/z"):
        zk.create("/z")
    else:
        print("/z already exists.")


def delete_z_znode():
    if zk.exists("/z"):
        zk.delete("/z", recursive=True)
    else:
        print("/z doesn't exist.")


def create_znode_child(child_name):
    if zk.exists("/z"):
        zk.create(f"/z/{child_name}", makepath=True)
    else:
        print("/z doesn't exist yet.")


def print_all_znodes(curr_znode="/z"):
    if zk.exists(curr_znode):
        print(curr_znode)
    try:
        if zk.get_children(curr_znode):
            for child in zk.get_children(curr_znode):
                print_all_znodes(f"{curr_znode}/{child}")
    except kazoo.exceptions.KazooException:
        print("No children of /z exist.")


def watch_create_z_znode(event):
    global pid
    pid = subprocess.Popen(["mspaint"])
    if zk.exists("/z"):
        try:
            zk.get_children("/z", watch=watch_create_znode_child)
        except kazoo.exceptions.KazooException:
            pass
    zk.exists("/z", watch=watch_delete_z_znode)


def watch_delete_z_znode(event):
    global pid
    pid.terminate()
    zk.exists("/z", watch=watch_create_z_znode)


def watch_create_znode_child(event):
    if zk.exists("/z"):
        try:
            print(f"Number of children: {len(zk.get_children('/z'))}")
            zk.get_children("/z", watch=watch_create_znode_child)
        except kazoo.exceptions.KazooException:
            pass


def get_action(actions):
    create_child_idx = -1
    for i, a in enumerate(actions):
        print(f"{i}) {a.__name__}")
        if a.__name__.endswith("child"):
            create_child_idx = i

    print(f"{len(actions)}) exit")

    while True:
        action = input("Pick one of the actions: ")
        try:
            action = int(action)
            if action == len(actions):  # exit program
                return None, None
            if not 0 <= action < len(actions):
                raise ValueError()
        except ValueError:
            print(f"You must pick a number between 0 and {len(actions) - 1}")
            continue

        if action == create_child_idx:
            child_name = input("Input child name: ")
            return actions[action], child_name
        return actions[action], None


def main():
    actions = [
        create_z_znode,
        delete_z_znode,
        create_znode_child,
        print_all_znodes,
    ]
    zk.start()

    if zk.exists("/z"):
        zk.delete("/z", recursive=True)

    zk.exists("/z", watch=watch_create_z_znode)
    while True:
        action, child_name = get_action(actions)
        if action is None and child_name is None:
            break
        if child_name:
            action(child_name)
        else:
            action()

    zk.stop()


if __name__ == "__main__":
    main()
