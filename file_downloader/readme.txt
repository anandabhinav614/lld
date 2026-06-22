You are building a simplified version of Internet Download Manager (IDM).
A user provides a URL and starts downloading a file.

The system should:
    Download multiple files simultaneously.
    Show progress of each download.
    Pause a download.
    Resume a paused download.
    Cancel a download.
    Retry failed downloads.
    Maintain download history.
    Support prioritization of downloads.
    Limit maximum concurrent downloads.

FR:
    1. Add a Download, User provides: URL, Destination Path -> System creates a download task.
    2. System starts downloading the file.
    3. Track Progress -> bytes downloaded, total bytes, percentage complete
    4. Pause Download -> Download can be paused.
    5. Resume Download-> Resume from the last downloaded byte.
    6. Cancel Download
    7. Download Status:
        QUEUED
        DOWNLOADING
        PAUSED
        COMPLETED
        FAILED
        CANCELLED
    8. Download History
    9. Concurrent Downloads (Support multiple downloads simultaneously.)
    10. Max Concurrent Limit: if max_concurrent = 3, If 10 downloads are added: 3 running, 7 waiting
    11. Retry Failed Downloads
    12. Priority Downloads  (Scheduler picks HIGH first.)

Core Entity:
1. Everything revolves around download -> DownloadTask:(id, url, filename, Destination, download_bytes, total_bytes, status, priority, error_message, created_at)
 Suppose download fails.->Status becomes: FAILED, Now user asks:Why did it fail? Status alone cannot answer.
    You need something like:
    error_message = "Connection timeout" or
    error_message = "404 Not Found" or
    error_message = "Disk Full"

2. Suppose there are 100 downloads. Who should own/manage them?
    DownloadManager, handles:
        all downloads
        running downloads
        queued downloads
        max concurrency
        scheduling
    It also expose the api's for: Add Download | Pause Download | Resume Download | Cancel Download | View History | Retry Failed Download

3. State Machine: DownloadStatus
    What states should a download go through?
    QUEUED
        |
        v
        DOWNLOADING
        |     \
        |       \
        |         \
        v          v
        PAUSED       FAILED
        |               |
        v               v
        DOWNLOADING   (resume/retry)

        DOWNLOADING
            |
            v
        COMPLETED

        QUEUED
        |
        v
        CANCELLED

        DOWNLOADING
        |
        v
        CANCELLED

        PAUSED
        |
        v
        CANCELLED

    .'. Allowed Transition:
        QUEUED -> DOWNLOADING | DOWNLOADING -> PAUSED | PAUSED -> DOWNLOADING | DOWNLOADING -> FAILED
        FAILED -> QUEUED | DOWNLOADING -> COMPLETED | 
        QUEUED -> CANCELLED
        DOWNLOADING -> CANCELLED
        PAUSED -> CANCELLED
    
4. Downloading a 10GB file might take 30 minutes. Should start() block the caller for 30 minutes?
    since we are also maintaing max concurrent download, we add that many concurrent threads
    Which task starts?
    Which task waits?
    When a slot becomes free?
    That's not a DownloadTask responsibility.
    That's not even a download worker responsibility.
    That's a scheduling responsibility.
    DownloadManager
        |
        |
        v
    DownloadScheduler
        |
        |
        +---- Queue
        |
        +---- Worker Threads

    How does the worker thread know that the user clicked Pause?
    while True:
    if task.status == PAUSED:
        break

    if task.status == CANCELLED:
        cleanup()
        break

    download_next_chunk()



