import json
import requests

# 1. Đọc dữ liệu từ file JSON
with open('aimatch_demo_data.json', 'r', encoding='utf-8') as file:
    jobs = json.load(file)

# 2. Khai báo đường dẫn API của Recruitment Service
# Thay đổi /api/jobs thành route chính xác trong source code của bạn
API_URL = "http://localhost:8000/api/jobs" 

# 3. Lặp qua từng job và gửi POST request để lưu vào hệ thống
success_count = 0
for job in jobs:
    try:
        response = requests.post(API_URL, json=job)
        
        if response.status_code in [200, 201]:
            print(f"✅ Đã thêm thành công: {job['title']}")
            success_count += 1
        else:
            print(f"❌ Lỗi khi thêm {job['title']}: {response.text}")
            
    except Exception as e:
        print(f"⚠️ Không thể kết nối tới API: {e}")

print(f"\n🎉 Hoàn tất! Đã bơm {success_count}/{len(jobs)} công việc vào Database.")