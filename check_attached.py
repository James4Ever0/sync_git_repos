import os

scriptBase = os.path.abspath(__file__)
scriptBase = os.path.dirname(scriptBase)

cwd = os.curdir
cwd = os.path.abspath(cwd)


import libtmux

server = libtmux.Server()


sessionName = "double_sync" + cwd.replace("/", "_")

# lock_name = cwd.replace("/", "_") + ".lock"
# lock_path = os.path.join("{}/locks".format(scriptBase), lock_name)

def checkAttached():
    try:
        for session in server.list_sessions():
            if session["session_name"] == sessionName:
                attached = session["session_attached"]
                print("ATTACHED?",attached)
                if attached == "0":
                    os.system("gnome-terminal -- tmux attach -t {}".format(sessionName))
    except: pass
checkAttached()
