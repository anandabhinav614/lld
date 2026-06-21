from abc import ABC, abstractmethod
from enum import Enum

class ComparisonOperator(Enum):
    GT = ">"
    LT = "<"
    EQ = "=="
    GTE = ">="
    LTE = "<="

class File:
    def __init__(self, name:str, size:int, extension:str):
        self.name = name
        self.size = size
        self.extension = extension

class Filter(ABC):
    def __init__(self):
        pass
    @abstractmethod
    def matches(self, file:File) -> bool:
        pass

# Leaf filters:
class SizeFilter(Filter):
    def __init__(self, size:int, operator:ComparisonOperator):
        self.size = size
        self.operator = operator

    def matches(self, file:File):
        if self.operator == ComparisonOperator.GT:
            return file.size>self.size
        elif self.operator == ComparisonOperator.LT:
            return file.size<self.size
        elif self.operator == ComparisonOperator.EQ:
            return file.size==self.size
        elif self.operator == ComparisonOperator.GTE:
            return file.size>=self.size
        elif self.operator == ComparisonOperator.LTE:
            return file.size<=self.size
        

class ExtensionFilter(Filter):
    def __init__(self, extension:str):
        self.extension = extension
    
    def matches(self, file):
        return file.extension == self.extension

class NameFilter(Filter):
    def __init__(self, name:str):
        self.name = name
    
    def matches(self, file):
        return self.name in file.name
        
# Composite filters:
class ORFilter(Filter):
    def __init__(self, left_filter:Filter, right_filter:Filter):
        self.left_filter = left_filter
        self.right_filter = right_filter

    def matches(self, file):
        return self.left_filter.matches(file) or self.right_filter.matches(file)
        
class ANDFilter(Filter):
    def __init__(self, left_filter:Filter, right_filter:Filter):
        self.left_filter = left_filter
        self.right_filter = right_filter

    def matches(self, file):
        left_val = self.left_filter.matches(file)
        if left_val is False:
            return False
        return self.right_filter.matches(file)
    
class NOTFilter(Filter):
    def __init__(self, not_filter:Filter):
        self.not_filter = not_filter
    
    def matches(self, file):
        return not self.not_filter.matches(file)

class FileSearcher:
    
    def search(self, files:list[File], query:Filter) ->list[File]:
        result = []

        for file in files:
            if query.matches(file):
                result.append(file)

        return result
    

def main():
    files = [File("a_invoice", 100, ".txt"),
             File("b", 2, ".xml"),
             File("c_invoice", 3, ".json"),
             File("d_invoice", 400, ".txt"),
             File("e_invoices", 500, ".png")]
    # (size > 100 AND extension=".txt") OR (name contains "invoice")
    query = ORFilter(ANDFilter(SizeFilter(100, ComparisonOperator.GT), ExtensionFilter(".txt")), (NameFilter("invoice")))
    result = FileSearcher().search(files, query)
    for file in result:
        print(file.name)
    

main()
