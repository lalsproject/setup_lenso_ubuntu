import mysql.connector
import time

# Daftar error code untuk tabel yang sudah ada
TABLE_EXISTS_ERROR_CODE = 1050

def execute_batch(cursor, connection, sql_statements, batch_size=10):
    failed_statements = []  # Untuk menyimpan pernyataan SQL yang gagal
    batch = []  # Batch SQL yang akan dijalankan
    for idx, statement in enumerate(sql_statements):
        statement = statement.strip()  # Menghapus spasi di awal dan akhir
        if statement:
            batch.append(statement)
        
        if len(batch) == batch_size or idx == len(sql_statements) - 1:
            for statement in batch:
                try:
                    cursor.execute(statement)  # Menjalankan pernyataan SQL satu per satu
                    connection.commit()  # Commit setiap statement
                    print(f"Sukses menjalankan: {statement}")
                except mysql.connector.Error as e:
                    if e.errno == TABLE_EXISTS_ERROR_CODE:
                        # Jika tabel sudah ada, abaikan error
                        print(f"Table sudah ada, dilewati: {e}")
                    else:
                        print(f"Error pada statement: {statement}, Error: {e}")
                        failed_statements.append(statement)  # Menyimpan pernyataan SQL yang gagal
            batch = []  # Kosongkan batch setelah dieksekusi

    return failed_statements


def retry_failed_statements(cursor, connection, failed_statements, max_retry=3):
    retry_count = 0
    while failed_statements and retry_count < max_retry:
        print(f"Mencoba ulang pernyataan SQL yang gagal... (Percobaan {retry_count + 1})")
        remaining_failed_statements = []  # Untuk menyimpan SQL yang masih gagal

        for statement in failed_statements:
            try:
                cursor.execute(statement)
                connection.commit()  # Commit setiap statement yang berhasil saat retry
                print(f"Sukses menjalankan ulang: {statement}")
            except mysql.connector.Error as e:
                if e.errno == TABLE_EXISTS_ERROR_CODE:
                    # Jika tabel sudah ada, abaikan error
                    print(f"Table sudah ada, dilewati: {e}")
                else:
                    print(f"Error saat mencoba ulang: {statement}, Error: {e}")
                    remaining_failed_statements.append(statement)  # Menyimpan SQL yang masih gagal

        failed_statements = remaining_failed_statements
        retry_count += 1

        if failed_statements:
            print(f"{len(failed_statements)} pernyataan SQL masih gagal. Coba lagi dalam beberapa detik.")
            time.sleep(min(5 * retry_count, 60))  # Tunggu lebih lama di setiap percobaan

    if not failed_statements:
        print("Semua pernyataan SQL berhasil diimpor!")
    else:
        print(f"Gagal menjalankan {len(failed_statements)} pernyataan SQL setelah {max_retry} percobaan.")


def import_sql_file_in_batches(cursor, connection, sql_file_path, batch_size=10):
    with open(sql_file_path, 'r') as file:
        sql_statements = file.read().split(';')  # Memisahkan tiap statement SQL berdasarkan tanda ";"
    
    failed_statements = execute_batch(cursor, connection, sql_statements, batch_size=batch_size)

    if failed_statements:
        retry_failed_statements(cursor, connection, failed_statements)

def check_and_create_user(cursor, connection, username="ic", host="%"):
    """Fungsi untuk mengecek apakah user sudah ada, jika belum tambahkan user dengan full privilege."""
    try:
        # Cek apakah user sudah ada di MariaDB
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{username}' AND host = '{host}')")
        user_exists = cursor.fetchone()[0]
        
        if not user_exists:
            # User belum ada, buat user baru dengan full privileges
            print(f"User '{username}' belum terdaftar, menambahkan user baru...")
            cursor.execute(f"CREATE USER '{username}'@'{host}' IDENTIFIED BY 'password';")
            cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{username}'@'{host}' WITH GRANT OPTION;")
            cursor.execute("FLUSH PRIVILEGES;")
            connection.commit()
            print(f"User '{username}' berhasil ditambahkan dengan akses penuh.")
        else:
            print(f"User '{username}' sudah terdaftar, tidak perlu ditambahkan.")
    
    except mysql.connector.Error as e:
        print(f"Kesalahan saat memeriksa atau membuat user: {e}")

def main(sql_file_path, host, user, password, database, batch_size=10):
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = connection.cursor()

    try:
        # Cek dan buat user jika belum ada
        check_and_create_user(cursor, connection)

        # Impor SQL dari berkas
        import_sql_file_in_batches(cursor, connection, sql_file_path, batch_size=batch_size)
    except Exception as e:
        print(f"Kesalahan saat mengimpor SQL: {e}")
    finally:
        cursor.close()
        connection.close()
        print("Proses impor SQL selesai.")


# Contoh penggunaan
sql_file_path = 'backup_struktur_idm_b_2024-12-02.sql'  # Ganti dengan path ke berkas SQL Anda
host = 'localhost'  # Ganti dengan host database Anda
user = 'root'  # Ganti dengan user database Anda
password = '12'  # Ganti dengan password user Anda
database = 'idm_b'  # Ganti dengan nama database Anda
batch_size = 50  # Jumlah pernyataan SQL yang dijalankan per batch, sesuaikan dengan kemampuan server

main(sql_file_path, host, user, password, database, batch_size)
