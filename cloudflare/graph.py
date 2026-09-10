import heapq

def dijkstra(n, times , start):
    adj_list = {}
    for u,v, w in times:
        if u not in adj_list:
            adj_list[u] = [(v,w)]
        else:
            adj_list[u].append((v,w))

    distances = [float("inf")] * (n+1)
    distances[start] = 0

    pq = [(0, start)]

    while pq:
        curr_cost, curr_node = heapq.heappop(pq)

        if curr_cost>distances[curr_node]:
            continue

        for neighbour, weight in adj_list.get(curr_node,[]):
            new_cost = curr_cost + weight

            if new_cost<distances[neighbour]:
                distances[neighbour]=new_cost
                heapq.heappush(pq, (new_cost, neighbour))
    result = max(distances[1:])
    return result if result!=float("inf") else -1

