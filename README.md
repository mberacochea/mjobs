# mjobs

A little tool to make it easier to inspect (IBM Spectrum LSF)[https://www.ibm.com/products/hpc-workload-management] (or just LSF) and [Slurm](https://slurm.schedmd.com/) jobs.

The program will auto detect (bjobs)[https://www.ibm.com/docs/en/spectrum-lsf/10.1.0?topic=bjobs-options] under (LSF)[https://www.ibm.com/products/hpc-workload-management], or (squeue)[https://slurm.schedmd.com/squeue.html] in [Slurm](https://slurm.schedmd.com/).

## IBM LSF

mjobs doesn't not support all the options of bjobs, only a subset. It also adds a the `-f FILTER`, `--bkill`, `-t` and `-nh` options.

```shell
Usage: mjobs [-h] [-q QUEUE] [-u USER] [-r] [-a] [-d] [-G USER_GROUP] [-g GROUP] [-m HOSTS] [-p] [-e] [-f FILTER] [-t] [-nh] [--bkill] [job_id ...]

bjobs but a bit nicer

Positional Arguments:
  job_id         Specifies the jobs or job arrays that bjobs displays.

Optional Arguments:
  -h, --help     show this help message and exit
  -q QUEUE       Displays jobs in the specified queue
  -u USER        Displays jobs in the specified user
  -r             Displays running jobs.
  -a             Displays information about jobs in all states, including jobs that finished recently.
  -d             Displays information about jobs that finished recently.
  -G USER_GROUP  Displays jobs associated with the specified user group.
  -g GROUP       Displays information about jobs attached to the specified job group.
  -m HOSTS       Displays jobs dispatched to the specified hosts.
  -p             Displays pending jobs, together with the pending reasons that caused each job not to be dispatched during the last dispatch turn.
  -e             Add the execution josts, output file and error file to the table.
  -f FILTER      Filter the jobs using the specified regex on the job name or pending reason.
  -t             No fancy table, a good ol' tsv
  -nh            Don't print the table header, useful to pipe the tsv output
  --bkill        Terminate found or filtered jobs with bkill.

```

### Example

![Alt text](images/mjobs-example.png?raw=true "mjobs example")

## Slurm

mjobs doesn't not support all the options of bjobs, only a subset. It also adds a the `-f FILTER`, `--bkill`, `-t` and `-nh` options.

```shell
Usage: mjobs [-h] [-q QUEUE] [-u USER] [-r] [-a] [-d] [-G USER_GROUP] [-g GROUP] [-m HOSTS] [-p] [-e] [-f FILTER] [-t] [-nh] [--bkill] [job_id ...]

bjobs but a bit nicer

Positional Arguments:
  job_id         Specifies the jobs or job arrays that bjobs displays.

Optional Arguments:
  -h, --help     show this help message and exit
  -q QUEUE       Displays jobs in the specified queue
  -u USER        Displays jobs in the specified user
  -r             Displays running jobs.
  -a             Displays information about jobs in all states, including jobs that finished recently.
  -d             Displays information about jobs that finished recently.
  -G USER_GROUP  Displays jobs associated with the specified user group.
  -g GROUP       Displays information about jobs attached to the specified job group.
  -m HOSTS       Displays jobs dispatched to the specified hosts.
  -p             Displays pending jobs, together with the pending reasons that caused each job not to be dispatched during the last dispatch turn.
  -e             Add the execution josts, output file and error file to the table.
  -f FILTER      Filter the jobs using the specified regex on the job name or pending reason.
  -t             No fancy table, a good ol' tsv
  -nh            Don't print the table header, useful to pipe the tsv output
  --bkill        Terminate found or filtered jobs with bkill.

```

# Installation - bundle the app

Create an executable with [pyinstaller](https://pyinstaller.readthedocs.io).

```shell
$ pyinstaller mjobs/main.py --onefile --clean --name mjobs
$ ./dist/main --help
```

### GH Actions binary

This binary is build the python 3.9 buster docker image. This is done to maintain compatibility with the libc version use at EMBl-EBI. For more information -> https://pyinstaller.org/en/stable/usage.html#making-gnu-linux-apps-forward-compatible


# Download

Get the executable from the releases tab.
