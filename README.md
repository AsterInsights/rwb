![Aster Insights](./assets/aster.png)

# 🧬 Research Workbench Command Line Interface

`rwb` is available for ORIEN partners on the Linux, Mac and Windows platforms.  Upon first run,
you will be prompted for your ORIEN credentials, which will be cached securely for future runs, unless
you expclitly `rwb logout`


## Installation

Download the executable for your desired platform from [`releases`](https://github.com/AsterInsights/rwb/releases)[]

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