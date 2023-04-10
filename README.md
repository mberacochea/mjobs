# mjobs

A little tool to make it easier to inspect LSF jobs.

<pre><font color="#FF8700">Usage:</font> <font color="#808080">mjobs</font> [<font color="#06989A">-h</font>] [<font color="#06989A">-q</font> <font color="#00AF87">QUEUE</font>] [<font color="#06989A">-u</font> <font color="#00AF87">USER</font>] [<font color="#06989A">-r</font>] [<font color="#06989A">-a</font>] [<font color="#06989A">-d</font>] [<font color="#06989A">-G</font> <font color="#00AF87">USER_GROUP</font>] [<font color="#06989A">-g</font> <font color="#00AF87">GROUP</font>] [<font color="#06989A">-m</font> <font color="#00AF87">HOSTS</font>] [<font color="#06989A">-p</font>] [<font color="#06989A">-e</font>] [<font color="#06989A">-f</font> <font color="#00AF87">FILTER</font>] [<font color="#06989A">-t</font>] [<font color="#06989A">-nh</font>]
             [<font color="#06989A">--bkill</font>]
             <font color="#06989A">[job_id ...]</font>

bjobs but a bit nicer

<font color="#FF8700">Positional Arguments:</font>
  <font color="#06989A">job_id</font>         Specifies the jobs or job arrays that bjobs displays.

<font color="#FF8700">Optional Arguments:</font>
  <font color="#06989A">-h</font>, <font color="#06989A">--help</font>     show this help message and exit
  <font color="#06989A">-q</font> <font color="#00AF87">QUEUE</font>       Displays jobs in the specified queue
  <font color="#06989A">-u</font> <font color="#00AF87">USER</font>        Displays jobs in the specified user
  <font color="#06989A">-r</font>             Displays running jobs.
  <font color="#06989A">-a</font>             Displays information about jobs in all states, including jobs that finished recently.
  <font color="#06989A">-d</font>             Displays information about jobs that finished recently.
  <font color="#06989A">-G</font> <font color="#00AF87">USER_GROUP</font>  Displays jobs associated with the specified user group.
  <font color="#06989A">-g</font> <font color="#00AF87">GROUP</font>       Displays information about jobs attached to the specified job group.
  <font color="#06989A">-m</font> <font color="#00AF87">HOSTS</font>       Displays jobs dispatched to the specified hosts.
  <font color="#06989A">-p</font>             Displays pending jobs, together with the pending reasons that caused each job not to be dispatched during the
                 last dispatch turn.
  <font color="#06989A">-e</font>             Add the execution josts, output file and error file to the table.
  <font color="#06989A">-f</font> <font color="#00AF87">FILTER</font>      Filter the jobs using the specified regex on the job name or pending reason.
  <font color="#06989A">-t</font>             No fancy table, a good ol&apos; tsv
  <font color="#06989A">-nh</font>            Don&apos;t print the table header, useful to pipe the tsv ouput
  <font color="#06989A">--bkill</font>        Run `<b>bkill</b>` on found or filtered jobs.
</pre>

## Example

![Alt text](images/mjobs-example.png?raw=true "mjobs example")

# Installation - bundle the app

Create an executable with [pyinstaller](https://pyinstaller.readthedocs.io).

```shell
$ pyinstaller mjobs/main.py --onefile --clean --name mjobs
$ ./dist/main --help
```

# Download

Get the executable from the releases tab.
