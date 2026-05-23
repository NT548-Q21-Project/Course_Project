import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json

def scrape_job_details(job_url):
    """Hàm này vào từng trang JD cụ thể để cào chi tiết"""
    # Fake User-Agent để web không chặn bot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(job_url, headers=headers)
        response.raise_for_status() # Báo lỗi nếu trang web từ chối
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Lấy Tiêu đề (Title)
        title_element = soup.find('h1', class_='job-details__title')
        title = title_element.text.strip() if title_element else "Unknown Title"
        
        # 2. Lấy Địa điểm (Location)
        location_element = soup.find('div', class_='job-details__location')
        location = location_element.text.strip() if location_element else "Vietnam"

        # 3. Phân tách phần Mô tả (Description), Yêu cầu (Requirements), Quyền lợi (Benefits)
        # Tùy thuộc vào HTML của ITviec, thường họ chia thành các div rõ ràng
        job_description = ""
        requirements = ""
        benefits = ""
        
        # Tìm tất cả các thẻ h3 chứa tiêu đề mục (Mô tả, Yêu cầu...)
        detail_sections = soup.find_all('div', class_='job-details__paragraph')
        
        for section in detail_sections:
            heading = section.find('h3')
            if heading:
                heading_text = heading.text.lower()
                content = section.text.replace(heading.text, '').strip() # Xóa tiêu đề ra khỏi nội dung
                
                if 'mô tả' in heading_text or 'description' in heading_text:
                    job_description = content
                elif 'yêu cầu' in heading_text or 'requirement' in heading_text or 'skills' in heading_text:
                    requirements = content
                elif 'quyền lợi' in heading_text or 'benefit' in heading_text:
                    benefits = content
                    
        # Nếu web không chia rõ, ta gộp tất cả vào cột description
        if not job_description and not requirements:
             description_block = soup.find('div', class_='job-details__content')
             job_description = description_block.text.strip() if description_block else ""

        # Map vào đúng cấu trúc Database aimatch_db của bạn
        job_data = {
            "title": title,
            "description": job_description,
            "responsibilities": "", # Cào web thường khó tách riêng cái này, tạm để trống
            "requirements": requirements,
            "nice_to_have": "", 
            "benefits": benefits,
            "location": location,
            "job_type": "full_time" # Mặc định
        }
        return job_data

    except Exception as e:
        print(f"Lỗi khi cào link {job_url}: {e}")
        return None

def main():
    # Danh sách các link JD bạn muốn cào (bạn có thể copy link từ trình duyệt vào đây)
    target_urls = [
        "https://itviec.com/it-jobs/software-engineer-backend-python", # Thay bằng link thật
        "https://itviec.com/it-jobs/data-engineer" # Thay bằng link thật
    ]
    
    scraped_jobs = []
    
    for url in target_urls:
        print(f"Đang cào dữ liệu từ: {url}")
        job_data = scrape_job_details(url)
        if job_data:
            scraped_jobs.append(job_data)
        
        # Nghỉ 2 giây trước khi cào link tiếp theo để tránh bị khóa IP
        time.sleep(2)
        
    # Lưu kết quả ra file JSON để import vào Database sau
    with open('aimatch_demo_data.json', 'w', encoding='utf-8') as f:
        json.dump(scraped_jobs, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Đã cào xong {len(scraped_jobs)} jobs và lưu vào file aimatch_demo_data.json!")
    
    # Optional: Lưu thêm một bản CSV cho dễ đọc bằng Excel
    df = pd.DataFrame(scraped_jobs)
    df.to_csv('aimatch_demo_data.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    main()