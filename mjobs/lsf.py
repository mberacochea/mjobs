#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2019-2021 - Martin Beracochea
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from subprocess import check_output
from typing import List, Optional


def _parse_bjobs(bjobs_output_str):
    """Parse records from bjobs json type output.
    This snippet was taken from: https://github.com/DataBiosphere/toil/blob/eb2ae8365ae2ebdd50132570b20f7d480eb40cac/src/toil/batchSystems/lsf.py#L331
    :param bjobs_output_str: stdout of bjobs json type output
    :return: list with the jobs
    """
    bjobs_dict = None
    bjobs_records = None
    # Handle Cannot connect to LSF. Please wait ... type messages
    dict_start = bjobs_output_str.find("{")
    dict_end = bjobs_output_str.rfind("}")
    if dict_start != -1 and dict_end != -1:
        bjobs_output = bjobs_output_str[dict_start : (dict_end + 1)]
        bjobs_dict = json.loads(bjobs_output)
        return bjobs_dict["RECORDS"]
    if bjobs_records is None:
        raise ValueError(f"Could not find bjobs output json in: {bjobs_output_str}")
    return []


def get_jobs(job_ids: Optional[list[int]] = None, lsf_args: Optional[List[str]] = None):
    """bjobs command, it uses the json output and includes [stat, name and jobid].
    Any other parameters in lsf_args will be included in the call to bjobs.
    """
    fields = [
        "stat",
        "name",
        "jobid",
        "job_group",
        "user",
        "queue",
        "submit_time",
        "start_time",
        "finish_time",
        "exec_host",
        "command",
        "exit_reason",
        "exit_code",
        "error_file",
        "output_file",
        "pend_reason",
    ]
    args = ["bjobs", "-json", "-o", " ".join(fields)]
    if lsf_args:
        args.extend(list(map(str, lsf_args)))
    if job_ids:
        args.extend(list(map(str, job_ids)))
    bjobs_output = check_output(args, universal_newlines=True)
    jobs = _parse_bjobs(bjobs_output)
    return jobs
