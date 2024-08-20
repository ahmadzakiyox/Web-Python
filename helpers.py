import os
import pandas as pd
from re import findall
from pytz import timezone
from datetime import datetime

def check_number(path):
  numbers = []

  with open(path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

  for line in lines:
    line = line.strip().replace('+', '')
    line = line.split()
    for l in line:
      if l.isdigit() and len(l) > 10:
        numbers.append(l)

  return numbers

def contact_to_vcf(admin_list, navy_list, client_list, admin_name, navy_name, client_name, file_name, option, totalc, name_number): 
  admin_contacts = [con.strip() for con in admin_list.split('\n') if con.replace(' ', '').replace('+', '').strip().isdigit()]
  navy_contacts = [con.strip() for con in navy_list.split('\n') if con.replace(' ', '').replace('+', '').strip().isdigit()]
  client_contacts = [con.strip() for con in client_list.split('\n') if con.replace(' ', '').replace('+', '').strip().isdigit()]
  vcf_files = []
  vcard_entries = []

  if admin_contacts:
    countc = 0

    for number in admin_contacts:
      countc+=1
      cname = f"{admin_name}-{countc}" if name_number == '2' else f"{admin_name} {countc}"
      vcard_entry = f"BEGIN:VCARD\nVERSION:3.0\nFN:{cname}\nTEL;TYPE=CELL:+{number}\nEND:VCARD"
      vcard_entries.append(vcard_entry)
    
    if option == '2':
      admin_file = f'files/{file_name}-admin.vcf'
      vcf_files.append(admin_file)
  
      with open(admin_file, 'w', encoding='utf-8') as vcard_file:
        for entry in vcard_entries:
            vcard_file.write(entry + "\n")

      vcard_entries = []

  if navy_contacts:
    countc = 0

    for number in navy_contacts:
      countc+=1
      cname = f"{navy_name}-{countc}" if name_number == '2' else f"{navy_name} {countc}"
      vcard_entry = f"BEGIN:VCARD\nVERSION:3.0\nFN:{cname}\nTEL;TYPE=CELL:+{number}\nEND:VCARD"
      vcard_entries.append(vcard_entry)

    if option == '2':
      navy_file = f'files/{file_name}-navy.vcf'
      vcf_files.append(navy_file)
  
      with open(navy_file, 'w', encoding='utf-8') as vcard_file:
        for entry in vcard_entries:
            vcard_file.write(entry + "\n")

      vcard_entries = []

  if option == '3':
    new_name = f'files/{file_name} admin&navy.vcf'
    vcf_files.append(new_name)

    with open(new_name, 'w', encoding='utf-8') as vcard_file:
      for entry in vcard_entries:
          vcard_file.write(entry + "\n")

    vcard_entries = []

  if client_contacts:
    countc = 0

    for number in client_contacts:
      countc+=1
      cname = f"{client_name}-{countc}" if name_number == '2' else f"{client_name} {countc}"
      vcard_entry = f"BEGIN:VCARD\nVERSION:3.0\nFN:{cname}\nTEL;TYPE=CELL:+{number}\nEND:VCARD"
      vcard_entries.append(vcard_entry)

    if option == '2':
      client_file = f'files/{file_name}-client.vcf'
      vcf_files.append(client_file)
  
      with open(client_file, 'w', encoding='utf-8') as vcard_file:
        for entry in vcard_entries:
            vcard_file.write(entry + "\n")

      vcard_entries = []
    elif option == '3':
      split_client = split(vcard_entries, totalc)

      vcount = 1
      for vcard in split_client:
        vcf_name = f"files/{file_name} client {vcount}.vcf"
        vcf_files.append(vcf_name)
        
        with open(vcf_name, 'w', encoding='utf-8') as vcard_file:
          for entry in vcard:
            vcard_file.write(entry + "\n")
        
        vcount+=1

      vcard_entries = []

  if vcard_entries:
    new_file = f"files/{file_name}.vcf"
    vcf_files.append(new_file)

    with open(new_file, 'w', encoding='utf-8') as vcard_file:
        for entry in vcard_entries:
            vcard_file.write(entry + "\n")

  return vcf_files

def is_admin(session):
  return False if session.get('role') != 'admin' else True

def is_login(session):
  return False if 'username' not in session else True

def is_user_valid(expired):
  expired = datetime.strptime(expired, '%Y-%m-%dT%H:%M')
  wib = timezone('Asia/Jakarta')
  now = datetime.now(wib)
  expired = wib.localize(expired)

  return False if now > expired else True

def remove_files(file_list):
  for file in file_list:
    if os.path.exists(file):
      os.remove(file)

def split(arr, num):
  return [arr[x:x+num] for x in range(0, len(arr), num)]

def txt_to_vcf(txt_file, vcf_file_name, contact_name, total_contact, total_file):
  total_contact = int(total_contact)
  total_file = int(total_file)
  numbers = check_number(txt_file)
  split_number = split(numbers, total_contact)
  countc = 0
  countf = 0
  vcf_files = []
  sisa = []

  for numbers in split_number:
    vcard_entries = []
    for number in numbers:
      countc+=1
      vcard_entry = f"BEGIN:VCARD\nVERSION:3.0\nFN:{contact_name}-{countc}\nTEL;TYPE=CELL:+{number}\nEND:VCARD"
      vcard_entries.append(vcard_entry)

    countf+=1
    if countf > total_file:
      sisa.append(numbers)
    else:
      vcf_name = f"files/{vcf_file_name}_{countf}.vcf"
      vcf_files.append(vcf_name)
      
      with open(vcf_name, 'w', encoding='utf-8') as vcard_file:
        for entry in vcard_entries:
            vcard_file.write(entry + "\n")
  
  if sisa:
    file_txt = "files/sisa-kontak.txt"
    vcf_files.append(file_txt)
    
    with open(file_txt, 'w', encoding='utf-8') as file:
      for s in sisa:
        file.write("\n".join(s) + "\n")
  
  return vcf_files

def vcf_parse(vcf_file, new_vcf, total_contact, total_file):
  total_contact = int(total_contact)
  total_file = int(total_file)

  with open(vcf_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

  contacts = []
  current_contact = []

  for line in lines:
    if not line.strip():
      continue

    current_contact.append(line)
    if line.strip() == 'END:VCARD':
      contacts.append(current_contact)
      current_contact = []

  split_contact = split(contacts, total_contact)
  countf = 0
  files = []

  for contacts in split_contact:
    countf+=1
    file_name = f"files/{new_vcf}_{countf}.vcf"
    files.append(file_name)
    
    with open(file_name, 'w', encoding='utf-8') as file:
      for contact in contacts:
        contact = "".join(contact)
        file.write(contact)

    if countf == total_file:
      break

  return files

def vcf_to_other(vcf_file, file_name, file_type):
  with open(vcf_file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

  contacts = []

  for line in lines:
    if 'TEL;' in line.strip():
      contact = findall('\d+', line.strip())[0]
      contacts.append(contact)

  file_name = f"files/{file_name}.{file_type}"

  if file_type == 'xlsx':
    df = pd.DataFrame(contacts, columns=["Contact"])
    df.to_excel(file_name, index=False, header=False)

  with open(file_name, 'w', encoding='utf-8') as txt_file:
    for c in contacts:
      txt_file.write(c + "\n")
      
  return file_name

def xlsx_to_txt(xlsx_file, vcf_file_name):
  df = pd.read_excel(xlsx_file)
  file_name = f"files/{vcf_file_name}.txt"
  df.to_csv(file_name, index=False, sep='\t')

  return file_name

def xlsx_to_vcf(xlsx_file, vcf_file_name, contact_name, total_contact, total_file):
  txt_file_name = xlsx_to_txt(xlsx_file, vcf_file_name)
  files = txt_to_vcf(txt_file_name, vcf_file_name, contact_name, total_contact, total_file)
  
  return files
