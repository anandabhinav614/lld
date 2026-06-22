from enum import Enum
from uuid import uuid4
from collections import deque
from datetime import datetime
from threading import Thread, Lock
import time

class DownloadStatus(Enum):
    QUEUED = "QUEUED"
    DOWNLOADING = "DOWNLOADING"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class DownloadTask:
    def __init__(self, url:str, destination:str, total_bytes:float):
        self.download_id = str(uuid4())
        self.url = url
        self.destination = destination
        self.downloaded_bytes = 0
        self.total_bytes = total_bytes
        self.status = DownloadStatus.QUEUED
        self.error_message = None
        self.created_at = datetime.now()
        self.transition_map = {DownloadStatus.DOWNLOADING:[DownloadStatus.PAUSED, DownloadStatus.FAILED, DownloadStatus.CANCELLED],
                               DownloadStatus.QUEUED:[DownloadStatus.DOWNLOADING, DownloadStatus.CANCELLED],
                               DownloadStatus.FAILED:[DownloadStatus.QUEUED],
                               DownloadStatus.PAUSED: [DownloadStatus.QUEUED, DownloadStatus.CANCELLED]}

    def valid_transition(self, requested_state:DownloadStatus) ->bool:
        allowed = self.transition_map.get(self.status, [])
        return requested_state in allowed
    
    def pause(self):
        if self.valid_transition(DownloadStatus.PAUSED):
            self.status = DownloadStatus.PAUSED
            return True
        return False

    def resume(self) -> bool:
        if self.valid_transition(DownloadStatus.QUEUED):
            self.status = DownloadStatus.QUEUED
            return True
        return False
    
    def cancel(self) -> bool:
        if self.valid_transition(DownloadStatus.CANCELLED):
            self.status = DownloadStatus.CANCELLED
            return True
        return False

# Take a task -> Download the file -> Update progress -> Exit   
class DownloadWorker(Thread):
    def __init__(self, task:DownloadTask, download_manager:"DownloadManager"):
        super().__init__()
        self.task = task
        self.download_manager = download_manager

    def run(self):
        while self.task.status!=DownloadStatus.COMPLETED and self.task.downloaded_bytes<self.task.total_bytes:
            if self.task.status == DownloadStatus.PAUSED:
                return
            if self.task.status == DownloadStatus.CANCELLED:
                return
            
            time.sleep(5)
            self.task.downloaded_bytes+=1
        
        if self.task.downloaded_bytes==self.task.total_bytes:
            self.task.status = DownloadStatus.COMPLETED
            self.download_manager.on_download_completed(self.task)
        
class DownloadManager:
    def __init__(self, max_concurrent_downloads:int):
        self.tasks:dict[str, DownloadTask] = {} # task_id -> Download task()
        self.waiting_queue:deque[DownloadTask] = deque()
        self.active_downloads:dict[str, DownloadTask] = {} # download id-> Download()
        self.max_concurrent_downloads =  max_concurrent_downloads
        self.lock = Lock()
    
    def add_download(self, download_info:dict):
        new_task = DownloadTask(download_info.get("url"), download_info.get("destination"), download_info.get("total_bytes"))
        self.tasks[new_task.download_id] = new_task
        self.waiting_queue.append(new_task)
        self.schedule_downloads()

    def pause(self, task_id:str):
        with self.lock:
            paused_task = self.active_downloads.get(task_id, None)
            if paused_task is None:
                return False
            if paused_task.pause():
                del self.active_downloads[task_id]
                
        self.schedule_downloads()
        return True


    def resume(self, task_id):
        with self.lock:
            resume_task = self.tasks.get(task_id, None)
            if resume_task is None:
                return False
            if resume_task.resume():
                self.tasks[task_id] = resume_task
                self.waiting_queue.append(resume_task)
        self.schedule_downloads()
        return True

    def cancel(self, task_id):
        with self.lock:
            cancel_task = self.tasks.get(task_id, None)
            if cancel_task is None:
                return False
            if cancel_task.cancel():
                self.tasks[task_id] = cancel_task
                if task_id in self.active_downloads:
                    del self.active_downloads[task_id]
        self.schedule_downloads()
        return True
    
    def get_download(self, task_id:str):
        return self.tasks.get(task_id, None)
    
    def schedule_downloads(self):
        with self.lock:
            while len(self.active_downloads)<self.max_concurrent_downloads and self.waiting_queue:
                fifo_task = self.waiting_queue.popleft()
                if fifo_task.status == DownloadStatus.CANCELLED:
                    continue
                if fifo_task.status == DownloadStatus.QUEUED:
                    fifo_task.status = DownloadStatus.DOWNLOADING
                    self.active_downloads[fifo_task.download_id] = fifo_task
                    worker = DownloadWorker(fifo_task, self)
                    worker.start()

    def on_download_completed(self, task:DownloadTask):
        # remmove it from active download list
        with self.lock:
            del self.active_downloads[task.download_id]
        self.schedule_downloads()
        
        





