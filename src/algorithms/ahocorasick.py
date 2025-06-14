from collections import deque, defaultdict

class AhoCorasick:
    def __init__(self):
        self.trie = defaultdict(dict)
        self.failure = {}
        self.output = defaultdict(list)
        self.patterns = []
        self.node_count = 1
    
    def add_pattern(self, pattern):
        self.patterns.append(pattern)
        node = 0
        
        for char in pattern:
            if char not in self.trie[node]:
                self.trie[node][char] = self.node_count
                self.node_count += 1
            node = self.trie[node][char]
        
        self.output[node].append(pattern)
    
    def build_failure_function(self):
        # Kalo gagal balik ke failure links
        self.failure = {0: 0}
        queue = deque()

        for char in self.trie[0]:
            child = self.trie[0][char]
            self.failure[child] = 0
            queue.append(child)

        while queue:
            current = queue.popleft()
            for char in self.trie[current]:
                child = self.trie[current][char]
                queue.append(child)

                failure_node = self.failure[current]

                while failure_node != 0 and char not in self.trie[failure_node]:
                    failure_node = self.failure[failure_node]

                if char in self.trie[failure_node] and failure_node != 0:
                    self.failure[child] = self.trie[failure_node][char]
                else:
                    self.failure[child] = 0
    
    def search(self, text):
        if not self.patterns:
            return []
        
        self.build_failure_function()
        
        results = []
        current = 0 
        
        for i, char in enumerate(text):
            while current != 0 and char not in self.trie[current]:
                current = self.failure[current]

            if char in self.trie[current]:
                current = self.trie[current][char]

            # Cek current state dan semua failure state
            temp_state = current
            visited = set()
            
            while temp_state != 0 and temp_state not in visited:
                visited.add(temp_state)

                for pattern in self.output[temp_state]:
                    start_pos = i - len(pattern) + 1
                    results.append((pattern, start_pos, i))
                
                temp_state = self.failure[temp_state]
        
        return results


def aho_corasick_search(text, patterns):
    """
    Mencari multiple patterns dalam text menggunakan Aho-Corasick
    
    Args:
        text: String yang akan dicari
        patterns: List of strings (pattern yang dicari)
    
    Returns:
        List of tuples (pattern, start_position, end_position)
    """
    ac = AhoCorasick()

    for pattern in patterns:
        ac.add_pattern(pattern)
    
    return ac.search(text)

# if __name__ == "__main__":
#     # Test case 1: Multiple patterns
#     text = "ushers"
#     patterns = ["he", "she", "his", "hers"]
    
#     print("=== Test Case 1 ===")
#     print(f"Text: '{text}'")
#     print(f"Patterns: {patterns}")
#     print("Manual check:")
#     print("  u s h e r s")
#     print("  0 1 2 3 4 5")
#     print("  Expected: 'he' at 2-3, 'she' at 1-3, 'hers' at 2-5")
    
#     results = aho_corasick_search(text, patterns)
#     print("Results:")
#     for pattern, start, end in results:
#         print(f"  Pattern '{pattern}' found at position {start}-{end}")
    
#     print()
    
#     # Test case 2: Simple overlapping
#     text = "abccab"
#     patterns = ["a", "ab", "bc", "c"]
    
#     print("=== Test Case 2 ===")
#     print(f"Text: '{text}'")
#     print(f"Patterns: {patterns}")
    
#     results = aho_corasick_search(text, patterns)
#     print("Results:")
#     for pattern, start, end in results:
#         print(f"  Pattern '{pattern}' found at position {start}-{end}")
    
#     print()
    
#     # Test case 3: Classical example
#     text = "ahishers"
#     patterns = ["he", "she", "his", "hers"]
    
#     print("=== Test Case 3 ===")
#     print(f"Text: '{text}'")
#     print(f"Patterns: {patterns}")
    
#     results = aho_corasick_search(text, patterns)
#     print("Results:")
#     for pattern, start, end in results:
#         print(f"  Pattern '{pattern}' found at position {start}-{end}")
    
#     # Debugging function
#     def debug_aho_corasick(text, patterns):
#         print(f"\n=== Debug Info ===")
#         ac = AhoCorasick()
#         for pattern in patterns:
#             ac.add_pattern(pattern)
#         ac.build_failure_function()
        
#         print("Trie structure:")
#         for node in sorted(ac.trie.keys()):
#             print(f"  Node {node}: {dict(ac.trie[node])}")
        
#         print("Failure links:")
#         for node in sorted(ac.failure.keys()):
#             print(f"  Node {node} -> {ac.failure[node]}")
        
#         print("Output function:")
#         for node in sorted(ac.output.keys()):
#             if ac.output[node]:
#                 print(f"  Node {node}: {ac.output[node]}")
    
#     debug_aho_corasick("ushers", ["he", "she", "his", "hers"])
