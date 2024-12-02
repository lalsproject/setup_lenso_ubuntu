import mysql.connector
import time

sql_file_path = 'backup_struktur_new_data_master_2024-12-02.sql'  # Ganti dengan path ke berkas SQL Anda
host = 'localhost'  # Ganti dengan host database Anda
user = 'root'  # Ganti dengan user database Anda
password = '12'  # Ganti dengan password user Anda
database = 'new_data_master'  # Ganti dengan nama database Anda

connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

def import_sql_file(cursor, sql_file_path):
    with open(sql_file_path, 'r') as file:
        sql_statements = file.read().split(';')  # Memisahkan tiap statement SQL berdasarkan tanda ";"
        
    failed_statements = []  # Daftar untuk menyimpan SQL yang gagal
    i = 1;
    for statement in sql_statements:
        statement = statement.strip()  # Menghapus spasi di awal dan akhir
        if statement:
            try:
                cursor.execute(statement)
                print(f"Sukses menjalankan: {i}")
                connection.commit()
            except Exception as e:
                print(f"Error menjalankan: {i}, Error: {e}")
                failed_statements.append(statement)  # Menyimpan pernyataan SQL yang gagal
        i = i+1
    return failed_statements


def retry_failed_statements(cursor, failed_statements):
    # Looping terus sampai semua SQL berhasil
    while failed_statements:
        print("Mencoba ulang pernyataan SQL yang gagal...")
        remaining_failed_statements = []  # Untuk menyimpan statement yang masih gagal

        for statement in failed_statements:
            try:
                cursor.execute(statement)
                print(f"Sukses menjalankan ulang: {statement}")
            except Exception as e:
                print(f"Error saat mencoba ulang: {statement}, Error: {e}")
                remaining_failed_statements.append(statement)  # Menyimpan SQL yang masih gagal

        if not remaining_failed_statements:
            print("Semua pernyataan SQL berhasil diimpor!")
            break
        else:
            print(f"{len(remaining_failed_statements)} pernyataan SQL masih gagal. Coba lagi dalam beberapa detik.")
            failed_statements = remaining_failed_statements
            time.sleep(5)  # Tunggu 5 detik sebelum mencoba ulang


def main(sql_file_path, host, user, password, database):
    
    cursor = connection.cursor()

    failed_statements = import_sql_file(cursor, sql_file_path)

    if failed_statements:
        retry_failed_statements(cursor, failed_statements)

    connection.commit()
    cursor.close()
    connection.close()
    print("Proses impor SQL selesai.")


# Contoh penggunaan


main(sql_file_path, host, user, password, database)
