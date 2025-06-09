import sys
import os

def resource_path(relative_path):
    """ 用于 PyInstaller 打包后正确访问资源文件 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)