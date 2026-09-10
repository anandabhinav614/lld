# Design a Consistent Hashing ring to distribute keys evenly across a dynamic set of servers. 
# To ensure load balancing, each physical server should be represented by $K$ virtual nodes on the hash ring.

"""
Problem: Which server should handle a given key?
Naive approach: hash(key) % number_of_servers
3 servers (A, B, C) → hash(key) % 3 maps each key to a server.
Add a 4th server (D) → formula becomes hash(key) % 4.
Since the modulus changed, almost every key gets remapped to a different server 
        — even though only one server was added.

Why this is bad: In a distributed system (like a cache or DB shard), 
remapping means massive cache misses / data movement every time you scale up or down
         — just adding one server can invalidate nearly everything.

"""
from bisect import bisect_left

class ConsistentHashRing:

    def __init__(self, k:int):
        self.ring = []
        self.server_nodes = {}
        self.k = k

    def hash_function(self, virtual_node:str) ->int:
        pass

    def add_server(self, server_id:str):

        if server_id in self.server_nodes:
            return

        self.server_nodes[server_id] = []
        for i in range(self.k):
            virtual_node = server_id + "_" + str(i)
            hash_val = self.hash_function(virtual_node)
            self.ring.append((hash_val, server_id))
            # pos = bisect_left(self.ring, (hash_val, server_id))
            # self.ring.insert(pos, (hash_val,server_id))
            self.server_nodes[server_id].append(hash_val)

        self.ring.sort()

    def remove_server(self, server_id:str) -> None:
        if server_id not in self.server_nodes:
            return

        new_server_ring = []
        for hash_val, server in self.ring:
            if server != server_id:
                new_server_ring.append((hash_val, server))

        self.ring = new_server_ring

        del self.server_nodes[server_id]

    def get_server(self, key:str) -> str:
        if not self.ring:
            return ""  
        hash_val = self.hash_function(key)
        idx = bisect_left(self.ring, (hash_val, ""))
        if idx == len(self.ring):
            idx = 0
        return self.ring[idx][1]


    