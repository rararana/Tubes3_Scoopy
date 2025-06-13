from faker import Faker

# Inisialisasi Faker
fake = Faker()

# Rentang ID
start_id = 200
end_id = 230

# Fungsi untuk menghasilkan query SQL
def generate_sql(start_id, end_id):
    sql_query = "INSERT INTO ApplicantProfile (id, first_name, last_name, date_of_birth, address, phone_number) VALUES\n"
    values = []
    
    for i in range(start_id, end_id + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=60).strftime('%Y-%m-%d')
        address = fake.address().replace("\n", ", ")
        phone_number = fake.phone_number()
        
        values.append(f"({i}, '{first_name}', '{last_name}', '{dob}', '{address}', '{phone_number}')")
    
    sql_query += ",\n".join(values) + ";"
    return sql_query

# Cetak hasilnya
sql_output = generate_sql(start_id, end_id)
print(sql_output)
