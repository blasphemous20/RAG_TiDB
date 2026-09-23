import json

import pandas as pd
from sentence_transformers import SentenceTransformer

from chat_bot import create_database_connection


def embed_knowledge(csv_path="data_knowledge.csv"):
    """Rebuild document embeddings when this script is run explicitly."""
    embedder = SentenceTransformer("BAAI/bge-m3")
    db = create_database_connection()
    curr = db.cursor()

    try:
        df = pd.read_csv(csv_path)
        print(f"Jumlah data dari CSV: {len(df)}")

        curr.execute("DELETE FROM documents")
        print("Data knowledge lama berhasil dihapus.")

        for index, row in df.iterrows():
            question = str(row["question"]).strip()
            answer = str(row["answer"]).strip()
            text = f"{question} {answer}"

            try:
                embedding_str = json.dumps(embedder.encode(text).tolist())
                curr.execute(
                    "INSERT INTO documents (text, embedding) VALUES (%s, %s)",
                    (text, embedding_str),
                )
                print(f"Data index-{index} berhasil ditambahkan.")
            except Exception as error:
                print(f"Data index-{index} error: {error}")
                print(f"Data index-{index} gagal ditambahkan.")

        db.commit()
        print("\nSemua knowledge berhasil diperbarui.")
    except Exception as error:
        db.rollback()
        print(f"\nTerjadi error: {error}")
        print("Perubahan database dibatalkan.")
        raise
    finally:
        curr.close()
        db.close()
        print("Koneksi database ditutup.")


if __name__ == "__main__":
    embed_knowledge()
