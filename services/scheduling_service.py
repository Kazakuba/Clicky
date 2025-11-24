import schedule
import time
import threading
from datetime import datetime, timedelta

class SchedulingService:
    def __init__(self):
        self.jobs = {}
        self.execution_counts = {}

    def schedule_workflow(self, workflow, callback):
        self.clear_jobs_for_workflow(workflow.name)
        self.jobs[workflow.name] = []
        self.execution_counts[workflow.name] = {}
        
        if hasattr(workflow, 'scheduled_executions') and workflow.scheduled_executions:
            for idx, scheduled_execution in enumerate(workflow.scheduled_executions):
                self._schedule_execution(workflow, scheduled_execution, callback, idx)
        elif workflow.start_time:
            self._schedule_legacy(workflow, callback)
        else:
            callback()

    def _schedule_execution(self, workflow, scheduled_execution, callback, idx):
        self.execution_counts[workflow.name][idx] = 0
        
        exec_datetime = scheduled_execution.execution_datetime
        
        if isinstance(exec_datetime, str):
            try:
                exec_datetime = datetime.fromisoformat(exec_datetime)
            except ValueError:
                try:
                    exec_datetime = datetime.strptime(exec_datetime, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    self._run_with_count(workflow, callback, idx, scheduled_execution.execution_count)
                    return
        
        if exec_datetime and exec_datetime > datetime.now():
            time_to_exec = exec_datetime - datetime.now()
            seconds_to_exec = time_to_exec.total_seconds()
            
            job = schedule.every(int(seconds_to_exec)).seconds.do(
                self._run_with_count, 
                workflow, 
                callback, 
                idx, 
                scheduled_execution.execution_count
            )
            self.jobs[workflow.name].append((job, idx))
        
        if scheduled_execution.repeat_interval:
            job = schedule.every(scheduled_execution.repeat_interval).seconds.do(
                self._run_with_count, 
                workflow, 
                callback, 
                idx, 
                scheduled_execution.execution_count
            )
            self.jobs[workflow.name].append((job, idx))

    def _schedule_legacy(self, workflow, callback):
        self.execution_counts[workflow.name][0] = 0
        
        try:
            if " " in workflow.start_time:
                start_time = datetime.strptime(workflow.start_time, "%Y-%m-%d %H:%M:%S")
                time_to_exec = start_time - datetime.now()
                if time_to_exec.total_seconds() > 0:
                    job = schedule.every(int(time_to_exec.total_seconds())).seconds.do(
                        self._run_with_count, workflow, callback, 0, workflow.execution_count
                    )
                    self.jobs[workflow.name].append((job, 0))
            else:
                job = schedule.every().day.at(workflow.start_time).do(
                    self._run_with_count, workflow, callback, 0, workflow.execution_count
                )
                self.jobs[workflow.name].append((job, 0))
        except (ValueError, AttributeError):
            self._run_with_count(workflow, callback, 0, workflow.execution_count)
        
        if workflow.repeat_interval:
            job = schedule.every(workflow.repeat_interval).seconds.do(
                self._run_with_count, workflow, callback, 0, workflow.execution_count
            )
            self.jobs[workflow.name].append((job, 0))

    def _run_with_count(self, workflow, callback, idx, max_executions):
        if workflow.name not in self.execution_counts:
            self.execution_counts[workflow.name] = {}
        if idx not in self.execution_counts[workflow.name]:
            self.execution_counts[workflow.name][idx] = 0
            
        if max_executions == 0 or self.execution_counts[workflow.name][idx] < max_executions:
            callback()
            self.execution_counts[workflow.name][idx] += 1
            
            if max_executions > 0 and self.execution_counts[workflow.name][idx] >= max_executions:
                self._clear_execution(workflow.name, idx)

    def run_pending(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_scheduler(self):
        threading.Thread(target=self.run_pending, daemon=True).start()

    def clear_jobs(self):
        schedule.clear()
        self.jobs = {}
        self.execution_counts = {}

    def clear_jobs_for_workflow(self, workflow_name):
        if workflow_name in self.jobs:
            for job, _ in self.jobs[workflow_name]:
                schedule.cancel_job(job)
            del self.jobs[workflow_name]
        
        if workflow_name in self.execution_counts:
            del self.execution_counts[workflow_name]

    def _clear_execution(self, workflow_name, idx):
        if workflow_name in self.jobs:
            for i, (job, job_idx) in enumerate(self.jobs[workflow_name]):
                if job_idx == idx:
                    schedule.cancel_job(job)
                    self.jobs[workflow_name].pop(i)
                    break
                    
            if workflow_name in self.execution_counts and idx in self.execution_counts[workflow_name]:
                del self.execution_counts[workflow_name][idx]