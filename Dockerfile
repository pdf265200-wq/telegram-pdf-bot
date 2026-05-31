FROM python:3.12-slim

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ara \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1 \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ requirements أولاً للاستفادة من ذاكرة التخزين المؤقت
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# إنشاء مجلدات ضرورية
RUN mkdir -p temp database logs

# تشغيل البوت
CMD ["python", "bot.py"]
