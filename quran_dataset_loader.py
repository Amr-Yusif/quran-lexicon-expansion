"""
مكتبة لتحميل وتجهيز بيانات القرآن الكريم والتفسير
"""

import os
import json
import requests
from tqdm import tqdm
import pandas as pd


class QuranDatasetLoader:
    """فئة لتحميل وتجهيز بيانات القرآن الكريم والتفسير والعلوم الإسلامية"""

    def __init__(self, data_dir="quran_data"):
        """تهيئة محمل بيانات القرآن"""
        self.data_dir = data_dir
        # إنشاء المجلد إذا لم يكن موجودًا
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def download_quran_text(self):
        """تحميل نص القرآن الكريم من واجهة برمجة التطبيقات"""
        quran_file = os.path.join(self.data_dir, "quran_text.json")

        # التحقق مما إذا كان الملف موجودًا بالفعل
        if os.path.exists(quran_file):
            print("ملف القرآن الكريم موجود بالفعل.")
            with open(quran_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # واجهة برمجة تطبيقات القرآن
        url = "https://api.alquran.cloud/v1/quran/ar.asad"
        
        try:
            print("جاري تحميل نص القرآن الكريم...")
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "surahs" in data["data"]:
                    with open(quran_file, "w", encoding="utf-8") as f:
                        json.dump(data["data"]["surahs"], f, ensure_ascii=False, indent=2)
                    print(f"تم حفظ نص القرآن الكريم في {quran_file}")
                    return data["data"]["surahs"]
                else:
                    print("تنسيق البيانات غير متوقع.")
            else:
                print(f"فشل التحميل. كود الاستجابة: {response.status_code}")
        except Exception as e:
            print(f"حدث خطأ أثناء تحميل القرآن: {str(e)}")
        
        return None

    def download_tafseer(self, tafseer_name="ar.muyassar"):
        """تحميل تفسير محدد للقرآن الكريم"""
        tafseer_file = os.path.join(self.data_dir, f"tafseer_{tafseer_name.replace('.', '_')}.json")

        # التحقق مما إذا كان الملف موجودًا بالفعل
        if os.path.exists(tafseer_file):
            print(f"ملف التفسير {tafseer_name} موجود بالفعل.")
            with open(tafseer_file, "r", encoding="utf-8") as f:
                return json.load(f)

        tafseer_data = []
        
        # تنزيل التفسير لكل سورة وآية
        try:
            print(f"جاري تحميل تفسير {tafseer_name}...")
            # تحميل عدد السور
            suras_url = "https://api.alquran.cloud/v1/meta"
            response = requests.get(suras_url)
            if response.status_code != 200:
                print("فشل في الحصول على بيانات السور")
                return None
            
            suras_count = response.json()["data"]["suras"]["count"]
            
            for sura in tqdm(range(1, suras_count + 1)):
                sura_url = f"https://api.alquran.cloud/v1/surah/{sura}/{tafseer_name}"
                response = requests.get(sura_url)
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data and "ayahs" in data["data"]:
                        for ayah in data["data"]["ayahs"]:
                            tafseer_data.append({
                                "sura": sura,
                                "ayah": ayah["numberInSurah"],
                                "text": ayah["text"]
                            })
            
            with open(tafseer_file, "w", encoding="utf-8") as f:
                json.dump(tafseer_data, f, ensure_ascii=False, indent=2)
            print(f"تم حفظ التفسير في {tafseer_file}")
            
        except Exception as e:
            print(f"حدث خطأ أثناء تحميل التفسير: {str(e)}")
        
        return tafseer_data

    def load_scientific_miracles(self):
        """تحميل أو إنشاء مجموعة بيانات المعجزات العلمية في القرآن"""
        miracles_file = os.path.join(self.data_dir, "scientific_miracles.json")
        
        # بيانات أولية للمعجزات العلمية إذا لم يكن الملف موجودًا
        if not os.path.exists(miracles_file):
            # قائمة أولية من المعجزات العلمية
            miracles = [
                {
                    "title": "تمدد الكون",
                    "verse": "والسماء بنيناها بأيد وإنا لموسعون",
                    "surah": "الذاريات",
                    "ayah_number": 47,
                    "explanation": "تشير الآية إلى حقيقة توسع الكون، وهي حقيقة علمية لم تكتشف إلا في القرن العشرين مع نظرية الانفجار العظيم وقانون هابل للتمدد."
                },
                {
                    "title": "الأجنة وتطور الخلق",
                    "verse": "ولقد خلقنا الإنسان من سلالة من طين، ثم جعلناه نطفة في قرار مكين، ثم خلقنا النطفة علقة فخلقنا العلقة مضغة فخلقنا المضغة عظاما فكسونا العظام لحما ثم أنشأناه خلقا آخر فتبارك الله أحسن الخالقين",
                    "surah": "المؤمنون",
                    "ayah_number": "12-14",
                    "explanation": "تصف هذه الآيات مراحل تطور الجنين البشري بدقة علمية مذهلة، مطابقة للحقائق التي لم تكتشف إلا في العصر الحديث بالفحص المجهري."
                },
                {
                    "title": "طبقات الغلاف الجوي",
                    "verse": "وأنزلنا من السماء ماء بقدر فأسكناه في الأرض وإنا على ذهاب به لقادرون",
                    "surah": "المؤمنون",
                    "ayah_number": 18,
                    "explanation": "تشير إلى حقيقة أن الغلاف الجوي يحتفظ بالماء ويوزعه بنظام دقيق، وهي حقيقة علمية تتعلق بدورة الماء في الطبيعة."
                },
                {
                    "title": "مراحل تكوين الحليب",
                    "verse": "وإن لكم في الأنعام لعبرة نسقيكم مما في بطونه من بين فرث ودم لبنا خالصا سائغا للشاربين",
                    "surah": "النحل",
                    "ayah_number": 66,
                    "explanation": "تصف الآية بدقة كيفية تكوين الحليب من بين محتويات الجهاز الهضمي والدم، وهي عملية معقدة لم تفهم تفاصيلها العلمية إلا حديثًا."
                },
                {
                    "title": "الجبال أوتاد",
                    "verse": "والجبال أوتادا",
                    "surah": "النبأ",
                    "ayah_number": 7,
                    "explanation": "تصف الآية الجبال بأنها أوتاد، وهو ما يتفق مع الاكتشافات الجيولوجية الحديثة التي تبين أن للجبال جذورًا عميقة في طبقات الأرض تشبه الأوتاد."
                }
            ]
            
            with open(miracles_file, "w", encoding="utf-8") as f:
                json.dump(miracles, f, ensure_ascii=False, indent=2)
            print(f"تم إنشاء ملف المعجزات العلمية في {miracles_file}")
        else:
            print("ملف المعجزات العلمية موجود بالفعل.")
            with open(miracles_file, "r", encoding="utf-8") as f:
                miracles = json.load(f)
                
        return miracles

    def prepare_quran_dataset_for_embedding(self):
        """تجهيز بيانات القرآن الكريم للتضمين"""
        # تحميل القرآن
        quran_surahs = self.download_quran_text()
        
        if not quran_surahs:
            print("لم يتم تحميل القرآن بنجاح.")
            return []
        
        chunks = []
        # تقسيم القرآن إلى وحدات (آيات أو مجموعات صغيرة من الآيات)
        for surah in quran_surahs:
            surah_name = surah.get("name", "")
            surah_number = surah.get("number", 0)
            
            # تجميع الآيات في كل سورة
            for ayah in surah.get("ayahs", []):
                ayah_number = ayah.get("numberInSurah", 0)
                ayah_text = ayah.get("text", "")
                
                # إضافة معلومات الآية
                chunk = {
                    "content": ayah_text,
                    "metadata": {
                        "source": "Quran",
                        "surah_name": surah_name,
                        "surah_number": surah_number,
                        "ayah_number": ayah_number,
                        "type": "ayah"
                    }
                }
                chunks.append(chunk)
                
        return chunks

    def prepare_tafseer_dataset_for_embedding(self, tafseer_name="ar.muyassar"):
        """تجهيز بيانات التفسير للتضمين"""
        # تحميل التفسير
        tafseer_data = self.download_tafseer(tafseer_name)
        
        if not tafseer_data:
            print("لم يتم تحميل التفسير بنجاح.")
            return []
        
        chunks = []
        # تجهيز بيانات التفسير للتضمين
        for item in tafseer_data:
            surah_number = item.get("sura", 0)
            ayah_number = item.get("ayah", 0)
            tafseer_text = item.get("text", "")
            
            # إضافة معلومات التفسير
            chunk = {
                "content": tafseer_text,
                "metadata": {
                    "source": f"Tafseer_{tafseer_name}",
                    "surah_number": surah_number,
                    "ayah_number": ayah_number,
                    "type": "tafseer"
                }
            }
            chunks.append(chunk)
                
        return chunks

    def prepare_miracles_dataset_for_embedding(self):
        """تجهيز بيانات المعجزات العلمية للتضمين"""
        # تحميل المعجزات العلمية
        miracles = self.load_scientific_miracles()
        
        chunks = []
        # تجهيز بيانات المعجزات العلمية للتضمين
        for miracle in miracles:
            title = miracle.get("title", "")
            verse = miracle.get("verse", "")
            surah = miracle.get("surah", "")
            ayah_number = miracle.get("ayah_number", "")
            explanation = miracle.get("explanation", "")
            
            # إنشاء نص كامل للمعجزة
            full_text = f"المعجزة: {title}\nالآية: {verse}\nالسورة: {surah} الآية: {ayah_number}\nالشرح: {explanation}"
            
            # إضافة معلومات المعجزة
            chunk = {
                "content": full_text,
                "metadata": {
                    "source": "Scientific_Miracle",
                    "title": title,
                    "surah": surah,
                    "ayah_number": ayah_number,
                    "type": "miracle"
                }
            }
            chunks.append(chunk)
                
        return chunks

    def get_all_datasets_for_embedding(self):
        """الحصول على جميع مجموعات البيانات للتضمين"""
        quran_chunks = self.prepare_quran_dataset_for_embedding()
        tafseer_chunks = self.prepare_tafseer_dataset_for_embedding()
        miracles_chunks = self.prepare_miracles_dataset_for_embedding()
        
        # دمج جميع الوحدات
        all_chunks = quran_chunks + tafseer_chunks + miracles_chunks
        
        return all_chunks