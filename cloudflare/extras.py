# design hit counter LC 362
from bisect import bisect_left

class HitCounter:

    def __init__(self):
        self.hits = []

    def hit(self, timestamp:int) -> None:
        self.hits.append(timestamp)

    def get_hits(self, timestamp:int) -> int:
        pos = bisect_left(self.hits, timestamp-300+1)
        return len(self.hits)-pos


# LC 359 Logger Rate Limiter

class LoggerRateLimiter:
    def __init__(self):
        self.ts ={}

    def should_print_message(self, timestamp:int, message:str) ->bool:
        if message not in self.ts:
            self.ts[message] = timestamp
            return True
        msg_ts = self.ts[message]
        if timestamp - msg_ts>=10:
            self.ts[message] = timestamp
            return True
        return False


def threeSum(nums: list[int]) -> list[list[int]]:
    nums.sort()
    ans = []
    for i in range(len(nums)-2):
        if i>0 and nums[i]==nums[i-1]:
            continue
        l = i+1
        r = len(nums) -1
        while(l<r):
            total = nums[i]+nums[l]+nums[r]



def gameOfLife(board: list[list[int]]) -> None:
    dir = [(-1, 0), (-1, 1), (0, 1), (1, 1),(1, 0),(1, -1), (0, -1), (-1, -1)]
    m, n = len(board), len(board[0])

    # 1->live cell
    # 0 -> dead cell
    # 2->was live now dead
    # 3 -> was dead now live

    def valid(row, col):
        if row>=m or row<0 or col>=n or col<0:
            return False
        return True

    for i in range(m):
        for j in range(n):
            curr_cell = board[i][j]
            live_cells = 0
            for r, c in dir:
                n_r, n_c = i+r, j+c
                if not valid(n_r, n_c):
                    continue
                if board[n_r][n_c] == 1 or board[n_r][n_c] == 2:
                    live_cells+=1

            # rules
            if curr_cell == 1 and live_cells<2:
                board[i][j]=2
            elif curr_cell == 1 and live_cells in (2, 3):
                continue
            elif curr_cell == 1 and live_cells>3:
                board[i][j] = 2
            elif curr_cell == 0 and live_cells == 3:
                board[i][j] = 3

    for i in range(m):
        for j in range(n):
            if board[i][j]==2:
                board[i][j] = 0
            elif board[i][j]==3:
                board[i][j] = 1
    

def countBattleships(self, board: list[list[str]]) -> int:
    count = 0

    m, n = len(board), len(board[0])

    def valid_battleship(i, j):
        if i<0 or i>=m or j<0 or j>=n:
            return True
        elif board[i][j] == 'X':
            return False
        return True

    for i in range(m):
        for j in range(n):
            if board[i][j] == 'X' and valid_battleship(i-1,j) and valid_battleship(i, j-1):
                count+=1

    return count

# 1094. Car Pooling
import heapq
def carPooling(trips: list[list[int]], capacity: int) -> bool:
    heap = []
    curr_capacity = capacity

    trips.sort(key=lambda x:x[1])

    for persons, from_loc, to_loc in trips:
        while heap and heap[0][0]<=from_loc:
            _, number_of_ppl = heapq.heappop(heap)
            curr_capacity+=number_of_ppl
        if persons<=curr_capacity:
            heapq.heappush(heap, (to_loc, persons))
            curr_capacity-=persons
        else:
            return False
    return True


