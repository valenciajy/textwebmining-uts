# =============================================
# SENTIMENT ANALYSIS SHOPEE REVIEWS - INDOBERT
# =============================================

import pandas as pd
import re
import unicodedata
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# 1️⃣ Load dataset Shopee reviews
reviews = pd.read_csv("shopee_reviews_3.csv")
print("Jumlah data awal:", len(reviews))

text_column = "text"

# 2️⃣ Bersihkan data: hapus NaN atau teks kosong
def normalize_strong(s):
    """Normalize unicode, remove invisible chars, collapse spaces, strip surrounding quotes."""
    if pd.isna(s):
        return ""
    s = str(s)
    # normalize unicode
    s = unicodedata.normalize("NFKC", s)
    # replace common invisible / whitespace characters with space
    for ch in ["\u00a0", "\u200b", "\u200c", "\u200d", "\ufeff"]:
        s = s.replace(ch, " ")
    # replace CR/LF/TAB with space
    s = s.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    # strip surrounding quotes and fancy quotes
    s = s.strip().strip('"\'' + "“”‘’«»`")
    # collapse multiple spaces
    s = re.sub(r"\s+", " ", s)
    return s

def is_na_like(s):
    """Return True if s is 'N/A'-like after normalization."""
    s_norm = normalize_strong(s).lower().strip()
    # remove all non-alphanumeric to convert 'N/A' -> 'na'
    s_alnum = re.sub(r'[^a-z0-9]', '', s_norm)
    # common NA-like tokens
    na_tokens = {"", "na", "n", "none", "null", "nan"}
    return s_alnum in na_tokens

# --- create normalized columns for inspection ---
reviews["_text_norm"] = reviews[text_column].apply(normalize_strong)
reviews["_text_alnum"] = reviews["_text_norm"].str.lower().apply(lambda t: re.sub(r'[^a-z0-9]', '', t))

# --- debug: show unique small sample of problematic rows ---
mask_na = reviews["_text_alnum"].isin({"", "na", "n", "none", "null", "nan"})
print("Count detected as N/A-like:", mask_na.sum())
if mask_na.sum() > 0:
    print("\nContoh baris yang terdeteksi N/A-like (repr):")
    # show index + repr to reveal invisible chars
    sample = reviews.loc[mask_na, text_column].head(20).apply(lambda x: repr(x))
    print(sample.to_string())

# if none detected, try to show rows that are short or unusual to help debug
if mask_na.sum() == 0:
    print("\nTidak ada yang cocok N/A-like berdasarkan rule awal.")
    # show top 20 distinct small-length entries to inspect
    small = reviews[text_column].astype(str).apply(lambda x: x.strip()).loc[reviews[text_column].astype(str).str.strip().str.len() <= 5].unique()
    print("Contoh entries dengan length <=5:", small[:20])

# --- drop the N/A-like rows ---
reviews_clean = reviews.loc[~mask_na].copy().reset_index(drop=True)
print("Jumlah data setelah dibersihkan:", len(reviews_clean))

# optionally drop the helper columns before further processing
reviews_clean = reviews_clean.drop(columns=["_text_norm", "_text_alnum"])
# continue processing with reviews_clean instead of reviews

# 3️⃣ Load pre-trained IndoBERT Sentiment Model
model_name = "mdhugol/indonesia-bert-sentiment-classification"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer,
    truncation=True,
    padding=True,
)

# 4️⃣ Jalankan analisis sentimen (dengan mapping label)
results = []
for text in reviews_clean[text_column]:
    try:
        result = sentiment_pipeline(text[:512])[0]
        label = result["label"]

        # Mapping label ke sentimen asli
        if label == "LABEL_0":
            results.append("Positive")
        elif label == "LABEL_1":
            results.append("Negative")
        elif label == "LABEL_2":
            results.append("Neutral")
        else:
            results.append("ERROR")
    except Exception:
        results.append("ERROR")

# 5️⃣ Simpan hasil
reviews_clean["sentiment"] = results
output_path = "hasil_sentimen_pretrained_clean_3.csv"
reviews_clean.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\n✅ Analisis selesai! Hasil disimpan di:", output_path)
print("\nDistribusi Sentimen:")
print(reviews_clean["sentiment"].value_counts())
