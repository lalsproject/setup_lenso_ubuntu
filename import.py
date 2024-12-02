import mysql.connector
import time

def execute_batch(cursor, sql_statements, batch_size=10):
    failed_statements = []  # Untuk menyimpan pernyataan SQL yang gagal
    batch = []  # Batch SQL yang akan dijalankan
    for idx, statement in enumerate(sql_statements):
        statement = statement.strip()  # Menghapus spasi di awal dan akhir
        if statement:
            batch.append(statement)
        
        if len(batch) == batch_size or idx == len(sql_statements) - 1:
            try:
                cursor.execute(';'.join(batch))  # Menjalankan batch SQL sekaligus
                print(f"Sukses menjalankan batch {idx // batch_size + 1}")
            except Exception as e:
                print(f"Error pada batch {idx // batch_size + 1}, Error: {e}")
                failed_statements.extend(batch)  # Menyimpan pernyataan SQL yang gagal
            batch = []  # Kosongkan batch setelah dieksekusi

    return failed_statements


def retry_failed_statements(cursor, failed_statements, max_retry=3):
    retry_count = 0
    while failed_statements and retry_count < max_retry:
        print(f"Mencoba ulang pernyataan SQL yang gagal... (Percobaan {retry_count + 1})")
        remaining_failed_statements = []  # Untuk menyimpan SQL yang masih gagal

        for statement in failed_statements:
            try:
                cursor.execute(statement)
                print(f"Sukses menjalankan ulang: {statement}")
            except Exception as e:
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


def import_sql_file_in_batches(cursor, sql_file_path, batch_size=10):
    with open(sql_file_path, 'r') as file:
        sql_statements = file.read().split(';')  # Memisahkan tiap statement SQL berdasarkan tanda ";"
    
    failed_statements = execute_batch(cursor, sql_statements, batch_size=batch_size)

    if failed_statements:
        retry_failed_statements(cursor, failed_statements)


def main(sql_file_path, host, user, password, database, batch_size=10):
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = connection.cursor()

    try:
        import_sql_file_in_batches(cursor, sql_file_path, batch_size=batch_size)
        connection.commit()
    except Exception as e:
        print(f"Kesalahan saat mengimpor SQL: {e}")
        connection.rollback()  # Rollback jika terjadi error besar
    finally:
        cursor.close()
        connection.close()
        print("Proses impor SQL selesai.")


# Contoh penggunaan
sql_file_path = 'path_ke_berkas_sql.sql'  # Ganti dengan path ke berkas SQL Anda
host = 'localhost'  # Ganti dengan host database Anda
user = 'root'  # Ganti dengan user database Anda
password = 'password_anda'  # Ganti dengan password user Anda
database = 'nama_database'  # Ganti dengan nama database Anda
batch_size = 50  # Jumlah pernyataan SQL yang dijalankan per batch, sesuaikan dengan kemampuan server

main(sql_file_path, host, user, password, database, batch_size)
