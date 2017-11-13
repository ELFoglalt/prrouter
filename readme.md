# Project Reality Route Exporter
This is a python script for exporting map route images from the game [Project Reality](http://www.realitymod.com/). Repo located at [https://github.com/ELFoglalt/prrouter/](https://github.com/ELFoglalt/prrouter/). You can find the full release [on my drive](https://drive.google.com/open?id=1MqVcgVX-yD5X6YvgdP4VvPCCbjJsQKK7).

> PRrouter v1.0, PR:BF2 v1.20.0


## Usage

The Project Reality Route Exporter utility runs as a command line application. The desired operations are to be specified trough command line arguments. See he built in help (`-h` or `--help`) for more information about how to export specific maps and layouts.

You can use the utility by either running the python script directly (requires Python3+)
```
$ python path/to/prrouter.py -h
```

or in case of the standalone executible, run it from the command line
```
$ path/to/prrouter.exe -h
```

The router uses ANSI escape sequences to format the output, so it is recommended that you use a combaptible command line.


 ## Other
By [ELFoglalt](https://github.com/ELFoglalt/), following the work of [WGPSenshi](https://github.com/WGPSenshi).

The Project Reality Route Exporter is distributed under the Apache License 2.0.