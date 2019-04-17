from collections import deque


class SessionDeepzoomStorage:
    dictionary = {}
    doubleSidedQueue = deque()
    counter = 0

    def append(self, sessionID, deepZoomGen):
        try:
            if self.counter >= 1000:
                oldestKey = self.doubleSidedQueue.pop()
                self.doubleSidedQueue.appendleft(sessionID)

                self.dictionary[sessionID] = deepZoomGen
                self.dictionary.pop(oldestKey, None)
            else:
                self.doubleSidedQueue.appendleft(sessionID)
                self.dictionary[sessionID] = deepZoomGen
                self.counter += 1
            return True
        except:
            return False

    def get(self, sessionID):
        try:
            return self.dictionary[sessionID]
        except:
            return None

    def size(self):
        return self.counter