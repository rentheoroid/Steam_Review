import requests
import csv
import time
import urllib.parse

def get_steam_reviews(app_id, limit=None):
    all_reviews = []
    cursor = '*'
    url_template = "https://store.steampowered.com/appreviews/{app_id}?json=1&filter=all&language=all&review_type=all&purchase_type=all&cursor={cursor}"

    print(f"Memulai pengambilan ulasan untuk App ID: {app_id}...")

    while True:
        encoded_cursor = urllib.parse.quote(cursor)
        url = url_template.format(app_id=app_id, cursor=encoded_cursor)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
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

        if limit is not None and total_reviews_so_far >= limit:
            print(f"Batas {limit} ulasan telah tercapai.")
            return all_reviews[:limit]

        next_cursor = data.get('cursor')
        if not next_cursor or next_cursor == cursor:
            print("Telah mencapai akhir dari semua ulasan.")
            break
        
        cursor = next_cursor
        time.sleep(1)

    return all_reviews

def save_reviews_to_csv(reviews, filename="steam_reviews.csv"):
    if not reviews:
        print("Tidak ada ulasan untuk disimpan.")
        return

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

            writer.writerow(fieldnames)

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
                    review.get('review').replace('\n', ' ').replace('\r', ''),
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
    APP_ID = 2124490  
    REVIEW_LIMIT = 5000

    all_game_reviews = get_steam_reviews(APP_ID, limit=REVIEW_LIMIT)

    if all_game_reviews:
        output_filename = f"steam_reviews_{APP_ID}.csv"
        save_reviews_to_csv(all_game_reviews, filename=output_filename)
