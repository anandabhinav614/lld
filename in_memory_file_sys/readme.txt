The file system consists of Directories and Files.
    Directory: Can contain Files and other Directories.
    File: Contains text content (string).
    Paths: Use Unix-style paths (e.g., /, /home/user/docs).

Your implementation must support the following interface (or equivalent):
    // Creates a new directory. 
    // False if parent directory doesn't exist or if name already exists.
    Mkdir(path string) 
    -> mkdir("/a/b"), should fail if /a doesn't exist.

    // Creates a new empty file.
    // False if parent directory doesn't exist or if name already exists.
    Touch(path string) 

    // Writes content to a file. Overwrites existing content.
    // False if file doesn't exist.
    Write(path string, content string) 

    // Returns the content of a file.
    // False if file doesn't exist.
    Read(path string) (string)

    // Lists the contents of a directory (names only).
    // False if directory doesn't exist.
    Ls(path string) ([]string)

    // Moves a file or directory from source to destination.
    // False if source doesn't exist or destination parent doesn't exist.
    Mv(srcPath, dstPath string) error

    // Removes a file or directory.
    // False if path doesn't exist.
    Rm(path string) 
    
    // Search for a file or directory by name (supports prefix or simple matching).
    Search(name string) ([]string)

Core Entites:
    1. FileSystem(Service):
        -mkdir(), touch(), write(), read(), ls(), mv(), rm(), search()
    2. Node(interface) -> helps to create class File, class Dir

Concurrency:
    Why RLock?
    Suppose mkdir() calls _traverse(), and later you refactor _traverse() to also acquire locks. 
    With a normal Lock, the same thread could deadlock by acquiring the same lock twice. RLock avoids that.

    The only tricky operation: mv()
    You need two locks.
    Always acquire them in a fixed order, for example:

        first, second = sorted([src_parent, dst_parent], key=id)
        with first.lock:
            with second.lock:
                ...

    Keep your current implementation as the single-threaded version.
    If the interviewer asks for concurrency, extend it live by:
    Adding an RLock to Directory.
    Adding an RLock to File.
    Explaining that a production-quality implementation would use hand-over-hand locking during traversal to avoid races while walking the tree.