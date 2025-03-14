import os
from mem0 import MemoryClient
import json

# تعيين API key لـ Mem0
API_KEY = "m0-ERkshrfpnqiFEo1i14gAUKJLj4vlxVQ10mgdSQLj"  # استبدل هذا بالمفتاح الخاص بك

# إنشاء عميل Mem0
client = MemoryClient(api_key=API_KEY)

# أمثلة لمعلومات من القرآن الكريم
quran_examples = [
    {
        "user_id": "quran_surahs",
        "messages": [
            {"role": "user", "content": "ما هي سورة الإخلاص؟"},
            {
                "role": "assistant",
                "content": "سورة الإخلاص هي السورة 112 من القرآن الكريم، وتتكون من 4 آيات، وهي: قُلْ هُوَ اللَّهُ أَحَدٌ، اللَّهُ الصَّمَدُ، لَمْ يَلِدْ وَلَمْ يُولَدْ، وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ",
            },
        ],
    },
    {
        "user_id": "quran_surahs",
        "messages": [
            {"role": "user", "content": "ما هي سورة الفاتحة؟"},
            {
                "role": "assistant",
                "content": "سورة الفاتحة هي السورة الأولى في القرآن الكريم، وتتكون من 7 آيات، وهي أم الكتاب وأم القرآن والسبع المثاني، وهي ركن أساسي في الصلاة، وتبدأ بـ 'بسم الله الرحمن الرحيم' وتنتهي بـ 'صراط الذين أنعمت عليهم غير المغضوب عليهم ولا الضالين'",
            },
        ],
    },
    {
        "user_id": "quran_themes",
        "messages": [
            {"role": "user", "content": "ما هي آيات الصبر في القرآن؟"},
            {
                "role": "assistant",
                "content": "من آيات الصبر في القرآن: 'واستعينوا بالصبر والصلاة' (البقرة: 45)، 'إنما يوفى الصابرون أجرهم بغير حساب' (الزمر: 10)، 'وبشر الصابرين الذين إذا أصابتهم مصيبة قالوا إنا لله وإنا إليه راجعون' (البقرة: 155-156)",
            },
        ],
    },
    {
        "user_id": "quran_themes",
        "messages": [
            {"role": "user", "content": "ما هي آيات الرحمة في القرآن؟"},
            {
                "role": "assistant",
                "content": "من آيات الرحمة في القرآن: 'ورحمتي وسعت كل شيء' (الأعراف: 156)، 'كتب ربكم على نفسه الرحمة' (الأنعام: 54)، 'وما أرسلناك إلا رحمة للعالمين' (الأنبياء: 107)",
            },
        ],
    },
]


# إضافة الذكريات
def add_quran_memories():
    print("جاري إضافة معلومات القرآن الكريم إلى Mem0...")

    for example in quran_examples:
        user_id = example["user_id"]
        messages = example["messages"]

        try:
            # إضافة الذاكرة
            client.add(messages, user_id=user_id)
            print(f"تم إضافة المعلومات بنجاح للمستخدم: {user_id}")
            print(f"- السؤال: {messages[0]['content']}")
            print(f"- الإجابة: {messages[1]['content'][:50]}...\n")
        except Exception as e:
            print(f"خطأ في إضافة الذاكرة: {str(e)}")


# البحث في الذاكرات
def search_quran_memories(query, user_id="quran_themes"):
    print(f"جاري البحث عن: '{query}' للمستخدم: {user_id}...")

    try:
        results = client.search(query, user_id=user_id)

        if results:
            print(f"تم العثور على {len(results)} نتائج:")
            for i, result in enumerate(results, 1):
                print(f"\nنتيجة {i}:")
                if "memory" in result:
                    print(f"المحتوى: {result['memory']}")
                if "score" in result:
                    print(f"درجة التطابق: {result['score']:.4f}")
                if "created_at" in result:
                    print(f"تاريخ الإنشاء: {result['created_at']}")
        else:
            print("لم يتم العثور على نتائج.")
    except Exception as e:
        print(f"خطأ في البحث: {str(e)}")


# تشغيل البرنامج
if __name__ == "__main__":
    print("=== برنامج تخزين واسترجاع معلومات القرآن الكريم ===\n")

    # إضافة الذكريات
    add_quran_memories()

    # البحث في الذكريات
    search_queries = [
        ("ما هي سورة الإخلاص", "quran_surahs"),
        ("آيات عن الصبر", "quran_themes"),
        ("أم الكتاب", "quran_surahs"),
    ]

    print("\n=== نتائج البحث ===\n")
    for query, user_id in search_queries:
        search_quran_memories(query, user_id)
        print("\n" + "-" * 50 + "\n")
