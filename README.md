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

## Best Practices
Molecular downloads necessarily involve large numbers of large files. As the sophistication of sequencing and analytical methods improves, these files will only continue to grow in size and number. Almost all of the projects available for download include terabytes of genomic files. The policies and practices of our partners and customers differ in how fast these files can be downloaded, and how many can be downloaded. We have provided options in the support scripts to support downloading single folders instead of entire projects, and also to control the speed of downloads by defining the number of threads for simultaneous downloads. We recommend using both these options. We provide a variety of files in our release and intermember projects - sometimes it is not necessary to download everything. Here is an example of a command line using the support scripts that use these options. It supports downloading only a single release folder and uses 2 threads to do the download. It is suggested to consult the Readme.md file with the support scripts in the latest release for more details.
```python
python3 download_project.py --project-id <your project id> --exec ./rwb.osx.x64 --workers 2 --include /Avatar_MolecularData_hg38/2024_05_31/Whole_Exome/tumor_vcfs
```
