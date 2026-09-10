from collections import OrderedDict


class LFU:
    def __init__(self, capacity:int):
        self.capacity = capacity
        self.keys_info:dict[int, tuple[int,int]] = {} # key-> (val, freq)
        self.freq_key:dict[int, OrderedDict] = {} # freq->{key:None, }
        self.min_freq = 0

    def increase_freq(self, key:int):
        pass

    def get(self, key:int):
        if key not in self.keys_info:
            return -1
        val, _= self.keys_info[key]
        self.increase_freq(key)

        return val

    def put(self, key, val):
        if key in self.keys_info:
            self.keys_info[key][0] = val
            self.increase_freq(key)
            return

        if len(self.keys_info)>=self.capacity:
            evict_key, _ = self.freq_key[self.min_freq].popitem(last=False)
            del  self.keys_info[evict_key]

        self.keys_info[key] = (val, 1)
        if 1 not in self.freq_key:
            self.freq_key[1] = OrderedDict()

        self.freq_key[1][key] = None
        self.min_freq = 1