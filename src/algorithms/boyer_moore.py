def bad_char_heuristic(pattern):
    """
    Menghitung tabel bad character heuristic menggunakan dictionary.
    Menyimpan posisi terakhir setiap karakter dalam pola.
    """
    m = len(pattern)
    bad_char = {}
    
    # Iterasi dari kiri ke kanan untuk menyimpan posisi terakhir setiap karakter
    for i in range(m):
        bad_char[pattern[i]] = i
    
    return bad_char

def boyer_moore_search(text, pattern):
    """
    Implementasi algoritma Boyer-Moore dengan bad character heuristic.
    Mengembalikan daftar indeks di mana pola ditemukan dalam teks.
    """
    n = len(text)
    m = len(pattern)

    # Edge cases
    if m == 0:
        return []
    if n == 0 or n < m:
        return []

    bad_char = bad_char_heuristic(pattern)
    
    s = 0  # shift dari pola terhadap teks
    matches = []

    while s <= (n - m):
        j = m - 1

        # Cocokkan karakter dari kanan ke kiri
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1

        # Jika pola ditemukan (j menjadi -1)
        if j < 0:
            matches.append(s)
            # Geser berdasarkan karakter setelah match (jika ada)
            if s + m < n:
                next_char = text[s + m]
                s += m - bad_char.get(next_char, -1)
            else:
                s += 1  # Jika sudah di akhir teks
        else:
            # Karakter tidak cocok pada posisi j
            mismatched_char = text[s + j]
            
            # Hitung shift berdasarkan bad character rule
            # j adalah posisi dalam pola, bad_char.get() memberikan posisi terakhir karakter
            shift = j - bad_char.get(mismatched_char, -1)
            
            # Pastikan shift minimal 1 untuk menghindari loop tak hingga
            s += max(1, shift)
            
    return matches