from collections import deque

class AhoCorasick:
    def __init__(self):
        self.goto_table = {}
        self.failure_table = {}
        self.output_table = {}
        self.patterns = []
        self.state_count = 1
        self._built = False
    
    def add_patterns(self, patterns):
        for pattern in patterns:
            if pattern:
                self.patterns.append(pattern)
        
        self._build_trie()
        self._built = False
    
    def _build_trie(self):
        self.goto_table = {0: {}}
        self.output_table = {}
        self.state_count = 1
        
        for pattern in self.patterns:
            state = 0
            
            for char in pattern:
                if char not in self.goto_table[state]:
                    self.goto_table[state][char] = self.state_count
                    self.goto_table[self.state_count] = {}
                    self.state_count += 1
                
                state = self.goto_table[state][char]
            
            if state not in self.output_table:
                self.output_table[state] = []
            self.output_table[state].append(pattern)
    
    def _build_failure_and_output(self):
        if self._built:
            return
        
        self.failure_table = {0: 0}
        queue = deque()
        
        for char, state in self.goto_table[0].items():
            self.failure_table[state] = 0
            queue.append(state)
        
        while queue:
            r = queue.popleft()
            
            for char, u in self.goto_table[r].items():
                queue.append(u)
                
                state = self.failure_table[r]
                while state != 0 and char not in self.goto_table[state]:
                    state = self.failure_table[state]
                
                if char in self.goto_table[state]:
                    self.failure_table[u] = self.goto_table[state][char]
                else:
                    self.failure_table[u] = 0
                
                failure_state = self.failure_table[u]
                if failure_state in self.output_table:
                    if u not in self.output_table:
                        self.output_table[u] = []
                    self.output_table[u].extend(self.output_table[failure_state])
        
        self._built = True
    
    def search(self, text):
        if not self.patterns or not text:
            return []
        
        self._build_failure_and_output()
        
        results = []
        state = 0
        
        for i, char in enumerate(text):
            while state != 0 and char not in self.goto_table[state]:
                state = self.failure_table[state]
            
            if char in self.goto_table[state]:
                state = self.goto_table[state][char]
            
            if state in self.output_table:
                for pattern in self.output_table[state]:
                    start_pos = i - len(pattern) + 1
                    results.append((pattern, start_pos, i))
        
        return results


def aho_corasick_search(text, patterns):
    ac = AhoCorasick()
    ac.add_patterns(patterns)
    
    return ac.search(text)