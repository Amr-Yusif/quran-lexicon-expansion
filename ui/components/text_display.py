"""
مكونات عرض النصوص - لعرض الآيات القرآنية والتفاسير
"""
import streamlit as st
from typing import Dict, List, Any, Optional
import pandas as pd
import json
from pathlib import Path
import os

def display_verse_with_tafseer(surah_name: str, ayah_number: int, tafseer_name: str = "ar.muyassar") -> None:
    """
    عرض آية قرآنية مع تفسيرها

    Args:
        surah_name: اسم السورة
        ayah_number: رقم الآية
        tafseer_name: اسم التفسير
    """
    # محاولة تحميل بيانات القرآن
    quran_data = _load_quran_data()
    
    # محاولة تحميل بيانات التفسير
    tafseer_data = _load_tafseer_data(tafseer_name)
    
    # العثور على رقم السورة
    surah_number = _get_surah_number(surah_name)
    
    if not quran_data or not surah_number:
        st.error(f"لم يمكن العثور على السورة: {surah_name}")
        return
    
    # البحث عن الآية
    verse = _find_verse(quran_data, surah_number, ayah_number)
    
    if not verse:
        st.error(f"لم يمكن العثور على الآية رقم {ayah_number} في سورة {surah_name}")
        return
    
    # عرض الآية
    st.markdown(f"### {surah_name} ({ayah_number})")
    
    # تحويل نص الآية إلى تنسيق مميز
    verse_text = verse.get("text", "")
    st.markdown(f'<div dir="rtl" style="font-size: 24px; background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 20px;">{verse_text}</div>', unsafe_allow_html=True)
    
    # عرض التفسير إذا كان متاحًا
    if tafseer_data:
        tafseer = _find_tafseer(tafseer_data, surah_number, ayah_number)
        if tafseer:
            st.subheader(f"تفسير {_get_tafseer_name(tafseer_name)}")
            st.markdown(f'<div dir="rtl" style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">{tafseer}</div>', unsafe_allow_html=True)
        else:
            st.info("التفسير غير متوفر لهذه الآية")

def display_verses_comparison(surah_name: str, start_ayah: int, end_ayah: int, tafseer_names: List[str] = None) -> None:
    """
    عرض مقارنة بين آيات متتالية مع تفاسير متعددة

    Args:
        surah_name: اسم السورة
        start_ayah: رقم الآية البداية
        end_ayah: رقم الآية النهاية
        tafseer_names: قائمة بأسماء التفاسير
    """
    if tafseer_names is None:
        tafseer_names = ["ar.muyassar", "ar.jalalayn"]
    
    # محاولة تحميل بيانات القرآن
    quran_data = _load_quran_data()
    
    # العثور على رقم السورة
    surah_number = _get_surah_number(surah_name)
    
    if not quran_data or not surah_number:
        st.error(f"لم يمكن العثور على السورة: {surah_name}")
        return
    
    # تحميل التفاسير
    tafseer_data_dict = {}
    for tafseer_name in tafseer_names:
        tafseer_data = _load_tafseer_data(tafseer_name)
        if tafseer_data:
            tafseer_data_dict[tafseer_name] = tafseer_data
    
    # عرض عنوان
    st.markdown(f"### مقارنة الآيات {start_ayah}-{end_ayah} من سورة {surah_name}")
    
    # عرض كل آية على حدة
    for ayah_number in range(start_ayah, end_ayah + 1):
        # البحث عن الآية
        verse = _find_verse(quran_data, surah_number, ayah_number)
        
        if not verse:
            st.warning(f"لم يمكن العثور على الآية رقم {ayah_number}")
            continue
        
        # عرض الآية
        st.markdown(f"#### الآية {ayah_number}")
        verse_text = verse.get("text", "")
        st.markdown(f'<div dir="rtl" style="font-size: 20px; background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 10px;">{verse_text}</div>', unsafe_allow_html=True)
        
        # عرض التفاسير
        if tafseer_data_dict:
            tabs = st.tabs([_get_tafseer_name(name) for name in tafseer_names])
            
            for i, (tafseer_name, tab) in enumerate(zip(tafseer_names, tabs)):
                with tab:
                    if tafseer_name in tafseer_data_dict:
                        tafseer = _find_tafseer(tafseer_data_dict[tafseer_name], surah_number, ayah_number)
                        if tafseer:
                            st.markdown(f'<div dir="rtl" style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">{tafseer}</div>', unsafe_allow_html=True)
                        else:
                            st.info("التفسير غير متوفر لهذه الآية")
        
        st.markdown("---")

def display_miracle_card(miracle: Dict[str, Any]) -> None:
    """
    عرض بطاقة معجزة علمية

    Args:
        miracle: بيانات المعجزة العلمية
    """
    # عرض بطاقة بتصميم جذاب
    st.markdown(f"""
    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px; background-color: #f9f9f9;">
        <h3 style="color: #1e3d59;">{miracle.get('title', 'معجزة علمية')}</h3>
        <div style="margin: 10px 0;">
            <span style="background-color: #17a2b8; color: white; padding: 3px 8px; border-radius: 5px; font-size: 0.8em;">
                {miracle.get('category', 'عامة')}
            </span>
        </div>
        <p style="color: #333;">{miracle.get('description', '')}</p>
        <div style="border-top: 1px solid #ddd; margin-top: 10px; padding-top: 10px;">
            <h4 style="color: #6b7a8f;">الدليل العلمي:</h4>
            <p>{miracle.get('evidence', '')}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض الآيات المرتبطة
    if "verses" in miracle and miracle["verses"]:
        st.markdown("### الآيات القرآنية المرتبطة")
        
        for verse in miracle["verses"]:
            surah = verse.get("surah", "")
            ayah = verse.get("ayah", 0)
            text = verse.get("text", "")
            
            if surah and ayah:
                with st.expander(f"{surah} ({ayah})"):
                    if text:
                        st.markdown(f'<div dir="rtl" style="font-size: 18px; background-color: #f0f8ff; padding: 10px; border-radius: 5px;">{text}</div>', unsafe_allow_html=True)
                    else:
                        try:
                            display_verse_with_tafseer(surah, ayah)
                        except Exception as e:
                            st.error(f"خطأ في عرض الآية: {str(e)}")

def display_search_results(results: List[Dict[str, Any]], title: str = "نتائج البحث") -> None:
    """
    عرض نتائج البحث بشكل منظم

    Args:
        results: قائمة نتائج البحث
        title: عنوان النتائج
    """
    st.subheader(title)
    
    if not results:
        st.info("لم يتم العثور على نتائج")
        return
    
    # عرض عدد النتائج
    st.success(f"تم العثور على {len(results)} نتيجة")
    
    # عرض كل نتيجة
    for i, result in enumerate(results):
        similarity = result.get("similarity", 0)
        similarity_percentage = f"{similarity:.0%}" if similarity <= 1 else f"{similarity:.2f}"
        
        with st.expander(f"{i+1}. {result.get('title', 'نتيجة')} (التطابق: {similarity_percentage})"):
            # عرض محتوى النتيجة
            if "type" in result and result["type"] == "miracle":
                display_miracle_card(result)
            else:
                # عرض محتوى النتيجة العام
                st.markdown(f"**الوصف:** {result.get('description', 'لا يوجد وصف')}")
                if "content" in result and result["content"]:
                    st.markdown(f"**المحتوى:** {result['content']}")
                
                # عرض البيانات الوصفية
                if "metadata" in result and result["metadata"]:
                    with st.expander("البيانات الوصفية"):
                        for key, value in result["metadata"].items():
                            st.write(f"**{key}:** {value}")

# دوال مساعدة داخلية
def _load_quran_data() -> Dict[str, Any]:
    """
    تحميل بيانات القرآن الكريم

    Returns:
        بيانات القرآن الكريم
    """
    # البحث عن ملف بيانات القرآن
    data_paths = [
        Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data" / "quran" / "quran.json",
        Path(os.path.dirname(os.path.abspath(__file__))).parent.parent.parent / "data" / "quran" / "quran.json"
    ]
    
    for path in data_paths:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"خطأ في تحميل بيانات القرآن: {str(e)}")
    
    return None

def _load_tafseer_data(tafseer_name: str) -> Dict[str, Any]:
    """
    تحميل بيانات التفسير

    Args:
        tafseer_name: اسم التفسير

    Returns:
        بيانات التفسير
    """
    # البحث عن ملف بيانات التفسير
    data_paths = [
        Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data" / "tafseer" / f"{tafseer_name}.json",
        Path(os.path.dirname(os.path.abspath(__file__))).parent.parent.parent / "data" / "tafseer" / f"{tafseer_name}.json"
    ]
    
    for path in data_paths:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"خطأ في تحميل بيانات التفسير: {str(e)}")
    
    return None

def _get_surah_number(surah_name: str) -> Optional[int]:
    """
    الحصول على رقم السورة من اسمها

    Args:
        surah_name: اسم السورة

    Returns:
        رقم السورة (1-114) أو None إذا لم يتم العثور عليها
    """
    # قائمة بأسماء السور
    surah_names = [
        'الفاتحة', 'البقرة', 'آل عمران', 'النساء', 'المائدة', 'الأنعام', 'الأعراف', 'الأنفال', 'التوبة', 'يونس',
        'هود', 'يوسف', 'الرعد', 'إبراهيم', 'الحجر', 'النحل', 'الإسراء', 'الكهف', 'مريم', 'طه',
        'الأنبياء', 'الحج', 'المؤمنون', 'النور', 'الفرقان', 'الشعراء', 'النمل', 'القصص', 'العنكبوت', 'الروم',
        'لقمان', 'السجدة', 'الأحزاب', 'سبأ', 'فاطر', 'يس', 'الصافات', 'ص', 'الزمر', 'غافر',
        'فصلت', 'الشورى', 'الزخرف', 'الدخان', 'الجاثية', 'الأحقاف', 'محمد', 'الفتح', 'الحجرات', 'ق',
        'الذاريات', 'الطور', 'النجم', 'القمر', 'الرحمن', 'الواقعة', 'الحديد', 'المجادلة', 'الحشر', 'الممتحنة',
        'الصف', 'الجمعة', 'المنافقون', 'التغابن', 'الطلاق', 'التحريم', 'الملك', 'القلم', 'الحاقة', 'المعارج',
        'نوح', 'الجن', 'المزمل', 'المدثر', 'القيامة', 'الإنسان', 'المرسلات', 'النبأ', 'النازعات', 'عبس',
        'التكوير', 'الانفطار', 'المطففين', 'الانشقاق', 'البروج', 'الطارق', 'الأعلى', 'الغاشية', 'الفجر', 'البلد',
        'الشمس', 'الليل', 'الضحى', 'الشرح', 'التين', 'العلق', 'القدر', 'البينة', 'الزلزلة', 'العاديات',
        'القارعة', 'التكاثر', 'العصر', 'الهمزة', 'الفيل', 'قريش', 'الماعون', 'الكوثر', 'الكافرون', 'النصر',
        'المسد', 'الإخلاص', 'الفلق', 'الناس'
    ]
    
    try:
        # البحث عن اسم السورة في القائمة
        return surah_names.index(surah_name) + 1
    except ValueError:
        return None

def _find_verse(quran_data: Dict[str, Any], surah_number: int, ayah_number: int) -> Optional[Dict[str, Any]]:
    """
    البحث عن آية في بيانات القرآن

    Args:
        quran_data: بيانات القرآن
        surah_number: رقم السورة
        ayah_number: رقم الآية

    Returns:
        بيانات الآية أو None
    """
    try:
        if not quran_data or not isinstance(quran_data, dict):
            return None
        
        # البحث عن السورة
        surahs = quran_data.get("data", {}).get("surahs", [])
        surah = next((s for s in surahs if s.get("number") == surah_number), None)
        
        if not surah:
            return None
        
        # البحث عن الآية
        ayahs = surah.get("ayahs", [])
        ayah = next((a for a in ayahs if a.get("numberInSurah") == ayah_number), None)
        
        return ayah
    except Exception as e:
        st.error(f"خطأ في البحث عن الآية: {str(e)}")
        return None

def _find_tafseer(tafseer_data: Dict[str, Any], surah_number: int, ayah_number: int) -> Optional[str]:
    """
    البحث عن تفسير آية

    Args:
        tafseer_data: بيانات التفسير
        surah_number: رقم السورة
        ayah_number: رقم الآية

    Returns:
        نص التفسير أو None
    """
    try:
        if not tafseer_data or not isinstance(tafseer_data, list):
            return None
        
        # البحث عن التفسير
        tafseer_item = next((t for t in tafseer_data if 
                           t.get("surah_number") == surah_number and 
                           t.get("ayah_number") == ayah_number), None)
        
        if tafseer_item:
            return tafseer_item.get("text")
        
        return None
    except Exception as e:
        st.error(f"خطأ في البحث عن التفسير: {str(e)}")
        return None

def _get_tafseer_name(tafseer_id: str) -> str:
    """
    الحصول على اسم التفسير المعروض من معرفه

    Args:
        tafseer_id: معرف التفسير

    Returns:
        اسم التفسير للعرض
    """
    tafseer_names = {
        "ar.muyassar": "التفسير الميسر",
        "ar.jalalayn": "تفسير الجلالين",
        "ar.waseet": "التفسير الوسيط",
        "ar.kashf": "تفسير الكشاف",
        "ar.tabari": "تفسير الطبري",
        "ar.qurtubi": "تفسير القرطبي",
        "ar.ibnkathir": "تفسير ابن كثير",
        "en.sahih": "Sahih International"
    }
    
    return tafseer_names.get(tafseer_id, tafseer_id)
