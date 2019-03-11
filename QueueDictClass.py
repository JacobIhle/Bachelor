from collections import deque

class OurDataStructure:
    dictionary = {}
    doubleSidedQueue = deque()
    counter = 0

    def append(self, key, deepZoomGen):
        try:
            if self.counter >= 10:
                oldestKey = self.doubleSidedQueue.pop()
                self.doubleSidedQueue.appendleft(key)

                self.dictionary[key] = deepZoomGen
                self.dictionary.pop(oldestKey, None)
            else:
                self.doubleSidedQueue.appendleft(key)
                self.dictionary[key] = deepZoomGen
                self.counter += 1
            return True
        except:
            return False

    def get(self, key):
        try:
            return self.dictionary[key]
        except:
            return None
