import os
from pymongo import MongoClient
from quart import Quart, jsonify, render_template, request, redirect, url_for, session, flash
from quart_session import Session

from config import *
from bot import *
from helpers import *

app = Quart(__name__)
app.secret_key = 'supersecretkey'
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB_URI'] = mongo_uri
app.config['SESSION_MONGODB_COLLECTION'] = 'sessions'

mclient = MongoClient(mongo_uri)
db = mclient.converter

Session(app)

@app.context_processor
def inject_user():
    return dict(bot_username=bot_username)

@app.route('/admin')
async def admin():
  if not is_admin(session):
    return redirect('/')
  
  users = list(db.users.find())
  
  return await render_template('admin.html', users=users)

@app.route('/')
async def index():
  if not is_login(session):
    return redirect(url_for('login'))
  
  return await render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
async def login():  
  form = await request.form

  if request.method == 'POST':
    username = form['username']
    password = form['password']
    user = db.users.find_one({'username': username})

    if user and user['password'] == password:
      if user.get('role') != 'admin' and not is_user_valid(user.get('expired')):
        await flash(f"Akun expired. Hubungi admin {owner}")

        return await render_template('login.html')

      session['username'] = username
      session['role'] = user.get('role')
      session['expired'] = user.get('expired')

      return redirect(url_for('index'))
    else:
      await flash('Invalid username or password')

  return await render_template('login.html')

@app.route('/logout')
async def logout():
  session.pop('username', None)
  session.pop('role', None)
  session.pop('expired', None)
  await flash('You have been logged out.')

  return redirect(url_for('login'))

@app.route('/generate', methods=['POST'])
async def generate():
  if not is_login:
    return redirect(url_for('login'))
  
  user = db.users.find_one({'username': session['username']})
  if user.get('role') != 'admin' and not is_user_valid(user.get('expired')):
    await flash(f"Akun expired. Hubungi admin {owner}")
    return redirect(url_for('logout'))

  try:
    form = await request.form
    admins = form['admins']
    navys = form['navys']
    clients = form['clients']
    admin_name = form['admin_name']
    navy_name = form['navy_name']
    client_name = form['client_name']
    nama_file = form['nama_file']
    id_tele = form['id_tele']
    hasil = form['hasil']
    totalc = form['totalc']
    name_number = form['name_number']

    files = contact_to_vcf(admins, navys, clients, admin_name, navy_name, client_name, nama_file, hasil, int(totalc), name_number)

    await send_files(id_tele, files)

    remove_files(files)

    await flash(f'Kontak berhasil terkirim melalui telegram {id_tele}')
    return redirect(url_for('index'))
  except Exception as e:
    print(e)
    return jsonify({'success': False, 'error': str(e)})

@app.route('/converter')
async def converter():
  if not is_login:
    return redirect(url_for('login'))
  
  return await render_template('converter.html')

@app.route('/convert_txt_to_vcf', methods=['POST'])
async def convert_txt_to_vcf():
  form = await request.form
  txt_file = (await request.files)['txt_file']
  vcf_file_name = form['vcf_file_name']
  contact_name = form['contact_name']
  total_contact = form['total_contact']
  total_file = form['total_file']
  id_tele = form['id_tele']

  txt_file_path = os.path.join('uploads', txt_file.filename)
  await txt_file.save(txt_file_path)

  files = txt_to_vcf(txt_file_path, vcf_file_name, contact_name, total_contact, total_file)

  await send_files(id_tele, files)
  await flash(f'Kontak berhasil terkirim melalui telegram {id_tele}')
  files.append(txt_file_path)
  remove_files(files)

  return redirect(url_for('converter'))

@app.route('/convert_xlsx_to_vcf', methods=['POST'])
async def convert_xlsx_to_vcf():
  form = await request.form
  xlsx_file = (await request.files)['xlsx_file']
  vcf_file_name = form['vcf_file_name']
  contact_name = form['contact_name']
  total_contact = form['total_contact']
  total_file = form['total_file']
  id_tele = form['id_tele']

  xlsx_file_path = os.path.join('uploads', xlsx_file.filename)
  await xlsx_file.save(xlsx_file_path)

  files = xlsx_to_vcf(xlsx_file_path, vcf_file_name, contact_name, total_contact, total_file)

  await send_files(id_tele, files)
  await flash(f'Kontak berhasil terkirim melalui telegram {id_tele}')
  files.append(xlsx_file_path)
  remove_files(files)

  return redirect(url_for('converter'))

@app.route('/convert_csv_to_vcf', methods=['POST'])
async def convert_csv_to_vcf():
  form = await request.form
  csv_file = (await request.files)['csv_file']
  vcf_file_name = form['vcf_file_name']
  contact_name = form['contact_name']
  total_contact = form['total_contact']
  total_file = form['total_file']
  id_tele = form['id_tele']

  csv_file_path = os.path.join('uploads', csv_file.filename)
  await csv_file.save(csv_file_path)

  files = txt_to_vcf(csv_file_path, vcf_file_name, contact_name, total_contact, total_file)

  await send_files(id_tele, files)
  await flash(f'Kontak berhasil terkirim melalui telegram {id_tele}')
  files.append(csv_file_path)
  remove_files(files)

  return redirect(url_for('converter'))

@app.route('/convert_vcf_to_other', methods=['POST'])
async def convert_vcf_to_other():
  form = await request.form
  vcf_file = (await request.files)['vcf_file']
  file_name = form['file_name']
  convert = form['convert']
  id_tele = form['id_tele']

  vcf_file_path = os.path.join('uploads', vcf_file.filename)
  await vcf_file.save(vcf_file_path)

  files = vcf_to_other(vcf_file_path, file_name, convert)

  await send_files(id_tele, files)
  await flash(f'Kontak berhasil terkirim melalui telegram {id_tele}')
  files.append(vcf_file_path)
  remove_files(files)

  return redirect(url_for('converter'))

@app.route('/tambahuser', methods=['POST'])
async def tambahuser():
  if not is_admin(session):
    return redirect('/')
  
  form = await request.form
  username = form['username']
  password = form['password']
  expired = form['expired']

  if db.users.find_one({'username': username}):
    await flash('Username already exists!')
  else:
    db.users.insert_one({'username': username, 'password': password, 'expired': expired, 'role': 'user'})
    await  flash('Registration successful!')

  return redirect(url_for('admin'))

@app.route('/edituser', methods=['POST'])
async def edituser():
  if not is_admin(session):
    return redirect('/')
  
  form = await request.form
  username = form['username']
  password = form['password']
  expired = form['expired']

  user = db.users.find_one({'username': username})
  if user:
    db.users.update_one(
      {'username': username},
      {'$set': {'password': password, 'expired': expired}}
    )
    await flash('User updated successfully!')
  else:
    await flash('User not found!')

  return redirect(url_for('admin'))

@app.route('/deleteuser', methods=['POST'])
async def deleteuser():
  if not is_admin(session):
    return redirect('/')
  
  form = await request.form
  username = form['username']
  user = db.users.find_one({'username': username})

  if user:
    db.users.delete_one({'username': username})
    await flash('User deleted successfully!')
  else:
    await flash('User not found!')

  return redirect(url_for('admin'))

@app.route('/tes')
async def tes():
  if not bot.is_connected():
    await bot.connect()
    
  print(await bot.get_me())

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, loop=bot.loop, debug=True)
