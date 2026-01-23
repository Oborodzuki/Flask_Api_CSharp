from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
DATA_FILE = 'data.json'
PASSWORD_FILE = 'password.txt'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

if not os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, 'w') as f:
        f.write("admin")

def verify_password(password):
    with open(PASSWORD_FILE, 'r') as f:
        return f.read().strip() == password

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Manager</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
            .login-section { background: #e8f4fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .data-section { display: none; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            button { padding: 8px 15px; margin: 5px; cursor: pointer; }
            .language-btn { position: absolute; top: 20px; right: 20px; }
        </style>
    </head>
    <body>
        <button class="language-btn" onclick="toggleLanguage()">中文/EN</button>
        <div class="container">
            <div class="header">
                <h1 id="title">数据管理系统</h1>
            </div>
            
            <div class="login-section" id="loginSection">
                <h3 id="loginTitle">管理员登录</h3>
                <input type="password" id="passwordInput" placeholder="密码">
                <button onclick="login()" id="loginBtn">登录</button>
            </div>

            <div class="data-section" id="dataSection">
                <div class="controls">
                    <button onclick="showAddForm()" id="addBtn">添加数据</button>
                    <button onclick="loadAllData()" id="refreshBtn">刷新数据</button>
                    <button onclick="showPasswordForm()" id="pwdBtn">修改密码</button>
                    <button onclick="logout()" id="logoutBtn">退出</button>
                </div>
                
                <div id="passwordForm" style="display:none; margin:20px 0;">
                    <h4 id="changePwdTitle">修改密码</h4>
                    <input type="password" id="oldPassword" placeholder="旧密码">
                    <input type="password" id="newPassword" placeholder="新密码">
                    <button onclick="changePassword()" id="changePwdBtn">确认修改</button>
                </div>

                <div id="addForm" style="display:none; margin:20px 0;">
                    <h4 id="addDataTitle">添加/编辑数据</h4>
                    <input type="text" id="keyInput" placeholder="键">
                    <textarea id="valueInput" placeholder="值 (JSON格式)" style="width:300px;height:100px"></textarea>
                    <button onclick="saveData()" id="saveBtn">保存</button>
                </div>

                <table id="dataTable">
                    <thead>
                        <tr>
                            <th id="keyHeader">键</th>
                            <th id="valueHeader">值</th>
                            <th id="actionHeader">操作</th>
                        </tr>
                    </thead>
                    <tbody id="dataBody"></tbody>
                </table>
            </div>
        </div>

        <script>
            let currentLanguage = 'zh';
            const translations = {
                'zh': {
                    'title': '数据管理系统',
                    'loginTitle': '管理员登录',
                    'loginBtn': '登录',
                    'addBtn': '添加数据',
                    'refreshBtn': '刷新数据',
                    'pwdBtn': '修改密码',
                    'logoutBtn': '退出',
                    'changePwdTitle': '修改密码',
                    'changePwdBtn': '确认修改',
                    'addDataTitle': '添加/编辑数据',
                    'saveBtn': '保存',
                    'keyHeader': '键',
                    'valueHeader': '值',
                    'actionHeader': '操作',
                    'edit': '编辑',
                    'delete': '删除',
                    'passwordPlaceholder': '密码',
                    'oldPasswordPlaceholder': '旧密码',
                    'newPasswordPlaceholder': '新密码',
                    'keyPlaceholder': '键',
                    'valuePlaceholder': '值 (JSON格式)'
                },
                'en': {
                    'title': 'Data Management System',
                    'loginTitle': 'Admin Login',
                    'loginBtn': 'Login',
                    'addBtn': 'Add Data',
                    'refreshBtn': 'Refresh Data',
                    'pwdBtn': 'Change Password',
                    'logoutBtn': 'Logout',
                    'changePwdTitle': 'Change Password',
                    'changePwdBtn': 'Confirm Change',
                    'addDataTitle': 'Add/Edit Data',
                    'saveBtn': 'Save',
                    'keyHeader': 'Key',
                    'valueHeader': 'Value',
                    'actionHeader': 'Actions',
                    'edit': 'Edit',
                    'delete': 'Delete',
                    'passwordPlaceholder': 'Password',
                    'oldPasswordPlaceholder': 'Old Password',
                    'newPasswordPlaceholder': 'New Password',
                    'keyPlaceholder': 'Key',
                    'valuePlaceholder': 'Value (JSON format)'
                }
            };

            function toggleLanguage() {
                currentLanguage = currentLanguage === 'zh' ? 'en' : 'zh';
                applyTranslations();
            }

            function applyTranslations() {
                const t = translations[currentLanguage];
                document.getElementById('title').textContent = t.title;
                document.getElementById('loginTitle').textContent = t.loginTitle;
                document.getElementById('loginBtn').textContent = t.loginBtn;
                document.getElementById('addBtn').textContent = t.addBtn;
                document.getElementById('refreshBtn').textContent = t.refreshBtn;
                document.getElementById('pwdBtn').textContent = t.pwdBtn;
                document.getElementById('logoutBtn').textContent = t.logoutBtn;
                document.getElementById('changePwdTitle').textContent = t.changePwdTitle;
                document.getElementById('changePwdBtn').textContent = t.changePwdBtn;
                document.getElementById('addDataTitle').textContent = t.addDataTitle;
                document.getElementById('saveBtn').textContent = t.saveBtn;
                document.getElementById('keyHeader').textContent = t.keyHeader;
                document.getElementById('valueHeader').textContent = t.valueHeader;
                document.getElementById('actionHeader').textContent = t.actionHeader;
                document.getElementById('passwordInput').placeholder = t.passwordPlaceholder;
                document.getElementById('oldPassword').placeholder = t.oldPasswordPlaceholder;
                document.getElementById('newPassword').placeholder = t.newPasswordPlaceholder;
                document.getElementById('keyInput').placeholder = t.keyPlaceholder;
                document.getElementById('valueInput').placeholder = t.valuePlaceholder;
            }

            let isLoggedIn = false;
            let allData = {};

            async function login() {
                const password = document.getElementById('passwordInput').value;
                const response = await fetch('/api/admin/verify', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({password})
                });
                
                if (response.ok) {
                    isLoggedIn = true;
                    document.getElementById('loginSection').style.display = 'none';
                    document.getElementById('dataSection').style.display = 'block';
                    loadAllData();
                } else {
                    alert('Login failed');
                }
            }

            function logout() {
                isLoggedIn = false;
                document.getElementById('loginSection').style.display = 'block';
                document.getElementById('dataSection').style.display = 'none';
            }

            async function loadAllData() {
                const response = await fetch('/api/data/all');
                const result = await response.json();
                if (result.success) {
                    allData = result.data;
                    displayData(allData);
                }
            }

            function displayData(data) {
                const tbody = document.getElementById('dataBody');
                tbody.innerHTML = '';
                
                for (const [key, value] of Object.entries(data)) {
                    const row = tbody.insertRow();
                    row.insertCell(0).textContent = key;
                    row.insertCell(1).textContent = JSON.stringify(value, null, 2);
                    
                    const actionCell = row.insertCell(2);
                    actionCell.innerHTML = `
                        <button onclick="editData('${key}')">${translations[currentLanguage].edit}</button>
                        <button onclick="deleteData('${key}')">${translations[currentLanguage].delete}</button>
                    `;
                }
            }

            function showAddForm() {
                document.getElementById('addForm').style.display = 'block';
                document.getElementById('keyInput').value = '';
                document.getElementById('valueInput').value = '';
            }

            async function saveData() {
                const key = document.getElementById('keyInput').value;
                try {
                    const value = JSON.parse(document.getElementById('valueInput').value);
                    const response = await fetch(`/api/data/${key}`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(value)
                    });
                    
                    if (response.ok) {
                        loadAllData();
                        document.getElementById('addForm').style.display = 'none';
                    }
                } catch (e) {
                    alert('JSON格式错误: ' + e.message);
                }
            }

            async function deleteData(key) {
                if (confirm('确认删除?')) {
                    const response = await fetch(`/api/data/${key}`, {method: 'DELETE'});
                    if (response.ok) {
                        loadAllData();
                    }
                }
            }

            function editData(key) {
                document.getElementById('addForm').style.display = 'block';
                document.getElementById('keyInput').value = key;
                document.getElementById('valueInput').value = JSON.stringify(allData[key], null, 2);
            }

            function showPasswordForm() {
                document.getElementById('passwordForm').style.display = 'block';
            }

            async function changePassword() {
                const oldPassword = document.getElementById('oldPassword').value;
                const newPassword = document.getElementById('newPassword').value;
                
                const response = await fetch('/api/admin/password', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({oldPassword, newPassword})
                });
                
                if (response.ok) {
                    alert('Password changed');
                    document.getElementById('passwordForm').style.display = 'none';
                }
            }

            applyTranslations();
        </script>
    </body>
    </html>
    '''

@app.route('/api/data/all', methods=['GET'])
def get_all_data():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/data/<key>', methods=['GET'])
def get_data(key):
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return jsonify({'success': True, 'data': data.get(key)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/data/<key>', methods=['POST'])
def set_data(key):
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        new_data = request.json
        new_data['lastModified'] = datetime.now().isoformat()
        data[key] = new_data
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/data/<key>', methods=['DELETE'])
def delete_data(key):
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        if key in data:
            del data[key]
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Key not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/verify', methods=['POST'])
def verify_admin():
    password = request.json.get('password')
    if verify_password(password):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid password'}), 401

@app.route('/api/admin/password', methods=['POST'])
def change_password():
    try:
        if not verify_password(request.json.get('oldPassword')):
            return jsonify({'success': False, 'error': 'Invalid old password'}), 401
        
        with open(PASSWORD_FILE, 'w') as f:
            f.write(request.json.get('newPassword'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("启动数据管理服务器...")
    print("前端地址: http://localhost:5001")
    print("API地址: http://localhost:5001/api")
    print("默认密码: admin")
    app.run(host='0.0.0.0', port=5001)