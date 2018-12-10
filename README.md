# pywslpath
windows 和 WSL 的路径互相转换，以及获取 windows 下的系统目录

## 安装
使用 setuptools 来安装

```
python3 setup.py install
```

## 用法
因为该脚本支持把 WSL Linux 下的所有路径转成 Windows,
所以要设置 `WSL_ROOTFS_DIR` 环境变量，指向当前 WSL Linux 安装的路径

```
pywslpath [OPTIONS] [PATH]
```

参数
```
-w               :   输出 windows 格式的路径
-d/--doubledash-path   :   双 `\`, 只有使用 -w 参数才有效,
                      这个参数一般在 linux 的 shell 里使用
-u               :   输出 linux 格式的路径
--desktop        :  获取 windows 的 DESKTOP 路径
--appdata        :  获取 windows 的 ApplicationData 路径
--localappdata   : 获取 windows 的 LocalApplicationData 路径
--temp           : 获取 windows 的 TEMP 路径
--sysdir         : 获取 windows 的 System 路径
--windir         : 获取 windows 的 Windows 路径
--start-menu     : 获取 windows 的 StartMenu 路径
--startup        : 获取 windows 的 Startup 路径
--home           : 获取 windows 的当前用户路径
--program-files  : 获取 windows 的 ProgramFiles 路径
```

例子
```
pywslpath -w -d /mnt/c/

pywslpath -w -d test

pywslpath -w -d --localappdata

pywslpath -u c:/Windows
pywslpath -u c:\\Windows
pywslpath -u "c:\Windows"
```

## 使用场景
### 支持使用 windows 路径进行 cd
在 zsh/bash 里定义以下函数
```
function wd(){
	p=`pywslpath -u $1`
	cd $p
}
```

`wd` 函数支持使用 windows 路径进行 cd


### 打开文件
可以在 WSL Linux 下调用 windows 下 的 VSCode/Atom 编辑器打开文件, 在 zsh/bash 里定义以下函数
```
VSCODE_BIN='code'

function vc(){
	p=`pywslpath -w -d $1`
	$VSCODE_BIN -r $p
}
function vcn(){
	p=`pywslpath -w -d $1`
	$VSCODE_BIN -n $p
}


win_local_appdata_winpath=`pywslpath -w -d --localappdata`
ATOM_BIN_WINPATH="$win_local_appdata_winpath\\atom\\atom.exe"
function ac(){
	p=`pywslpath -w -d $1`
	powershell.exe "Start-Process -FilePath \"$ATOM_BIN_WINPATH\" -ArgumentList \"$p\""
}

function acn(){
	p=`pywslpath -w -d $1`
	powershell.exe "Start-Process -FilePath \"$ATOM_BIN_WINPATH\" -ArgumentList \"-n\", \"$p\""
}
```

### 其他
使用 windows 默认的软件打开目录或者文件, 在 zsh/bash 里定义以下函数
```
function open(){
	if [ "$1" = "--help" ];then
		pywslpath $1
		return
	fi
	p=`pywslpath -w -d $1`
	powershell.exe start "\"$p\""
}
```
