# mjobs

A little tool to make it easier to inspect (IBM Spectrum LSF)[https://www.ibm.com/products/hpc-workload-management] (or just LSF) and [Slurm](https://slurm.schedmd.com/) jobs.

The program will auto detect [bjobs](https://www.ibm.com/docs/en/spectrum-lsf/10.1.0?topic=bjobs-options) under [LSF](https://www.ibm.com/products/hpc-workload-management), or [squeue][https://slurm.schedmd.com/squeue.html] in [Slurm](https://slurm.schedmd.com/).

## IBM LSF

mjobs doesn't not support all the options of bjobs, only a subset. It also adds a the `-f FILTER`, `--bkill`, `-ts` and `-nh` options.

<pre>[mbc@codon-login-02 ~]$ ./mjobs -h
<font color="#FF8700">Usage:</font> <font color="#808080">mjobs</font> [<font color="#05979A">-h</font>] [<font color="#05979A">-f</font> <font color="#00AF87">FILTER</font>] [<font color="#05979A">-ts</font>] [<font color="#05979A">-nh</font>] [<font color="#05979A">-q</font> <font color="#00AF87">QUEUE</font>] [<font color="#05979A">-u</font> <font color="#00AF87">USER</font>] [<font color="#05979A">-r</font>] [<font color="#05979A">-a</font>] [<font color="#05979A">-d</font>] [<font color="#05979A">-G</font> <font color="#00AF87">USER_GROUP</font>] [<font color="#05979A">-g</font> <font color="#00AF87">GROUP</font>] [<font color="#05979A">-m</font> <font color="#00AF87">HOSTS</font>] [<font color="#05979A">-p</font>] [<font color="#05979A">-e</font>] [<font color="#05979A">--bkill</font>] [<font color="#05979A">job_id</font> ...]

Just like bjobs but a bit nicer

<font color="#FF8700">Positional Arguments:</font>
  <font color="#05979A">job_id</font>         Specifies the jobs or job arrays that bjobs displays.

<font color="#FF8700">Optional Arguments:</font>
  <font color="#05979A">-h</font>, <font color="#05979A">--help</font>     show this help message and exit
  <font color="#05979A">-f</font> <font color="#00AF87">FILTER</font>      Filter the jobs using the specified regex on the job name or pending reason.
  <font color="#05979A">-ts</font>, <font color="#05979A">--tsv</font>     No fancy table, a good ol&apos; tsv
  <font color="#05979A">-nh</font>            Don&apos;t print the table header, useful to pipe the tsv output
  <font color="#05979A">-q</font> <font color="#00AF87">QUEUE</font>       Displays jobs in the specified queue
  <font color="#05979A">-u</font> <font color="#00AF87">USER</font>        Displays jobs in the specified user
  <font color="#05979A">-r</font>             Displays running jobs.
  <font color="#05979A">-a</font>             Displays information about jobs in all states, including jobs that finished recently.
  <font color="#05979A">-d</font>             Displays information about jobs that finished recently.
  <font color="#05979A">-G</font> <font color="#00AF87">USER_GROUP</font>  Displays jobs associated with the specified user group.
  <font color="#05979A">-g</font> <font color="#00AF87">GROUP</font>       Displays information about jobs attached to the specified job group.
  <font color="#05979A">-m</font> <font color="#00AF87">HOSTS</font>       Displays jobs dispatched to the specified hosts.
  <font color="#05979A">-p</font>             Displays pending jobs, together with the pending reasons that caused each job not to be dispatched during the last dispatch turn.
  <font color="#05979A">-e</font>             Add the execution hosts, output file and error file to the table.
  <font color="#05979A">--bkill</font>        Terminate found or filtered jobs with bkill.</pre>

### Example

<pre>[mbc@codon-login-02 ~]$ mjobs -u emgpr_wgs -f SRR12480298_mgnify_analysis
<i>                                                                LSF jobs for emgpr_wgs                                                                 </i>
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃<b>    JobId </b>┃<b> Status </b>┃<b> JobName                     </b>┃<b> JobGroup </b>┃<b> User      </b>┃<b> Queue      </b>┃<b> Submit Time  </b>┃<b> Start Time   </b>┃<b> Finish Time    </b>┃<b> Pending reason </b>┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 87346050 │ <font color="#89E234"><b>RUN   </b></font> │ <font color="#EF2828"><b>SRR12480298_mgnify_analysis</b></font> │   ----   │ emgpr_wgs │ production │ Feb 25 08:00 │ Feb 25 08:03 │ Feb 28 08:03 L │      ----      │
└──────────┴────────┴─────────────────────────────┴──────────┴───────────┴────────────┴──────────────┴──────────────┴────────────────┴────────────────┘
</pre>

## Slurm

mjobs doesn't not support all the options of squeue, only a subset. It also adds a the `-f FILTER`, `-ts` and `-nh` options.

<pre>[mbc@codon-slurm-login-01 ~]$ ./mjobs -h
<font color="#FF8700">Usage:</font> <font color="#808080">mjobs</font> [<font color="#05979A">-h</font>] [<font color="#05979A">-f</font> <font color="#00AF87">FILTER</font>] [<font color="#05979A">-ts</font>] [<font color="#05979A">-nh</font>] [<font color="#05979A">-p</font> <font color="#00AF87">PARTITION</font>] [<font color="#05979A">-u</font> <font color="#00AF87">USER</font>]
             [<font color="#05979A">-t</font> <font color="#00AF87">{pending,running,suspended,completed,cancelled,failed,timeout,node_fail,preempted,boot_fail,deadline,out_of_memory,completing,configuring,resizing,resv_del_hold,requeued,requeue_fed,requeue_hold,revoked,signaling,special_exit,stage_out,stopped} [{pending,running,suspended,completed,cancelled,failed,timeout,node_fail,preempted,boot_fail,deadline,out_of_memory,completing,configuring,resizing,resv_del_hold,requeued,requeue_fed,requeue_hold,revoked,signaling,special_exit,stage_out,stopped} ...]</font>]
             [<font color="#05979A">-w</font> <font color="#00AF87">NODELIST [NODELIST ...]</font>] [<font color="#05979A">-e</font>]
             [<font color="#05979A">job_id</font> ...]

Just like squeue but a bit nicer

<font color="#FF8700">Positional Arguments:</font>
  <font color="#05979A">job_id</font>                Specifies the jobs or job arrays that squeue displays.

<font color="#FF8700">Optional Arguments:</font>
  <font color="#05979A">-h</font>, <font color="#05979A">--help</font>            show this help message and exit
  <font color="#05979A">-f</font> <font color="#00AF87">FILTER</font>             Filter the jobs using the specified regex on the job name or pending reason.
  <font color="#05979A">-ts</font>, <font color="#05979A">--tsv</font>            No fancy table, a good ol&apos; tsv
  <font color="#05979A">-nh</font>                   Don&apos;t print the table header, useful to pipe the tsv output
  <font color="#05979A">-p</font>, <font color="#05979A">--partition</font> <font color="#00AF87">PARTITION</font>
                        Specify the partitions of the jobs or steps to view. Accepts a comma separated list of partition names.
  <font color="#05979A">-u</font>, <font color="#05979A">--user</font> <font color="#00AF87">USER</font>       Request jobs or job steps from a comma separated list of users. The list can consist of user names or user id numbers. Performance of the command can be measurably improved for systems with large numbers of jobs when a
                        single user is specified.
  <font color="#05979A">-t</font>, <font color="#05979A">--states</font> <font color="#00AF87">{pending,running,suspended,completed,cancelled,failed,timeout,node_fail,preempted,boot_fail,deadline,out_of_memory,completing,configuring,resizing,resv_del_hold,requeued,requeue_fed,requeue_hold,revoked,signaling,special_exit,stage_out,stopped} [{pending,running,suspended,completed,cancelled,failed,timeout,node_fail,preempted,boot_fail,deadline,out_of_memory,completing,configuring,resizing,resv_del_hold,requeued,requeue_fed,requeue_hold,revoked,signaling,special_exit,stage_out,stopped} ...]</font>
                        Specify the states of jobs to view. Accepts a comma separated list of state names or &apos;all&apos;. If &apos;all&apos; is specified then jobs of all states will be reported. If no state is specified then pending, running, and completing jobs
                        are reported. See the JOB STATE CODES section below for a list of valid states. Both extended and compact forms are valid. Note the &lt;state_list&gt; supplied is case insensitive (&apos;pending&apos; and &apos;PENDING&apos; are equivalent).
  <font color="#05979A">-w</font>, <font color="#05979A">--nodelist</font> <font color="#00AF87">NODELIST [NODELIST ...]</font>
                        Report only on jobs allocated to the specified node or list of nodes. This may either be the NodeName or NodeHostname as defined in slurm.conf(5) in the event that they differ. A node_name of localhost is mapped to the
                        current host name.
  <font color="#05979A">-e</font>                    Add the execution nodes, stdoutput file and stderror file to the table.</pre>

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
