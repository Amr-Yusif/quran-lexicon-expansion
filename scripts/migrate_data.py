{{ ... }}
# وظيفة تحميل كتب الإعجاز العددي والحروفي
def download_numerical_miracles():
    """تحميل كتب الإعجاز العددي والحروفي في القرآن"""
    logger.info("جاري تحميل كتب الإعجاز العددي والحروفي في القرآن...")
    
    # إنشاء المجلد الرئيسي
    numerical_miracles_dir = NUMERICAL_MIRACLES_DIR
    numerical_miracles_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ تأكيد وجود المجلد: {numerical_miracles_dir}")
    
    # قائمة ببعض كتب الإعجاز العددي المهمة
    numerical_books = [
        {
            "title": "المعجزة العددية في القرآن الكريم",
            "author": "عبد الرزاق نوفل",
            "url": "https://archive.org/download/numerical_miracle_quran/numerical_miracle_quran.pdf",
        },
        {
            "title": "إعجاز الرقم 19 في القرآن الكريم",
            "author": "بسام جرار",
            "url": "https://archive.org/download/ijaz_raqm_19/ijaz_raqm_19.pdf",
        },
        {
            "title": "الإعجاز العددي في القرآن",
            "author": "عبد الدائم الكحيل",
            "url": "https://archive.org/download/kaheel_numerical_miracle/kaheel_numerical_miracle.pdf",
        },
        {
            "title": "الإعجاز العددي للقرآن الكريم",
            "author": "عادل عبد الصادق",
            "url": "https://archive.org/download/ijaz_adadi_quran/ijaz_adadi_quran.pdf",
        }
    ]
    
    # تحميل الكتب
    for book in numerical_books:
        file_name = f"{book['author']} - {book['title']}.pdf"
        destination = numerical_miracles_dir / file_name
        
        if destination.exists():
            logger.info(f"الملف موجود بالفعل: {destination}")
            continue
            
        download_file(book["url"], destination, description=file_name)

# وظيفة تحميل برنامج العلم والإيمان
def download_science_and_faith():
    """تحميل حلقات برنامج العلم والإيمان للدكتور مصطفى محمود"""
    logger.info("جاري تحميل حلقات برنامج العلم والإيمان...")
    
    # إنشاء مجلد مخصص
    mustafa_mahmoud_dir = SCHOLARS_DIRS["mustafa_mahmoud"]
    science_faith_dir = mustafa_mahmoud_dir / "science_and_faith"
    science_faith_dir.mkdir(parents=True, exist_ok=True)
    
    # تحميل حلقات برنامج العلم والإيمان
    for source_url in SOURCES["science_and_faith"]:
        # تحميل ملفات الفيديو والصوت
        media_links = extract_archive_org_links(source_url, file_extensions=['.mp3', '.mp4'])
        
        for idx, link in enumerate(media_links[:5]):  # تحميل الخمسة الأولى فقط للاختبار
            file_name = unquote(os.path.basename(link))
            destination = science_faith_dir / file_name
            
            download_file(link, destination, description=f"العلم والإيمان - {file_name}")
            
            # إضافة فترة انتظار قصيرة بين التحميلات لتجنب الضغط على الخادم
            time.sleep(1)

# وظيفة تحميل كتب العقيدة
def download_aqeedah_books():
    """تحميل كتب العقيدة (أصول الدين)"""
    logger.info("جاري تحميل كتب العقيدة...")
    
    books = [
        {
            "title": "كتاب التوحيد",
            "author": "ابن خزيمة",
            "url": "https://archive.org/download/FP0001/Fp82.pdf"
        },
        {
            "title": "شرح الأصول الثلاثة",
            "author": "محمد بن عبد الوهاب",
            "url": "https://archive.org/download/waq59426/59426.pdf"
        },
        {
            "title": "العقيدة الواسطية",
            "author": "ابن تيمية",
            "url": "https://archive.org/download/WAQ11021/11021.pdf"
        },
        {
            "title": "الاعتقاد",
            "author": "البيهقي",
            "url": "https://archive.org/download/WAQ11017/11017.pdf"
        },
        {
            "title": "العقيدة الطحاوية",
            "author": "الطحاوي",
            "url": "https://archive.org/download/WAQ80518/80518.pdf"
        }
    ]
    
    for book in books:
        file_name = f"{book['author']} - {book['title']}.pdf"
        destination = AQEEDAH_DIR / file_name
        
        if destination.exists():
            logger.info(f"الملف موجود بالفعل: {destination}")
            continue
            
        download_file(book["url"], destination, description=file_name)

# وظيفة تحميل كتب الفقه وأصوله
def download_fiqh_books():
    """تحميل كتب الفقه وأصوله"""
    logger.info("جاري تحميل كتب الفقه...")
    
    books = [
        {
            "title": "رياض الصالحين",
            "author": "النووي",
            "url": "https://archive.org/download/WAQ105662/105662.pdf"
        },
        {
            "title": "مختصر خليل",
            "author": "خليل بن إسماعيل المالكي",
            "url": "https://archive.org/download/FP76897/82_73080.pdf"
        },
        {
            "title": "المغني",
            "author": "ابن قدامة المقدسي",
            "url": "https://archive.org/download/FP0001/Fp92_1.pdf"
        },
        {
            "title": "روضة الطالبين",
            "author": "النووي",
            "url": "https://archive.org/download/WAQ40170/40170.pdf"
        },
        {
            "title": "الفقه على المذاهب الأربعة",
            "author": "عبد الرحمن الجازيري",
            "url": "https://archive.org/download/WAQ14308/14308.pdf"
        }
    ]
    
    for book in books:
        file_name = f"{book['author']} - {book['title']}.pdf"
        destination = FIQH_DIR / file_name
        
        if destination.exists():
            logger.info(f"الملف موجود بالفعل: {destination}")
            continue
            
        download_file(book["url"], destination, description=file_name)

# وظيفة تحميل كتب التفسير
def download_tafsir_books():
    """تحميل كتب التفسير"""
    logger.info("جاري تحميل كتب التفسير...")
    
    # إنشاء تصنيفات فرعية للتفاسير
    classical_tafsir_dir = TAFSIR_BOOKS_DIR / "classical"  # التفاسير الكلاسيكية
    contemporary_tafsir_dir = TAFSIR_BOOKS_DIR / "contemporary"  # التفاسير المعاصرة
    linguistic_tafsir_dir = TAFSIR_BOOKS_DIR / "linguistic"  # التفاسير اللغوية
    thematic_tafsir_dir = TAFSIR_BOOKS_DIR / "thematic"  # التفاسير الموضوعية
    
    # إنشاء المجلدات
    for directory in [
        classical_tafsir_dir, contemporary_tafsir_dir,
        linguistic_tafsir_dir, thematic_tafsir_dir
    ]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ تأكيد وجود المجلد: {directory}")
    
    # التفاسير الكلاسيكية
    classical_tafsirs = [
        # ابن كثير - الإصدارات المختلفة
        {
            "title": "تفسير ابن كثير - المجلد الأول",
            "author": "ابن كثير",
            "url": "https://archive.org/download/WAQ13645/13645.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير ابن كثير - الكامل",
            "author": "ابن كثير",
            "url": "https://ia800701.us.archive.org/32/items/FP73896/73896.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير ابن كثير - مختصر",
            "author": "ابن كثير",
            "url": "https://archive.org/download/moktasartafsiribnkatheerj3/moktasartafsiribnkatheerj1.pdf",
            "directory": classical_tafsir_dir
        },
        
        # القرطبي - الإصدارات المختلفة
        {
            "title": "تفسير القرطبي - المجلد الأول",
            "author": "القرطبي",
            "url": "https://archive.org/download/FP76897/01_73040.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير القرطبي - المجلد الثاني",
            "author": "القرطبي",
            "url": "https://archive.org/download/FP76897/02_73040.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير القرطبي - الجامع لأحكام القرآن",
            "author": "القرطبي",
            "url": "https://ia803202.us.archive.org/24/items/jameealawhkamal/jameealawhkamal.pdf",
            "directory": classical_tafsir_dir
        },
        
        # الطبري - الإصدارات المختلفة
        {
            "title": "تفسير الطبري - المجلد الأول",
            "author": "الطبري",
            "url": "https://archive.org/download/FP76897/01_73041.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير الطبري - المجلد الثاني",
            "author": "الطبري",
            "url": "https://archive.org/download/FP76897/02_73041.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير الطبري - جامع البيان",
            "author": "الطبري",
            "url": "https://archive.org/download/FP73874/73874.pdf",
            "directory": classical_tafsir_dir
        },
        
        # تفاسير كلاسيكية أخرى مهمة
        {
            "title": "تفسير البغوي - معالم التنزيل",
            "author": "البغوي",
            "url": "https://archive.org/download/tafseer_baghawi/tafseer_baghawi.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير الزمخشري - الكشاف",
            "author": "الزمخشري",
            "url": "https://archive.org/download/alkashaf-alzamkhshari/alkashaf-alzamkhshari.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير السعدي",
            "author": "السعدي",
            "url": "https://archive.org/download/WAQ25780/25780.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير الجلالين",
            "author": "السيوطي والمحلي",
            "url": "https://archive.org/download/FP76897/3684_73071.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير البيضاوي - أنوار التنزيل وأسرار التأويل",
            "author": "البيضاوي",
            "url": "https://archive.org/download/anwaar_tanzeel/anwaar_tanzeel.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير ابن الجوزي - زاد المسير",
            "author": "ابن الجوزي",
            "url": "https://archive.org/download/zaad_maseer/zaad_maseer.pdf",
            "directory": classical_tafsir_dir
        },
        {
            "title": "تفسير الشوكاني - فتح القدير",
            "author": "الشوكاني",
            "url": "https://archive.org/download/fath_qadeer/fath_qadeer.pdf",
            "directory": classical_tafsir_dir
        }
    ]
    
    # التفاسير المعاصرة
    contemporary_tafsirs = [
        {
            "title": "تفسير التحرير والتنوير",
            "author": "ابن عاشور",
            "url": "https://archive.org/download/FP140316/01_140316.pdf",
            "directory": contemporary_tafsir_dir
        },
        {
            "title": "في ظلال القرآن",
            "author": "سيد قطب",
            "url": "https://archive.org/download/Fe_Dhelal_Quran/Fe_Dhelal_Quran.pdf",
            "directory": contemporary_tafsir_dir
        },
        {
            "title": "تفسير المنار",
            "author": "محمد رشيد رضا",
            "url": "https://archive.org/download/almnar-tafseer/almnar-tafseer.pdf",
            "directory": contemporary_tafsir_dir
        },
        {
            "title": "تفسير الشعراوي",
            "author": "محمد متولي الشعراوي",
            "url": "https://archive.org/download/tafseer_shaarawi/tafseer_shaarawi.pdf",
            "directory": contemporary_tafsir_dir
        },
        {
            "title": "التفسير الوسيط",
            "author": "محمد سيد طنطاوي",
            "url": "https://archive.org/download/altafsiraltantawi/altafsiraltantawi.pdf",
            "directory": contemporary_tafsir_dir
        }
    ]
    
    # التفاسير اللغوية
    linguistic_tafsirs = [
        {
            "title": "التفسير اللغوي للقرآن الكريم",
            "author": "مساعد الطيار",
            "url": "https://archive.org/download/altafseer_allughawi/altafseer_allughawi.pdf",
            "directory": linguistic_tafsir_dir
        },
        {
            "title": "معاني القرآن",
            "author": "الفراء",
            "url": "https://archive.org/download/maani_quran_faraa/maani_quran_faraa.pdf",
            "directory": linguistic_tafsir_dir
        },
        {
            "title": "البحر المحيط",
            "author": "أبو حيان الأندلسي",
            "url": "https://archive.org/download/bahr_muheet/bahr_muheet.pdf",
            "directory": linguistic_tafsir_dir
        }
    ]
    
    # التفاسير الموضوعية
    thematic_tafsirs = [
        {
            "title": "التفسير الموضوعي للقرآن الكريم",
            "author": "مصطفى مسلم",
            "url": "https://archive.org/download/al-tafseer-mawdoui/al-tafseer-mawdoui.pdf",
            "directory": thematic_tafsir_dir
        },
        {
            "title": "المعجزة الكبرى - القرآن",
            "author": "محمد أبو زهرة",
            "url": "https://archive.org/download/moajiza_kubra_quran/moajiza_kubra_quran.pdf",
            "directory": thematic_tafsir_dir
        }
    ]
    
    # دمج جميع التفاسير
    all_tafsirs = classical_tafsirs + contemporary_tafsirs + linguistic_tafsirs + thematic_tafsirs
    
    # تحميل جميع كتب التفسير
    for book in all_tafsirs:
        file_name = f"{book['author']} - {book['title']}.pdf"
        destination = book['directory'] / file_name
        
        if destination.exists():
            logger.info(f"الملف موجود بالفعل: {destination}")
            continue
            
        download_file(book["url"], destination, description=file_name)
{{ ... }}

def download_tafsir_hashiyat():
    """تحميل حواشي التفاسير وتعليقات العلماء عليها"""
    logger.info("جاري تحميل حواشي التفاسير...")
    
    # إنشاء المجلد
    hashiyat_dir = TAFSIR_BOOKS_DIR / "hashiyat"
    hashiyat_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"✅ تأكيد وجود المجلد: {hashiyat_dir}")
    
    # قائمة الحواشي
    hashiyat_books = [
        {
            "title": "حاشية الشهاب على البيضاوي",
            "author": "شهاب الدين الخفاجي",
            "url": "https://archive.org/download/hashiyat_shihab/hashiyat_shihab.pdf",
        },
        {
            "title": "حاشية الصاوي على الجلالين",
            "author": "أحمد الصاوي",
            "url": "https://archive.org/download/hashiyat_sawi/hashiyat_sawi.pdf",
        },
        {
            "title": "عناية القاضي وكفاية الراضي على تفسير البيضاوي",
            "author": "الشهاب الخفاجي",
            "url": "https://archive.org/download/inayat_qadi/inayat_qadi.pdf",
        },
        {
            "title": "حاشية القونوي على تفسير البيضاوي",
            "author": "عصام الدين القونوي",
            "url": "https://archive.org/download/hashiyat_qunawi/hashiyat_qunawi.pdf",
        },
        {
            "title": "حاشية زاده على البيضاوي",
            "author": "محي الدين شيخ زاده",
            "url": "https://archive.org/download/hashiyat_sheikzadeh/hashiyat_sheikzadeh.pdf",
        }
    ]
    
    # تحميل الكتب
    for book in hashiyat_books:
        file_name = f"{book['author']} - {book['title']}.pdf"
        destination = hashiyat_dir / file_name
        
        if destination.exists():
            logger.info(f"الملف موجود بالفعل: {destination}")
            continue
            
        download_file(book["url"], destination, description=file_name)

def download_islamic_heritage_books():
    """تحميل كتب التراث الإسلامي"""
    logger.info("جاري تحميل كتب التراث الإسلامي...")
    
    # إنشاء مجلدات فرعية للتنظيم
    language_books_dir = HERITAGE_BOOKS_DIR / "language"  # كتب اللغة
    literature_books_dir = HERITAGE_BOOKS_DIR / "literature"  # كتب الأدب
    history_books_dir = HERITAGE_BOOKS_DIR / "history"  # كتب التاريخ
    philosophy_books_dir = HERITAGE_BOOKS_DIR / "philosophy"  # كتب الفلسفة والمنطق
    
    # إنشاء المجلدات
    for directory in [
        language_books_dir, literature_books_dir, history_books_dir, philosophy_books_dir
    ]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ تأكيد وجود المجلد: {directory}")
    
    # كتب اللغة
    language_books = [
        {
            "title": "لسان العرب",
            "author": "ابن منظور",
            "url": "https://archive.org/download/WAQ10376_201312/10376.pdf",
            "directory": language_books_dir
        },
        {
            "title": "مقاييس اللغة",
            "author": "ابن فارس",
            "url": "https://archive.org/download/waq101269/101269.pdf",
            "directory": language_books_dir
        },
        {
            "title": "الصحاح تاج اللغة وصحاح العربية",
            "author": "الجوهري",
            "url": "https://archive.org/download/WAQ29574/29574.pdf",
            "directory": language_books_dir
        },
        {
            "title": "النحو الوافي",
            "author": "عباس حسن",
            "url": "https://archive.org/download/WAQ95058/95058.pdf",
            "directory": language_books_dir
        }
    ]
    
    # كتب الأدب
    literature_books = [
        {
            "title": "البيان والتبيين",
            "author": "الجاحظ",
            "url": "https://archive.org/download/WAQ33264/33264.pdf",
            "directory": literature_books_dir
        },
        {
            "title": "الشعر والشعراء",
            "author": "ابن قتيبة",
            "url": "https://archive.org/download/FP76897/01_76897.pdf",
            "directory": literature_books_dir
        },
        {
            "title": "العقد الفريد",
            "author": "ابن عبد ربه",
            "url": "https://archive.org/download/WAQ13301/13301.pdf",
            "directory": literature_books_dir
        },
        {
            "title": "الكامل في اللغة والأدب",
            "author": "المبرد",
            "url": "https://archive.org/download/WAQ33263/33263.pdf",
            "directory": literature_books_dir
        }
    ]
    
    # كتب التاريخ
    history_books = [
        {
            "title": "تاريخ الطبري",
            "author": "الطبري",
            "url": "https://archive.org/download/WAQ19926/19926.pdf",
            "directory": history_books_dir
        },
        {
            "title": "البداية والنهاية",
            "author": "ابن كثير",
            "url": "https://archive.org/download/WAQ20217/20217.pdf",
            "directory": history_books_dir
        },
        {
            "title": "الكامل في التاريخ",
            "author": "ابن الأثير",
            "url": "https://archive.org/download/WAQ26529/26529.pdf",
            "directory": history_books_dir
        },
        {
            "title": "مروج الذهب ومعادن الجوهر",
            "author": "المسعودي",
            "url": "https://archive.org/download/WAQ19398/19398.pdf",
            "directory": history_books_dir
        }
    ]
    
    # كتب الفلسفة والمنطق
    philosophy_books = [
        {
            "title": "تهافت الفلاسفة",
            "author": "الغزالي",
            "url": "https://archive.org/download/tahafut_falasifa/tahafut_falasifa.pdf",
            "directory": philosophy_books_dir
        },
        {
            "title": "فصل المقال",
            "author": "ابن رشد",
            "url": "https://archive.org/download/fasl_maqal/fasl_maqal.pdf",
            "directory": philosophy_books_dir
        },
        {
            "title": "رسائل إخوان الصفا",
            "author": "إخوان الصفا",
            "url": "https://archive.org/download/rasail_ikhwan_safa/rasail_ikhwan_safa.pdf",
            "directory": philosophy_books_dir
        },
        {
            "title": "الشفاء - المنطق",
            "author": "ابن سينا",
            "url": "https://archive.org/download/shifa_logic/shifa_logic.pdf",
            "directory": philosophy_books_dir
        }
    ]
    
    # دمج جميع الكتب
    all_heritage_books = language_books + literature_books + history_books + philosophy_books
    
    # تحميل الكتب
    for book in all_heritage_books:
        file_name = f"{book['author']} - {book['title']}.pdf"
        destination = book['directory'] / file_name
        
        if destination.exists():
            logger.info(f"الملف موجود بالفعل: {destination}")
            continue
            
        download_file(book["url"], destination, description=file_name)
{{ ... }}

if __name__ == "__main__":
    # تهيئة جميع المجلدات الأساسية
    create_directories()
    
    # تنفيذ عمليات التحميل
    download_quran_copies()
    download_tafsir_books()
    download_scientific_miracles()
    download_numerical_miracles()
    download_science_and_faith()
    download_hadith_books()
    download_aqeedah_books()
    download_fiqh_books()
    download_seerah_books()
    download_tafsir_hashiyat()
    download_islamic_heritage_books()
    
    logger.info("✅ تم الانتهاء من تحميل جميع الموارد!")
{{ ... }}
