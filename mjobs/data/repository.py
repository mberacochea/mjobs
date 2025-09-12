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

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from mjobs.models import SlurmJob


class JobRepository(ABC):
    """Abstract repository interface for job data access.

    This interface defines the contract for accessing job data,
    whether from real Slurm commands or test data sources.
    """

    @abstractmethod
    def get_jobs(self, job_ids: Optional[List[int]] = None, extra_args: Optional[List[str]] = None) -> List[SlurmJob]:
        """Retrieve jobs based on criteria.

        :param job_ids: Specific job IDs to fetch (optional)
        :param extra_args: Additional arguments for job filtering (optional)
        :return: List of SlurmJob instances
        :raises JobRepositoryError: If job retrieval fails
        """
        pass

    @abstractmethod
    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific job.

        :param job_id: The job ID to get details for
        :return: Dictionary containing detailed job information
        :raises JobRepositoryError: If job details retrieval fails
        """
        pass


class JobRepositoryError(Exception):
    """Exception raised for job repository operations."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """Initialize the exception.

        :param message: Human-readable error message
        :param original_error: The original exception that caused this error
        """
        super().__init__(message)
        self.original_error = original_error
