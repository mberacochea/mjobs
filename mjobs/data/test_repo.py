#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2024 - Martin Beracochea
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

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from mjobs.models import SlurmJob

from .repository import JobRepository


class TestJobRepository(JobRepository):
    """Repository for generating fake Slurm job data for testing.

    This implementation generates realistic fake data for development and testing
    purposes without requiring actual Slurm installation.
    """

    def __init__(self, seed: Optional[int] = None):
        """Initialize the test repository.

        :param seed: Random seed for reproducible test data (optional)
        """
        if seed is not None:
            random.seed(seed)

        self.job_states = ["RUNNING", "PENDING", "COMPLETED", "FAILED", "CANCELLED"]
        self.partitions = ["compute", "gpu", "highmem", "bigmem", "short", "long", "standard"]
        self.users = ["alice", "bob", "charlie", "diana", "eve", "frank"]
        self.job_names = [
            "blast_search",
            "assembly_job",
            "training_model",
            "data_analysis",
            "simulation_run",
            "preprocessing",
            "alignment",
            "annotation",
            "quality_control",
            "variant_calling",
            "rna_seq_pipeline",
            "deep_learning",
            "molecular_dynamics",
            "phylogeny_inference",
            "nf-EBIMETAGENOMICS_MIASSEMBLER_MIASSEMBLER_SHORT_READS_ASSEMBLER_SPADES_(ERR13502861)",
            "nf-CHIPSEQ_PIPELINE_BWA_MEM_(SRR12345678)",
            "nf-RNASEQ_STAR_ALIGNMENT_(sample_01)",
            "nf-ATACSEQ_PEAK_CALLING_(condition_A)",
            "nextflow_pipeline_preprocessing",
            "metagenomics_assembly_job",
            "genomics_variant_calling",
            "transcriptomics_differential_expression",
        ]
        self.commands = [
            "python train_model.py --epochs 100 --lr 0.001",
            "blast -query sequences.fasta -db nr -out results.xml",
            "spades.py -1 reads_1.fastq -2 reads_2.fastq -o assembly/",
            "bwa mem ref.fa reads.fastq | samtools sort -o aligned.bam",
            "gatk HaplotypeCaller -I input.bam -O variants.vcf -R reference.fa",
            "nextflow run pipeline.nf --input data/ --outdir results/",
            "matlab -batch 'run_simulation(1000, 0.5)'",
            "Rscript analysis.R --input data.csv --output plots/",
        ]
        self.nodes_list = [
            "compute-001",
            "compute-002",
            "compute-003",
            "gpu-001",
            "gpu-002",
            "highmem-001",
            "highmem-002",
            "N/A",  # For non-running jobs
        ]

    def get_jobs(self, job_ids: Optional[List[int]] = None, extra_args: Optional[List[str]] = None) -> List[SlurmJob]:
        """Generate fake jobs that match the requested criteria.

        :param job_ids: Specific job IDs to generate (optional)
        :param extra_args: Filtering arguments (simulated, optional)
        :return: List of fake SlurmJob instances
        """
        # Generate default number of jobs or specific ones
        if job_ids:
            jobs = [self._generate_job_with_id(str(job_id)) for job_id in job_ids]
        else:
            # Generate 50 jobs by default
            jobs = [self._generate_random_job() for _ in range(50)]

        # Apply simple filtering based on extra_args (simulate real filtering)
        if extra_args:
            jobs = self._apply_filters(jobs, extra_args)

        return jobs

    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Generate fake detailed job information.

        :param job_id: The job ID to generate details for
        :return: Dictionary containing fake detailed job information
        """
        # Generate a consistent job for this ID
        job = self._generate_job_with_id(job_id)

        # Generate detailed information
        return {
            "JobId": job.job_id,
            "JobName": job.job_name,
            "UserId": f"{job.user_name}({random.randint(1000, 9999)})",
            "GroupId": f"users({random.randint(100, 999)})",
            "Priority": str(random.randint(1, 100)),
            "Nice": "0",
            "Account": random.choice(["default", "project_a", "project_b"]),
            "QOS": random.choice(["normal", "high", "low"]),
            "JobState": job.job_state,
            "Reason": job.state_reason,
            "Dependency": "(null)",
            "Requeue": "1" if random.choice([True, False]) else "0",
            "Restarts": str(random.randint(0, 3)),
            "BatchFlag": "1",
            "Reboot": "0",
            "ExitCode": "0:0" if job.job_state == "COMPLETED" else "1:0" if job.job_state == "FAILED" else "(null)",
            "RunTime": self._generate_runtime(),
            "TimeLimit": job.time_limit,
            "TimeMin": "N/A",
            "SubmitTime": job.submit_time,
            "EligibleTime": job.submit_time,
            "AccrueTime": job.submit_time,
            "StartTime": job.start_time,
            "EndTime": self._generate_end_time(job.job_state),
            "Deadline": "N/A",
            "SuspendTime": "None",
            "SecsPreSuspend": "0",
            "LastSchedEval": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "Scheduler": "Main",
            "Partition": job.partition,
            "AllocNode:Sid": f"{random.choice(self.nodes_list)}:{random.randint(1000, 9999)}",
            "ReqNodeList": "(null)",
            "ExcNodeList": "(null)",
            "NodeList": job.nodes,
            "BatchHost": job.nodes if job.nodes != "N/A" else "N/A",
            "NumNodes": "1" if job.nodes != "N/A" else "0",
            "NumCPUs": str(random.randint(1, 32)),
            "NumTasks": str(random.randint(1, 16)),
            "CPUs/Task": str(random.randint(1, 4)),
            "ReqB:S:C:T": "0:0:*:*",
            "TRES": f"cpu={random.randint(1, 32)},mem={random.randint(1000, 64000)}M,node=1",
            "Socks/Node": "*",
            "NtasksPerN:B:S:C": f"{random.randint(1, 16)}:0:*:*",
            "CoreSpec": "*",
            "MinCPUsNode": "1",
            "MinMemoryNode": f"{random.randint(1000, 16000)}M",
            "MinTmpDiskNode": "0",
            "Features": "(null)",
            "DelayBoot": "00:00:00",
            "OverSubscribe": "OK" if random.choice([True, False]) else "NO",
            "Contiguous": "1" if random.choice([True, False]) else "0",
            "Licenses": "(null)",
            "Network": "(null)",
            "Command": job.command,
            "WorkDir": job.workdir,
            "StdErr": f"{job.workdir}/slurm-{job.job_id}.out",
            "StdIn": "/dev/null",
            "StdOut": f"{job.workdir}/slurm-{job.job_id}.out",
            "Power": "(null)",
            "RebootOnFailure": "No",
            "TresPerTask": "",
            "ReqTRES": f"cpu={random.randint(1, 32)},mem={random.randint(1000, 16000)}M,node=1",
            "AllocTRES": f"cpu={random.randint(1, 32)},mem={random.randint(1000, 64000)}M,node=1",
            "MCS_label": "N/A",
        }

    def _generate_random_job(self) -> SlurmJob:
        """Generate a completely random job."""
        job_id = str(random.randint(100000, 999999))
        return self._generate_job_with_id(job_id)

    def _generate_job_with_id(self, job_id: str) -> SlurmJob:
        """Generate a job with a specific ID but random other attributes.

        :param job_id: The job ID to use
        :return: SlurmJob with the specified ID
        """
        # Use job_id as seed for consistent generation
        temp_random = random.Random(job_id)

        job_state = temp_random.choice(self.job_states)
        user_name = temp_random.choice(self.users)
        job_name = temp_random.choice(self.job_names)

        # Generate timestamps
        submit_time = self._generate_timestamp(temp_random, days_ago=temp_random.randint(0, 7))
        start_time = self._generate_start_time(temp_random, submit_time, job_state)
        end_time = self._generate_end_time_relative(temp_random, start_time, job_state)

        return SlurmJob(
            job_id=job_id,
            job_name=job_name,
            time_limit=temp_random.choice(["1:00:00", "4:00:00", "12:00:00", "1-00:00:00", "7-00:00:00"]),
            memory=f"{temp_random.randint(1, 64)}G",
            partition=temp_random.choice(self.partitions),
            job_state=job_state,
            user_name=user_name,
            command=temp_random.choice(self.commands),
            state_reason=self._generate_state_reason(temp_random, job_state),
            start_time=start_time,
            submit_time=submit_time,
            end_time=end_time,
            workdir=f"/home/{user_name}/work/{job_name}_{job_id}",
            nodes=temp_random.choice(self.nodes_list) if job_state == "RUNNING" else "N/A",
        )

    def _apply_filters(self, jobs: List[SlurmJob], extra_args: List[str]) -> List[SlurmJob]:
        """Apply filtering based on extra arguments (simulate squeue filters).

        :param jobs: List of jobs to filter
        :param extra_args: Arguments like ["-u", "alice", "-t", "RUNNING"]
        :return: Filtered list of jobs
        """
        filtered_jobs = jobs.copy()

        # Simple simulation of common filters
        for i in range(0, len(extra_args), 2):
            if i + 1 >= len(extra_args):
                break

            flag, value = extra_args[i], extra_args[i + 1]

            if flag == "-u":  # User filter
                filtered_jobs = [job for job in filtered_jobs if job.user_name == value]
            elif flag == "-t":  # State filter
                filtered_jobs = [job for job in filtered_jobs if job.job_state == value.upper()]
            elif flag == "-p":  # Partition filter
                filtered_jobs = [job for job in filtered_jobs if job.partition == value]

        return filtered_jobs

    def _generate_timestamp(self, rng: random.Random, days_ago: int = 0, hours_ago: int = 0) -> str:
        """Generate a timestamp string.

        :param rng: Random number generator
        :param days_ago: Number of days in the past
        :param hours_ago: Number of hours in the past
        :return: Formatted timestamp string
        """
        dt = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
        return dt.strftime("%Y-%m-%dT%H:%M:%S")

    def _generate_start_time(self, rng: random.Random, submit_time: str, job_state: str) -> str:
        """Generate start time based on job state.

        :param rng: Random number generator
        :param submit_time: Job submission time
        :param job_state: Current job state
        :return: Formatted start time string
        """
        if job_state in ["PENDING"]:
            return "N/A"
        else:
            # Start some time after submission
            submit_dt = datetime.strptime(submit_time, "%Y-%m-%dT%H:%M:%S")
            start_dt = submit_dt + timedelta(minutes=rng.randint(1, 60))
            return start_dt.strftime("%Y-%m-%dT%H:%M:%S")

    def _generate_end_time_relative(self, rng: random.Random, start_time: str, job_state: str) -> str:
        """Generate end time or remaining time.

        :param rng: Random number generator
        :param start_time: Job start time
        :param job_state: Current job state
        :return: Formatted end/remaining time string
        """
        if job_state in ["COMPLETED", "FAILED", "CANCELLED"]:
            return "INVALID"  # Job finished
        elif job_state == "PENDING":
            return "N/A"
        else:  # RUNNING
            return f"{rng.randint(0, 23)}:{rng.randint(0, 59)}:{rng.randint(0, 59)}"

    def _generate_end_time(self, job_state: str) -> str:
        """Generate end time for job details.

        :param job_state: Current job state
        :return: Formatted end time string
        """
        if job_state in ["COMPLETED", "FAILED", "CANCELLED"]:
            return (datetime.now() - timedelta(hours=random.randint(1, 48))).strftime("%Y-%m-%dT%H:%M:%S")
        else:
            return "Unknown"

    def _generate_runtime(self) -> str:
        """Generate runtime string.

        :return: Formatted runtime string (HH:MM:SS)
        """
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _generate_state_reason(self, rng: random.Random, job_state: str) -> str:
        """Generate appropriate state reason.

        :param rng: Random number generator
        :param job_state: Current job state
        :return: Appropriate state reason string
        """
        reasons = {
            "PENDING": ["Priority", "Resources", "Dependency", "QOSMaxJobsPerUserLimit"],
            "RUNNING": ["None"],
            "COMPLETED": ["None"],
            "FAILED": ["NonZeroExitCode", "OutOfMemory", "TimeLimit"],
            "CANCELLED": ["UserRequest", "AdminCancel", "TimeLimit"],
        }
        return rng.choice(reasons.get(job_state, ["None"]))
