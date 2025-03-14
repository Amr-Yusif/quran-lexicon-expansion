#!/bin/bash

# سكريبت إعداد بيئة العمل لمشروع مساعد القرآن الذكي المحلي

echo "بدء إعداد بيئة العمل لمشروع مساعد القرآن الذكي..."

# التأكد من وجود دوكر وdocker-compose
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null
then
    echo "يرجى تثبيت Docker و Docker Compose أولاً"
    echo "يمكنك اتباع التعليمات على: https://docs.docker.com/get-docker/"
    exit 1
fi

# إنشاء مجلدات البيانات
mkdir -p ./data/mongodb
mkdir -p ./data/redis
mkdir -p ./data/qdrant
mkdir -p ./quran_data

echo "تم إنشاء مجلدات البيانات"

# تحميل وبناء الصور
echo "جاري بناء وتشغيل الخدمات باستخدام Docker Compose..."
docker-compose up -d

# انتظار بدء تشغيل الخدمات
echo "انتظار بدء تشغيل الخدمات..."
sleep 10

# تأكد من تحميل نموذج Mistral في Ollama
echo "جاري تحميل نموذج Mistral في Ollama..."
if docker exec quran-assistant-ollama ollama list | grep -q "mistral"; then
    echo "نموذج Mistral موجود بالفعل"
else
    docker exec quran-assistant-ollama ollama pull mistral
fi

# تهيئة مجموعات Qdrant
echo "جاري تهيئة مجموعات Qdrant..."
for collection in "tafsir_explanations" "scholars_books" "scientific_miracles"
do
    # التحقق مما إذا كانت المجموعة موجودة بالفعل
    status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:6333/collections/$collection)
    
    if [ "$status_code" -eq 200 ]; then
        echo "مجموعة $collection موجودة بالفعل"
    else
        # إنشاء المجموعة
        curl -X PUT http://localhost:6333/collections/$collection \
            -H 'Content-Type: application/json' \
            -d '{
                "vectors": {
                    "size": 768,
                    "distance": "Cosine"
                }
            }'
        echo "تم إنشاء مجموعة $collection"
    fi
done

echo "تم إعداد بيئة العمل بنجاح!"
echo "لتشغيل التطبيق:"