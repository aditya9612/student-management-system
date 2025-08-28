import pandas as pd
import random

def make_phone():
    return f"9{random.randint(100000000, 999999999)}"

data = {
    'name': [f'Student{i}' for i in range(1, 6)],
    'email': [f'student{i}@example.com' for i in range(1, 6)],
    'phone': [make_phone() for _ in range(5)],
    'password': [f'pass{i}123' for i in range(1, 6)]
}
df = pd.DataFrame(data)
df.to_excel('sample_students.xlsx', index=False)
print('Excel file created: sample_students.xlsx')
