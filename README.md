# mjobs

A little tool to make it easier to inspect LSF jobs.

```shell
usage: mjobs [-h] [-q QUEUE] [-u USER] [-r] [-a] [-d] [-G USER_GROUP] [-g GROUP] [-m HOSTS] [-p] [-e] [-f FILTER] [job_id ...]

bjobs but a bit nicer

positional arguments:
  job_id         Specifies the jobs or job arrays that bjobs displays.

optional arguments:
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
  -e             Add the output file and error file to the table.
  -f FILTER      Filter the jobs using the specified regex on the job name or pending reason.
```

# Installation - bundle the app

Create an executable with [pyinstaller](https://pyinstaller.readthedocs.io).

```shell
$ pyinstaller mjobs/main.py --onefile --clean --name mjobs
$ ./dist/main --help
```

# Download

Get the artifact from github URL
