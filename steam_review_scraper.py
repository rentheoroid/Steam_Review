import requests
import csv
import time
import urllib.parse

def get_steam_reviews(app_id, limit=None):
    """
    Mengambil ulasan game dari Steam menggunakan API JSON-nya.

    Args:
        app_id (int): ID aplikasi game di Steam.
        limit (int, optional): Batas jumlah maksimum ulasan yang akan diambil.
                               Jika None, akan mencoba mengambil semua ulasan. Defaults to None.

    Returns:
        list: Daftar ulasan, di mana setiap ulasan adalah sebuah dictionary.
    """
    all_reviews = []
    cursor = '*'  # Kursor awal untuk paginasi
    url_template = "https://store.steampowered.com/appreviews/{app_id}?json=1&filter=all&language=all&review_type=all&purchase_type=all&cursor={cursor}"

    print(f"Memulai pengambilan ulasan untuk App ID: {app_id}...")

    while True:
        # Meng-encode kursor agar aman untuk URL
        encoded_cursor = urllib.parse.quote(cursor)
        url = url_template.format(app_id=app_id, cursor=encoded_cursor)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Cek jika ada error HTTP
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error saat melakukan request: {e}")
            break
        except ValueError:
            print("Gagal mem-parsing JSON. Mungkin ada masalah dengan respons dari Steam.")
            break

        if data.get('success') != 1:
            print(f"API request gagal. Pesan dari Steam: {data.get('success')}")
            break

        reviews = data.get('reviews', [])
        if not reviews:
            print("Tidak ada ulasan lagi yang ditemukan.")
            break

        for review in reviews:
            all_reviews.append(review)

        num_fetched = len(reviews)
        total_reviews_so_far = len(all_reviews)
        print(f"Berhasil mengambil {num_fetched} ulasan. Total ulasan sejauh ini: {total_reviews_so_far}")

        # Cek apakah sudah mencapai batas yang ditentukan
        if limit is not None and total_reviews_so_far >= limit:
            print(f"Batas {limit} ulasan telah tercapai.")
            return all_reviews[:limit]

        # Ambil kursor berikutnya untuk halaman selanjutnya
        next_cursor = data.get('cursor')
        if not next_cursor or next_cursor == cursor:
            print("Telah mencapai akhir dari semua ulasan.")
            break
        
        cursor = next_cursor

        # Jeda sejenak agar tidak membebani server Steam
        time.sleep(1)

    return all_reviews

def save_reviews_to_csv(reviews, filename="steam_reviews.csv"):
    """
    Menyimpan daftar ulasan ke dalam file CSV.

    Args:
        reviews (list): Daftar ulasan yang akan disimpan.
        filename (str): Nama file output CSV.
    """
    if not reviews:
        print("Tidak ada ulasan untuk disimpan.")
        return

    # Mendefinisikan kolom yang ingin disimpan
    fieldnames = [
        'recommendationid',
        'author_steamid',
        'author_num_games_owned',
        'author_num_reviews',
        'author_playtime_forever',
        'author_playtime_last_two_weeks',
        'language',
        'review',
        'timestamp_created',
        'timestamp_updated',
        'voted_up',
        'votes_up',
        'votes_funny',
        'weighted_vote_score',
        'steam_purchase',
        'received_for_free'
    ]

    print(f"\nMenyimpan {len(reviews)} ulasan ke dalam file '{filename}'...")

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Menulis header
            writer.writerow(fieldnames)

            # Menulis data ulasan
            for review in reviews:
                author_info = review.get('author', {})
                row = [
                    review.get('recommendationid'),
                    author_info.get('steamid'),
                    author_info.get('num_games_owned'),
                    author_info.get('num_reviews'),
                    author_info.get('playtime_forever'),
                    author_info.get('playtime_last_two_weeks'),
                    review.get('language'),
                    review.get('review').replace('\n', ' ').replace('\r', ''), # Membersihkan newlines
                    review.get('timestamp_created'),
                    review.get('timestamp_updated'),
                    review.get('voted_up'),
                    review.get('votes_up'),
                    review.get('votes_funny'),
                    review.get('weighted_vote_score'),
                    review.get('steam_purchase'),
                    review.get('received_for_free')
                ]
                writer.writerow(row)
        print("Proses penyimpanan selesai!")
    except IOError as e:
        print(f"Error saat menulis ke file: {e}")


if __name__ == "__main__":
    # Ganti APP_ID dengan ID game yang Anda inginkan
    # Contoh dari link Anda: https://steamcommunity.com/app/2124490/... -> APP_ID = 2124490
    APP_ID = 2124490  

    # Ganti REVIEW_LIMIT jika Anda hanya ingin mengambil sejumlah ulasan tertentu
    # Atur ke None untuk mencoba mengambil semua ulasan (bisa memakan waktu lama)
    REVIEW_LIMIT = 5000  # Contoh: hanya mengambil 500 ulasan pertama

    # Panggil fungsi untuk mendapatkan ulasan
    all_game_reviews = get_steam_reviews(APP_ID, limit=REVIEW_LIMIT)

    # Simpan ulasan ke file CSV
    if all_game_reviews:
        output_filename = f"steam_reviews_{APP_ID}-part2.csv"
        save_reviews_to_csv(all_game_reviews, filename=output_filename)
