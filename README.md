![Aster Insights](./assets/aster.png)

# 🧬 Research Workbench Command Line Interface

Research Workbench `rwb` is now available for ORIEN partners on Linux, Mac and Windows platforms. Upon the first run, you will be requested to input your ORIEN credentials, which will be cached securely to make future runs easily accessible, unless you explicitly `rwb logout`.


## Installation

Download the executable for your desired platform from [`releases`](https://github.com/AsterInsights/rwb/releases).

### Linux/Mac

```sh
mv rwb.version.arch /a/path/to/bins/on/your/path
chmod +x /a/path/to/bins/on/your/path/rwb
rwb project list
```

#### For example (Linux):

```sh
mv ~/Downloads/rwb.linux.x64 /usr/local/bin/rwb
chmod +x /usr/local/bin/rwb
rwb project list
```

## Support Scripts
The supporting scripts in the accompanying supporting_scripts.zip file are recommended as a companion to downloading the executable. The Python scripts make it possible to manage downloads and select what will be downloaded. The scripts are revised at times, and contributions to script functionality are gratefully accepted and will be incorporated in future releases. The support scripts require Python 3.7 or above, and permits downloads on multiple threads.
