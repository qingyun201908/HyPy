from flask import Flask, render_template, request, json
from flask_mysqldb import MySQL
import math
from datetime import datetime  # 添加datetime模块用于日期处理

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'test'
mysql = MySQL(app)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    diary_id = request.args.get('id', type=int)
    
    cur = mysql.connection.cursor()
    
    if diary_id:
        cur.execute("SELECT id, date, text, images FROM posts WHERE id = %s", (diary_id,))
    else:
        offset = (page - 1)
        cur.execute("SELECT id, date, text, images FROM posts ORDER BY id ASC LIMIT 1 OFFSET %s", (offset,))
    
    diary = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) FROM posts")
    total = cur.fetchone()[0]
    cur.close()
    
    processed_diary = None
    if diary:
        try:
            # 将日期字符串转换为datetime对象
            diary_date = datetime.fromisoformat(diary[1]) if isinstance(diary[1], str) else diary[1]
            
            images_data = json.loads(diary[3]) if diary[3] and diary[3] != 'null' else []
            images = []
            for img in images_data if isinstance(images_data, list) else []:
                if not img:  # 跳过空元素
                    continue
                image_info = {
                    "url": f"https://profile-api.hydev.org/exports/hykilp/{img['url']}" 
                           if img.get('url') and not img['url'].startswith('http') 
                           else img.get('url', ''),
                    "thumb": f"https://profile-api.hydev.org/exports/hykilp/{img['thumb']}" 
                             if img.get('thumb') and not img['thumb'].startswith('http') 
                             else img.get('thumb', ''),
                    "width": img.get('width'),
                    "height": img.get('height'),
                    "type": img.get('media_type', 'photo'),
                    "original_name": img.get('original_name', '未命名图片')
                }
                # 如果原始名称为空，提供默认值
                if not image_info['original_name']:
                    image_info['original_name'] = '未命名图片'
                images.append(image_info)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing images: {e}")
            images = []
        
        processed_diary = {
            'id': diary[0],
            'date': diary_date,  # 使用转换后的datetime对象
            'text': diary[2],
            'images': images
        }
    
    total_pages = total
    
    start_page = max(1, page - 3)
    end_page = min(total_pages, page + 3)
    
    return render_template('index.html', 
                           diary=processed_diary, 
                           page=page,
                           total_pages=total_pages,
                           start_page=start_page,
                           end_page=end_page)