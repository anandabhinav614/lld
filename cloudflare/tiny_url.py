class Codec:
    def __init__(self):
        self.long_to_short = {}
        self.short_to_long = {}
        self.chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.counter = 1
        self.fix_url_prefix = "https://tinyurl.com/"

    def encode(self, longUrl: str) -> str:
        """Encodes a URL to a shortened URL.
        """
        if longUrl in self.long_to_short:
            return self.long_to_short[longUrl]

        val = self.counter
        remainders = []
        while val:
            val_remainder = val%62
            val = val // 62
            remainders.append(self.chars[val_remainder])

        suffix = ""
        for i in range(len(remainders)-1, -1, -1):
            suffix+=remainders[i]

        shortUrl = self.fix_url_prefix + suffix
        
        self.short_to_long[shortUrl] = longUrl
        self.long_to_short[longUrl] = shortUrl

        self.counter+=1
        
        return shortUrl

    def decode(self, shortUrl: str) -> str:
        """Decodes a shortened URL to its original URL.
        """
        return self.short_to_long.get(shortUrl, None)

# Your Codec object will be instantiated and called as such:
# codec = Codec()
# codec.decode(codec.encode(url)) 