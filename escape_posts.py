import json
from telegram.utils.helpers import escape_markdown

INPUT_FILE = "posts.json"
OUTPUT_FILE = "posts_escaped.json"

def escape_post_texts(posts):
    for post in posts:
        if "text" in post and post["text"]:
            post["text"] = escape_markdown(post["text"], version=2)
    return posts

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    escaped_posts = escape_post_texts(posts)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(escaped_posts, f, ensure_ascii=False, indent=2)

    print(f"✅ Fertig! Datei gespeichert unter: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
