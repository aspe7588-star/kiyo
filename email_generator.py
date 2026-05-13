"""
Bot Generator Otomatis Email
=============================
Fitur:
- Generate email acak dengan berbagai format nama
- Support custom domain
- Bulk generation (banyak email sekaligus)
- Export ke file TXT/CSV
- Format email: firstname.lastname, firstname_lastname, firstnamelastname, dll.
"""

import random
import string
import csv
import os
from datetime import datetime


# Data nama untuk generate email
FIRST_NAMES = [
    "andi", "budi", "citra", "dewi", "eko", "fani", "gita", "hadi",
    "indah", "joko", "kartika", "lina", "mira", "nanda", "oki",
    "putri", "reza", "sari", "tono", "udin", "vina", "wati",
    "xena", "yuni", "zaki", "ahmad", "bambang", "cahya", "dian",
    "fitri", "galih", "hendra", "irfan", "jasmine", "kevin",
    "lisa", "maya", "nina", "oscar", "prima", "queen", "rani",
    "surya", "tika", "umi", "vera", "winda", "yoga", "zahra"
]

LAST_NAMES = [
    "pratama", "santoso", "wijaya", "kusuma", "hidayat", "putra",
    "sari", "utami", "lestari", "wibowo", "nugroho", "setiawan",
    "handoko", "susanto", "gunawan", "hartono", "suryadi", "permana",
    "saputra", "ramadhan", "firmansyah", "kurniawan", "adriansyah",
    "mahendra", "budiman", "cahyono", "darmawan", "effendi",
    "fajar", "ginting", "harahap", "iskandar", "junaedi"
]

DEFAULT_DOMAINS = [
    "dcctb.com",
    "nucledt.com",
    "emailnax.com",
    "csjunkies.com",
    "zlorkun.com",
    "finews.biz",
    "hfraja.com",
    "rfcdrive.com",
    "exdonuts.com",
    "trevomj.com",
    "stvbndge.com",
    "wywnxa.com",
    "trickwe.com",
    "bfrfrr.com",
    "dfrfrr.com"
]

EMAIL_FORMATS = [
    "firstname.lastname",      # andi.pratama@domain.com
    "firstname_lastname",      # andi_pratama@domain.com
    "firstnamelastname",       # andipratama@domain.com
    "firstlast",               # andipratama@domain.com (short)
    "f.lastname",              # a.pratama@domain.com
    "firstname.l",             # andi.p@domain.com
    "firstname+number",        # andi123@domain.com
    "firstname.lastname+number" # andi.pratama99@domain.com
]


def generate_random_string(length=5):
    """Generate string acak dari huruf kecil."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def generate_random_number(min_val=1, max_val=999):
    """Generate angka acak."""
    return random.randint(min_val, max_val)


def generate_email(first_name=None, last_name=None, domain=None, email_format=None):
    """
    Generate satu email acak.
    
    Args:
        first_name: Nama depan (opsional, akan random jika kosong)
        last_name: Nama belakang (opsional, akan random jika kosong)
        domain: Domain email (opsional, akan random jika kosong)
        email_format: Format email (opsional, akan random jika kosong)
    
    Returns:
        String email yang di-generate
    """
    fname = first_name or random.choice(FIRST_NAMES)
    lname = last_name or random.choice(LAST_NAMES)
    dom = domain or random.choice(DEFAULT_DOMAINS)
    fmt = email_format or random.choice(EMAIL_FORMATS)
    
    number = generate_random_number()
    
    if fmt == "firstname.lastname":
        local_part = f"{fname}.{lname}"
    elif fmt == "firstname_lastname":
        local_part = f"{fname}_{lname}"
    elif fmt == "firstnamelastname":
        local_part = f"{fname}{lname}"
    elif fmt == "firstlast":
        local_part = f"{fname}{lname[:3]}"
    elif fmt == "f.lastname":
        local_part = f"{fname[0]}.{lname}"
    elif fmt == "firstname.l":
        local_part = f"{fname}.{lname[0]}"
    elif fmt == "firstname+number":
        local_part = f"{fname}{number}"
    elif fmt == "firstname.lastname+number":
        local_part = f"{fname}.{lname}{number}"
    else:
        local_part = f"{fname}.{lname}"
    
    return f"{local_part}@{dom}"


def bulk_generate(count=10, domain=None, email_format=None, unique=True):
    """
    Generate banyak email sekaligus.
    
    Args:
        count: Jumlah email yang ingin di-generate
        domain: Domain khusus (opsional)
        email_format: Format khusus (opsional)
        unique: Pastikan semua email unik (default: True)
    
    Returns:
        List of email strings
    """
    emails = set() if unique else []
    max_attempts = count * 10  # Hindari infinite loop
    attempts = 0
    
    while (len(emails) < count) and (attempts < max_attempts):
        email = generate_email(domain=domain, email_format=email_format)
        if unique:
            emails.add(email)
        else:
            emails.append(email)
        attempts += 1
    
    return list(emails) if unique else emails


def export_to_txt(emails, filename=None):
    """Export daftar email ke file TXT."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emails_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        for email in emails:
            f.write(email + '\n')
    
    print(f"[OK] {len(emails)} email berhasil disimpan ke: {filename}")
    return filename


def export_to_csv(emails, filename=None):
    """Export daftar email ke file CSV."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emails_{timestamp}.csv"
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["No", "Email"])
        for i, email in enumerate(emails, 1):
            writer.writerow([i, email])
    
    print(f"[OK] {len(emails)} email berhasil disimpan ke: {filename}")
    return filename


def display_menu():
    """Tampilkan menu utama."""
    print("\n" + "=" * 50)
    print("   BOT GENERATOR OTOMATIS EMAIL")
    print("=" * 50)
    print("\n[1] Generate 1 email acak")
    print("[2] Generate banyak email (bulk)")
    print("[3] Generate dengan custom domain")
    print("[4] Generate dengan format tertentu")
    print("[5] Generate & export ke file")
    print("[6] Lihat format email tersedia")
    print("[0] Keluar")
    print("\n" + "-" * 50)


def show_formats():
    """Tampilkan format email yang tersedia."""
    print("\n Format Email Tersedia:")
    print("-" * 40)
    for i, fmt in enumerate(EMAIL_FORMATS, 1):
        example = generate_email(
            first_name="andi",
            last_name="pratama",
            domain="gmail.com",
            email_format=fmt
        )
        print(f"  [{i}] {fmt}")
        print(f"      Contoh: {example}")
    print()


def main():
    """Fungsi utama bot."""
    print("\n Selamat datang di Bot Generator Otomatis Email!")
    print(" Bot ini akan membantu Anda membuat email secara otomatis.\n")
    
    while True:
        display_menu()
        choice = input("\nPilih menu [0-6]: ").strip()
        
        if choice == "0":
            print("\n Terima kasih! Sampai jumpa.\n")
            break
        
        elif choice == "1":
            print("\n--- Generate 1 Email Acak ---")
            email = generate_email()
            print(f"\n   Email: {email}\n")
        
        elif choice == "2":
            print("\n--- Generate Banyak Email ---")
            try:
                count = int(input("Jumlah email yang ingin di-generate: "))
                if count <= 0:
                    print("[!] Jumlah harus lebih dari 0!")
                    continue
                if count > 10000:
                    print("[!] Maksimal 10.000 email per generate!")
                    continue
            except ValueError:
                print("[!] Masukkan angka yang valid!")
                continue
            
            emails = bulk_generate(count=count)
            print(f"\n {len(emails)} Email berhasil di-generate:\n")
            for i, email in enumerate(emails[:20], 1):
                print(f"  [{i:3d}] {email}")
            if len(emails) > 20:
                print(f"  ... dan {len(emails) - 20} email lainnya.")
            print()
        
        elif choice == "3":
            print("\n--- Generate dengan Custom Domain ---")
            custom_domain = input("Masukkan domain (contoh: perusahaan.com): ").strip()
            if not custom_domain or '.' not in custom_domain:
                print("[!] Domain tidak valid!")
                continue
            try:
                count = int(input("Jumlah email: "))
            except ValueError:
                print("[!] Masukkan angka yang valid!")
                continue
            
            emails = bulk_generate(count=count, domain=custom_domain)
            print(f"\n {len(emails)} Email dengan domain @{custom_domain}:\n")
            for i, email in enumerate(emails[:20], 1):
                print(f"  [{i:3d}] {email}")
            if len(emails) > 20:
                print(f"  ... dan {len(emails) - 20} email lainnya.")
            print()
        
        elif choice == "4":
            print("\n--- Generate dengan Format Tertentu ---")
            show_formats()
            try:
                fmt_choice = int(input("Pilih format [1-8]: ")) - 1
                if fmt_choice < 0 or fmt_choice >= len(EMAIL_FORMATS):
                    print("[!] Pilihan tidak valid!")
                    continue
            except ValueError:
                print("[!] Masukkan angka yang valid!")
                continue
            
            try:
                count = int(input("Jumlah email: "))
            except ValueError:
                print("[!] Masukkan angka yang valid!")
                continue
            
            selected_format = EMAIL_FORMATS[fmt_choice]
            emails = bulk_generate(count=count, email_format=selected_format)
            print(f"\n {len(emails)} Email format '{selected_format}':\n")
            for i, email in enumerate(emails[:20], 1):
                print(f"  [{i:3d}] {email}")
            if len(emails) > 20:
                print(f"  ... dan {len(emails) - 20} email lainnya.")
            print()
        
        elif choice == "5":
            print("\n--- Generate & Export ke File ---")
            try:
                count = int(input("Jumlah email: "))
            except ValueError:
                print("[!] Masukkan angka yang valid!")
                continue
            
            domain = input("Custom domain (kosongkan untuk random): ").strip() or None
            if domain and '.' not in domain:
                print("[!] Domain tidak valid!")
                continue
            
            emails = bulk_generate(count=count, domain=domain)
            
            print("\nFormat export:")
            print("  [1] TXT")
            print("  [2] CSV")
            export_choice = input("Pilih format [1-2]: ").strip()
            
            if export_choice == "1":
                export_to_txt(emails)
            elif export_choice == "2":
                export_to_csv(emails)
            else:
                print("[!] Pilihan tidak valid!")
        
        elif choice == "6":
            show_formats()
        
        else:
            print("\n[!] Pilihan tidak valid! Silakan pilih 0-6.")


if __name__ == "__main__":
    main()
