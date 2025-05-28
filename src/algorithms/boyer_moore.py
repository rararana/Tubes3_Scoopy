def bad_char_heuristic(pattern):
    """
    menghitung tabel bad character heuristic menggunakan dictionary
    untuk mendukung berbagai karakter Unicode
    """
    m = len(pattern)
    bad_char = {}  # inisialisasi sebagai dictionary kosong
    for i in range(m):
        bad_char[pattern[i]] = i 
    return bad_char

def boyer_moore_search(text, pattern):
    """
    mengembalikan daftar indeks di mana pola ditemukan
    """
    n = len(text)
    m = len(pattern)

    if m == 0:
        return []
    if n == 0 or n < m:
        return []

    bad_char = bad_char_heuristic(pattern)
    
    s = 0  # s adalah shift dari pola sehubungan dengan teks
    matches = []

    while s <= (n - m):
        j = m - 1

        # kurangi indeks j dari pola selama karakter cocok
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1

        # jika pola ditemukan (j menjadi -1)
        if j < 0:
            matches.append(s)
            #
            char_to_check = text[s + m] if (s + m) < n else '' # karakter yang akan digeser
            s += (m - bad_char.get(char_to_check, -1) if char_to_check else 1)
        else:
            # geser pola sehingga karakter yang tidak cocok dalam teks sejajar
            # dengan kemunculan terakhir dari karakter tersebut dalam pola
            # atau geser 1 jika karakter tidak ada dalam pola
            char_to_check = text[s + j]
            s += max(1, j - bad_char.get(char_to_check, -1))
            
    return matches
