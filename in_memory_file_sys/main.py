from abc import ABC
from threading import RLock

class Node(ABC):
    def __init__(self, name:str):
        self.name = name
    
    @property
    def is_file(self):
        raise NotImplementedError
    
    def get_name(self):
        return self.name
    
class File(Node):
    def __init__(self, name, file_content:str=""):
        super().__init__(name)
        self.file_content = file_content
    
    @property
    def is_file(self):
        return True

class Directory(Node):
    def __init__(self, name):
        super().__init__(name)
        self.children:dict[str,Node] = {}
    
    @property
    def is_file(self):
        return False

class FileSystem:
    def __init__(self, dir):
        self.root:Directory = dir

    def _traverse(self, path:str)->tuple[Directory, str]:
        parts = []
        for p in path.split('/'):
            if p:
                parts.append(p)
        
        if not parts:
            raise ValueError("Not a valid path")

        # ignore root
        if parts[0] == self.root.get_name():
            parts = parts[1:]

        # after ignoring root if still there is no node then create root first
        if not parts:
            return self.root, self.root.name
        
        curr = self.root
        for part in parts[:-1]:
            child = curr.children.get(part)
            if child is None:
                raise ValueError("Invalid path")
            if child.is_file:
                raise ValueError("Cannot traverse through a file")
            curr = child

        return curr, parts[-1]

    def _get_node(self, path: str) -> Node:
        par_dir, name = self._traverse(path)
        node = par_dir.children.get(name)
        if node is None:
            raise ValueError("Path doesn't exist")
        return node

    def mkdir(self, path:str):
        par_dir, new_dir_name = self._traverse(path)

        child = par_dir.children.get(new_dir_name, None)
        if child:
            raise ValueError("Path already exists")
        
        new_dir = Directory(new_dir_name)
        par_dir.children[new_dir_name]=new_dir
        return True

    def touch(self, path:str):
        par_dir, new_file_name = self._traverse(path)
        child = par_dir.children.get(new_file_name, None)
        if child:
            raise ValueError("Path already exists")
        
        new_file = File(new_file_name)
        par_dir.children[new_file_name] = new_file
        return True
    
    def write(self, path:str, content:str) ->bool :
        try:
            par_dir, file_name = self._traverse(path)
            file:Node = par_dir.children.get(file_name, None)
            if not file or not file.is_file:
                return False
            file.file_content = content
            return True
        except ValueError:
            return False 
    
    def read(self, path:str):
        node = self._get_node(path)
        if not node.is_file:
            raise ValueError("Not a file")
        return node.file_content
    
    def ls(self, path:str):
        node = self._get_node(path)
        if node.is_file:
            raise ValueError("Given path is a file not dir")
        return list(node.children.keys())

    def mv(self, from_path:str, to_path:str):
        src_par_dir, node_name = self._traverse(from_path)
        dst_par_dir, dir_name = self._traverse(to_path)

        node = src_par_dir.children.get(node_name, None)
        if not node:
            return False
        to_dir = dst_par_dir.children.get(dir_name, None)
        if not to_dir or to_dir.is_file:
            return False
        if node_name in to_dir.children:
            return False
        to_dir.children[node_name] = node
        del src_par_dir.children[node_name]
        return True

    def rm(self, path:str):
        par_dir, name = self._traverse(path)
        if name not in par_dir.children:
            raise ValueError("Path not found")
        del par_dir.children[name]

    def search(self, name:str):
        result = []
        def dfs(node:Directory|File, curr_path:str):
            if node.get_name()==name:
                result.append(curr_path)
            if not node.is_file:
                for child_name, child in node.children.items():
                    dfs(child, curr_path+"/"+child_name)

        dfs(self.root, self.root.get_name())
        return result

