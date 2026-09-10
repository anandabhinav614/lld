class MyCircularQueue:

    def __init__(self, k: int):
        self.k = k
        self.queue = [None for _ in range(k)]
        self.last_ind = 0
        self.first_ind = 0
        self.curr_size = 0

    def enQueue(self, value: int) -> bool:
        if self.curr_size==self.k:
            return False
        self.queue[self.last_ind]=value
        self.last_ind = (self.last_ind+1)%self.k
        self.curr_size+=1
        return True

    def deQueue(self) -> bool:
        if self.curr_size==0:
            return False
        self.queue[self.first_ind] = None
        self.curr_size-=1
        self.first_ind = (self.first_ind+1)%self.k
        return True

    def Front(self) -> int:
        if self.curr_size == 0:
            return -1
        return self.queue[self.first_ind]

    def Rear(self) -> int:
        if self.curr_size == 0:
            return -1
        return self.queue[self.last_ind-1]

    def isEmpty(self) -> bool:
        return self.curr_size == 0

    def isFull(self) -> bool:
        return self.curr_size == self.k


# Your MyCircularQueue object will be instantiated and called as such:
# obj = MyCircularQueue(k)
# param_1 = obj.enQueue(value)
# param_2 = obj.deQueue()
# param_3 = obj.Front()
# param_4 = obj.Rear()
# param_5 = obj.isEmpty()
# param_6 = obj.isFull()