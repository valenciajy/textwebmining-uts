import pandas as pd
import re

# 1. Load dataset Shopee reviews
reviews = pd.read_csv("D:/texwebmining_proyek_UTS/shopee_reviews.csv")

# 2. Load InSet Lexicon
def load_inset(positive_path, negative_path):
    lexicon = {}
    
    # Baca positif
    with open(positive_path, encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            parts = line.strip().split("\t")  # pake tab sebagai pemisah
            if len(parts) >= 2:
                word, score = parts[0], parts[1]
                try:
                    lexicon[word] = int(score)
                except ValueError:
                    continue  # skip kalau bukan angka
    
    # Baca negatif
    with open(negative_path, encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                word, score = parts[0], parts[1]
                try:
                    lexicon[word] = int(score)
                except ValueError:
                    continue
    
    return lexicon

# 3. Text cleaning
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)       # hapus URL
    text = re.sub(r'[^a-z\s]', ' ', text)     # hapus simbol & angka
    text = re.sub(r'\s+', ' ', text).strip()  # hapus spasi berlebih
    return text

# 4. Sentiment scoring
def sentiment_inset(text, lexicon):
    text = clean_text(text)
    words = text.split()
    total_score = 0
    matched_words = []
    
    for w in words:
        if w in lexicon:
            score = lexicon[w]
            total_score += score
            matched_words.append((w, score))
    
    # Debug (bisa di-comment kalau sudah yakin)
    print(f"Matched words: {matched_words} | Total score: {total_score}")
    
    if total_score > 0:
        return "Positive"
    elif total_score < 0:
        return "Negative"
    else:
        return "Neutral"

# 5. Load lexicon
lex = load_inset("D:/texwebmining_proyek_UTS/positive.tsv",
                 "D:/texwebmining_proyek_UTS/negative.tsv")

# 6. Apply sentiment analysis
reviews["sentiment"] = reviews["text"].apply(lambda t: sentiment_inset(t, lex))

# 7. Simpan hasil ke CSV
output_path = "D:/texwebmining_proyek_UTS/shopee_reviews_with_sentiment.csv"
reviews.to_csv(output_path, index=False, encoding="utf-8-sig")

print(reviews[["text", "sentiment"]].head())
print(f"\n✅ Hasil sudah disimpan di {output_path}")
