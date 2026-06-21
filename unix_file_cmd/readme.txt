implemnet linux find command as an api ,the api willl support:
Supports multiple search criteria:
    File size
    File extension
    File name substring (easily extensible)
    Supports Boolean composition of queries:
        AND, OR, NOT

Req:
Api ->find(root, criteria)
    criteria:
        size > 100
        extension = ".txt"
        name contains "report"
    and criteria can be combined:
        (size > 100 AND extension=".txt")
        (name contains "invoice" OR extension=".pdf")
        NOT(extension=".tmp")

Entities: 
    File(name, size, entension)
    Filter(interface) +matches(file) ->SizeFilter, ExtensionFilter, NameFilter

How to model -> NOT(extension=".tmp") as we have all major filters?
            -> (size > 100 AND extension=".txt")
            query = AndFilter(SizeFilter(),ExtensionFilter())
            here we need to do -> SizeFilter() AND ExtensionFilter()
            now to do this efficently we can have a class called ANDFilter.
            which takes left and right -> return left and right, here left,right are filters.
            Similarly we can have NOTFilter, ORFilter classes.

            ->(size > 100 AND extension=".txt") OR (name contains "invoice")
            query = OrFilter(AndFilter(SizeFilter(),ExtensionFilter()),NameFilter())
            The left side of the OR is not a simple filter. It's another filter tree.
                      OR
                    /    \
                    AND    Name
                /   \
            Size    Extension

            Execution:
                OR.matches(file)
                    AND.matches(file)
                        Size.matches(file)
                        Extension.matches(file)
                    Name.matches(file)
            
            This is Composite Pattern - Composite Pattern allows individual objects and groups of objects to be treated uniformly.
            Another famous example file/folder:
            Folder
                Folder
                    File
                    File
                File
            

Extension:
we can have folder and files both, we can do dfs traversal in that case.


```
class Node(ABC):
    pass

class File(Node):
    def __init__(self, name: str, size: int, extension: str):
        self.name = name
        self.size = size
        self.extension = extension

class Folder(Node):
    def __init__(self, name: str):
        self.name = name
        self.children: list[Node] = []

    def add(self, node: Node):
        self.children.append(node)


class FileSearcher:

    def search(self, root: Folder, query: Filter) -> list[File]:
        result = []
        self._dfs(root, query, result)
        return result

    def _dfs(self, node: Node, query: Filter, result: list[File]):

        if isinstance(node, File):
            if query.matches(node):
                result.append(node)
            return

        # node is Folder
        for child in node.children:
            self._dfs(child, query, result)
```
i/p:
    root
    ├── docs
    │   ├── invoice_2025.txt
    │   └── notes.txt
    └── images
        ├── photo.png
        └── invoice_scan.jpg

query = ORFilter(
    ANDFilter(
        SizeFilter(100, ComparisonOperator.GT),
        ExtensionFilter(".txt")
    ),
    NameFilter("invoice")
)
        
o/p:    invoice_2025
        invoice_scan
