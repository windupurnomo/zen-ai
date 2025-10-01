"""
Main Application
Aplikasi untuk mengubah Natural Language (Bahasa Indonesia) menjadi SQL Query
untuk tabel todo(id, task, status)
"""

from intent_classifier import IntentClassifier
from sql_generator import SQLGenerator


class NL2SQL:
    def __init__(self):
        print("Initializing NL2SQL System...")
        print("Loading sentence transformer model...")
        self.classifier = IntentClassifier()
        self.generator = SQLGenerator()
        print("System ready!\n")

    def process(self, user_input: str):
        """
        Process natural language input dan generate SQL query

        Args:
            user_input: Kalimat dalam bahasa Indonesia
        """
        print(f"Input: {user_input}")
        print("-" * 60)

        # Klasifikasi intent
        intent, score = self.classifier.classify(user_input)

        if intent is None:
            print(f"Intent: TIDAK DIKENALI (confidence: {score:.3f})")
            print("SQL Query: -- Error: Intent tidak dapat diidentifikasi")
        else:
            print(f"Intent: {intent} (confidence: {score:.3f})")

            # Generate SQL query
            sql_query = self.generator.generate(intent, user_input)
            print(f"SQL Query: {sql_query}")

        print("=" * 60)
        print()


def main():
    # Initialize system
    nl2sql = NL2SQL()

    # Contoh penggunaan
    test_queries = [
        "Tampilkan semua task",
        "Lihat task yang sudah selesai",
        "Tampilkan task yang belum dikerjakan",
        "Tambah task belajar Python",
        "Buat task baru meeting dengan client",
        "Hapus task nomor 3",
        "Delete task id 5",
        "Update status task 2 jadi done",
        "Tandai task 4 sudah selesai",
        "Ganti status task 1 jadi pending"
    ]

    print("=" * 60)
    print("DEMO: Natural Language to SQL Query")
    print("=" * 60)
    print()

    for query in test_queries:
        nl2sql.process(query)

    # Interactive mode
    print("\n" + "=" * 60)
    print("MODE INTERAKTIF")
    print("=" * 60)
    print("Ketik 'exit' atau 'quit' untuk keluar\n")

    while True:
        try:
            user_input = input("Masukkan perintah: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'keluar']:
                print("Terima kasih! Sampai jumpa!")
                break

            nl2sql.process(user_input)

        except KeyboardInterrupt:
            print("\n\nTerima kasih! Sampai jumpa!")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")


if __name__ == "__main__":
    main()
