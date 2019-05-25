# coding='utf-8'

import os
import re
import subprocess
import click

__version__ = '0.3.1'

WSL_ROOTFS_DIR = os.environ['WSL_DISTRO_ROOTFS_DIR']
if WSL_ROOTFS_DIR and WSL_ROOTFS_DIR.endswith('/'):
    WSL_ROOTFS_DIR = WSL_ROOTFS_DIR[:-1]

win_abs_path_pattern = re.compile(r'^[A-Za-z]:(\\[^:/\\\*\?<>\|]+)*(\\)?$')
win_abs_path_pattern2 = re.compile(r'^[A-Za-z]:(/[^:/\\\*\?<>\|]+)*(/)?$')
win_abs_path_doubledash_pattern = re.compile(
    r'^[A-Za-z]:(\\\\[^:/\\\*\?<>\|]+)*(\\\\)?$'
    )


def is_abs_path(path):
    if path.startswith('/'):
        return True
    if win_abs_path_pattern.match(path):
        return True
    if win_abs_path_pattern2.match(path):
        return True
    if win_abs_path_doubledash_pattern.match(path):
        return True

    return False


def is_unix_path(path):
    if path.startswith('/'):
        return True
    return False


def is_windows_path(path):
    if win_abs_path_pattern.match(path) is not None:
        return True
    if win_abs_path_pattern2.match(path) is not None:
        return True
    if win_abs_path_doubledash_pattern.match(path) is not None:
        return True

    return False


def convert_to_win_path(doubledash_path_option, path, check=True):
    if check:
        if win_abs_path_doubledash_pattern.match(path):
            if doubledash_path_option:
                return path
            else:
                p = path.replace('\\\\', '\\')
                return p
        if win_abs_path_pattern.match(path) and doubledash_path_option:
            p = path.replace('\\', '\\\\')
            return p
        if win_abs_path_pattern2.match(path):
            return path

    if path.startswith('/proc/'):
        raise OSError("%s is not real file or directory" % path)

    p = path
    if not p.startswith('/mnt/'):
        if not WSL_ROOTFS_DIR:
            raise OSError("please define env var WSL_DISTRO_ROOTFS_DIR")

        p = '%s%s' % (WSL_ROOTFS_DIR, p)

    p = p[len('/mnt/'):]
    idx = p.find('/')
    drive = p[:idx]
    p = p[idx:]
    if doubledash_path_option:
        p = p.replace('/', '\\\\')
    else:
        p = p.replace('/', '\\')
    return '%s:%s' % (drive, p)


def convert_to_wsl_path(path, check=True):
    if check:
        if is_unix_path(path):
            return path

    if not WSL_ROOTFS_DIR:
        raise OSError("please define env var WSL_DISTRO_ROOTFS_DIR")

    p = path
    idx = p.find(':')
    drive = p[:idx].lower()
    p = p[idx+1:]
    p = p.replace('\\', '/')
    p = '/mnt/%s%s' % (drive, p)
    if p.startswith(WSL_ROOTFS_DIR):
        p = p[len(WSL_ROOTFS_DIR):]
    return p


# 转换相对路径
def convert_relative_path(path):
    return path.replace('\\', '/')


def get_env(k):
    def inner():
        return os.environ[k]
    return inner


def get_winsys_envvar(k):
    '''
    从 powershell 里的环境变量获取路径
    '''
    return subprocess.check_output(
            'powershell.exe -Command "echo \$%s"' % k,
            shell=True,
            stderr=subprocess.STDOUT,
            encoding='UTF-8',
            text=True
    ).split('\n')[0]


def get_winsys_regenv(k):
    '''
     从注册表里的环境变量获取路径
    '''

    return subprocess.check_output(
            'powershell.exe -Command "& {(get-childitem Env:%s).Value}"' % k,
            shell=True,
            stderr=subprocess.STDOUT,
            encoding='UTF-8',
            text=True
    ).split('\n')[0]


def get_winsys_folder(k):
    '''
    see https://docs.microsoft.com/en-us/dotnet/api/system.environment.specialfolder?view=netframework-4.7.2
    '''
    return subprocess.check_output(
        'powershell.exe -Command "& { [Environment]::GetFolderPath(\\\"%s\\\") }"' % k,
        stderr=subprocess.STDOUT,
        shell=True,
        encoding='UTF-8',
        text=True
        ).split('\n')[0]


winsys_type_path_map = {
    'userprofile': lambda: get_winsys_folder('UserProfile'),
    'desktop': lambda: get_winsys_folder('DESKTOP'),
    'appdata': lambda: get_winsys_folder('ApplicationData'),
    'localappdata': lambda: get_winsys_folder('LocalApplicationData'),
    'temp': lambda: get_winsys_folder('TEMP'),
    'sys': lambda: get_winsys_folder('System'),
    'sysx86': lambda: get_winsys_folder('SystemX86'),
    'windir': lambda: get_winsys_folder('Windows'),
    'startmenu': lambda: get_winsys_folder('StartMenu'),
    'startup': lambda: get_winsys_folder('Startup'),
    'home': lambda: get_winsys_envvar('HOME'),
    'programfiles': lambda: get_winsys_folder('ProgramFiles'),
    'programfilesx86': lambda: get_winsys_folder('ProgramFilesX86'),
    'programdata': lambda: get_winsys_regenv('ProgramData'),
    'allusersprofile': lambda: get_winsys_regenv('ALLUSERSPROFILE')
}


def get_winsys_path(win_path_type):
    v = winsys_type_path_map[win_path_type]
    if not v:
        return None

    if type(v) is str:
        return v
    return v()


@click.command()
@click.option('--version', 'show_version', is_flag=True)
@click.option('-u', 'path_format', flag_value='unix')
@click.option('-w', 'path_format', flag_value='windows')
@click.option('--abs-path', 'abs_path_option', is_flag=True, default=True)
@click.option('-d', '--doubledash-path', 'doubledash_path_option',
              is_flag=True, default=False)
@click.option('--desktop', 'win_path_type', flag_value='desktop', default='')
@click.option('--appdata', 'win_path_type', flag_value='appdata')
@click.option('--localappdata', 'win_path_type', flag_value='localappdata')
@click.option('--temp', 'win_path_type', flag_value='temp')
@click.option('--sysdir', 'win_path_type', flag_value='sys')
@click.option('--sysx86dir', 'win_path_type', flag_value='sysx86')
@click.option('--windir', 'win_path_type', flag_value='windir')
@click.option('--start-menu', 'win_path_type', flag_value='startmenu')
@click.option('--startup', 'win_path_type', flag_value='startup')
@click.option('--home', 'win_path_type', flag_value='home')
@click.option('--program-files', 'win_path_type', flag_value='programfiles')
@click.option('--programfiles', 'win_path_type', flag_value='programfiles')
@click.option('--programfilesx86', 'win_path_type', flag_value='programfilesx86')
@click.option('--allusersprofile', 'win_path_type', flag_value='allusersprofile')
@click.option('--programdata', 'win_path_type', flag_value='programdata')
@click.argument('path', nargs=-1)
def main(show_version, path_format, abs_path_option, doubledash_path_option,
         win_path_type, path):
    if show_version:
        print('version is %s' % __version__)
        return

    p = path
    if win_path_type:
        p = get_winsys_path(win_path_type)
        if not p:
            raise OSError("not support windows path type %s" % win_path_type)
    else:
        if not path:
            raise OSError("not found any path")
        if len(path) > 1:
            raise OSError("only support one path")

        p = path[0]
        is_abs = is_abs_path(p)

        if not is_abs and not abs_path_option:
            print(convert_relative_path(p))
            return
        if not is_abs:
            p = os.path.abspath(p)

    if path_format == 'unix':
        print(convert_to_wsl_path(p))
        return
    elif path_format == 'windows':
        print(convert_to_win_path(doubledash_path_option, p))
        return

    convert_path = ''
    if is_windows_path(p):
        convert_path = convert_to_wsl_path(p, check=False)
    elif is_unix_path(p):
        convert_path = convert_to_win_path(
                doubledash_path_option, p, check=False)

    print(convert_path)


if __name__ == '__main__':
    main()
