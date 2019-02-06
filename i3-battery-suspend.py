import i3ipc
import subprocess
import re
import atexit

i3 = i3ipc.Connection()


# Variables

# Get them from xprop WM_CLASS
exclude_class = ["chromium"]


# Function to call for returning containers to normal when exit
def exit_handler():
    for x in i3.get_tree().leaves():
        window = use_xprop(x.window)
        subprocess.Popen(
            ["kill", "-CONT", " {}".format(use_xprop(x.window))], stdout=subprocess.PIPE)
        subprocess.Popen("xprop -id %s -format _NET_WM_WINDOW_OPACITY 32c -set _NET_WM_WINDOW_OPACITY 0xFFFFFFFF" % x.window, stdout=subprocess.PIPE, shell=True)


atexit.register(exit_handler)

# Define a callback to be called when you switch workspaces.

def use_xprop(x):
    """Get property for our x(id)"""
    process = subprocess.Popen(
        ["xprop", "-id", " {}".format(x)], stdout=subprocess.PIPE)
    proc_stdout = process.communicate()[0].strip()

    # id
    _id = re.search('(?:_NET_WM_PID.+? = )(\d+)',
                    str(proc_stdout), re.MULTILINE)

    # Class
    _class = re.search(r'(?:WM_CLASS.+? = )(.+?\\n)',
                       str(proc_stdout), re.MULTILINE)

    if _class.group(1):
        items = _class.group(1).replace('\\n', "").split(",")
        for item in items:
            if any(item.strip().strip('"') in exclude for exclude in exclude_class):
                return None

    return _id.group(1)


def get_all_apps(active=None):
    for x in i3.get_tree().leaves():
        _x_id = use_xprop(x.window)
        _x_active_id = use_xprop(active)

        if _x_id is not None:
            if _x_active_id == _x_id:
                subprocess.Popen("xprop -id %s -format _NET_WM_WINDOW_OPACITY 32c -set _NET_WM_WINDOW_OPACITY 0xFFFFFFFF" % x.window, stdout=subprocess.PIPE, shell=True)
                subprocess.Popen(["kill", "-CONT", " %s" % _x_id], stdout=subprocess.PIPE)
            else:
                subprocess.Popen("xprop -id %s -format _NET_WM_WINDOW_OPACITY 32c -set _NET_WM_WINDOW_OPACITY 0x8FFFFFFF" % x.window, stdout=subprocess.PIPE, shell=True)
                subprocess.Popen(["kill", "-STOP", " %s" % _x_id], stdout=subprocess.PIPE)


def on_window_focus(i3, e):
    focused = i3.get_tree().find_focused()
    get_all_apps(focused.window)


# Subscribe to events
# i3.on('workspace::focus', on_workspace_focus)
i3.on("window::focus", on_window_focus)

i3.main()
