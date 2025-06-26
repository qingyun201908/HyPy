from flask import Flask, render_template, request, json
from flask_mysqldb import MySQL
import math

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'test'
mysql = MySQL(app)

# 分页查询日记，每次只查询一条
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    diary_id = request.args.get('id', type=int)  # 获取特定ID
    
    cur = mysql.connection.cursor()
    
    # 查询特定日记（如果有ID参数）
    if diary_id:
        cur.execute("SELECT id, date, text, images FROM posts WHERE id = %s", (diary_id,))
    else:
        # 计算偏移量
        offset = (page - 1)
        # 查询当前页的日记（每次只查询一条）
        cur.execute("SELECT id, date, text, images FROM posts ORDER BY id ASC LIMIT 1 OFFSET %s", (offset,))
    
    diary = cur.fetchone()
    
    # 查询总数量
    cur.execute("SELECT COUNT(*) FROM posts")
    total = cur.fetchone()[0]
    cur.close()
    
    # 处理JSON格式的图片数组
    processed_diary = {}
    if diary:
        try:
            # 解析JSON数据并提取图片URL
            images_data = json.loads(diary[3]) if diary[3] and diary[3] != 'null' else []
            # 添加基础URL前缀并提取其他信息
            images = [{
                "url": f"https://profile-api.hydev.org/exports/hykilp/{img['url']}" if img['url'] and not img['url'].startswith('http') else img['url'],
                "thumb": f"https://profile-api.hydev.org/exports/hykilp/{img['thumb']}" if img.get('thumb') and not img['thumb'].startswith('http') else img.get('thumb', ''),
                "width": img.get('width'),
                "height": img.get('height'),
                "type": img.get('media_type', 'photo'),
                "original_name": img.get('original_name', '')
            } for img in images_data] if isinstance(images_data, list) else []
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing images: {e}")
            images = []
        
        processed_diary = {
            'id': diary[0],
            'date': diary[1],
            'text': diary[2],
            'images': images
        }
    
    total_pages = total  # 由于每页只显示一条，总页数等于总条数
    
    # 创建页码范围（最多显示7个页码）
    start_page = max(1, page - 3)
    end_page = min(total_pages, page + 3)
    
    return render_template('index.html', 
                           diary=processed_diary, 
                           page=page,
                           total_pages=total_pages,
                           start_page=start_page,
                           end_page=end_page)