"""
محمل ملفات PDF - تحليل وتجهيز الكتب الإسلامية
"""
import os
import json
import fitz  # PyMuPDF
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import re

class PDFLoader:
    """
    محمل ملفات PDF - يتولى تحليل الكتب الإسلامية وتجهيزها للتضمين
    """
    
    def __init__(self, data_dir: str = None):
        """
        تهيئة محمل ملفات PDF

        Args:
            data_dir: مسار مجلد البيانات (اختياري)
        """
        if data_dir is None:
            # استخدام المجلد الافتراضي إذا لم يتم تحديد مجلد
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        else:
            self.data_dir = data_dir
        
        # التأكد من وجود مجلد البيانات
        self.books_dir = os.path.join(self.data_dir, "books")
        self.extracts_dir = os.path.join(self.data_dir, "extracts")
        os.makedirs(self.books_dir, exist_ok=True)
        os.makedirs(self.extracts_dir, exist_ok=True)
        
        # تهيئة مسارات الملفات
        self.metadata_file = os.path.join(self.books_dir, "metadata.json")
        
        # تهيئة ملف البيانات الوصفية إذا لم يكن موجودًا
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
    
    def load_pdf(self, pdf_path: str, category: str = "other") -> Dict[str, Any]:
        """
        تحميل وتحليل ملف PDF

        Args:
            pdf_path: مسار ملف PDF
            category: فئة الكتاب (القرآن، الحديث، الفقه، إلخ)

        Returns:
            معلومات الكتاب مع مسار النسخة المحفوظة
        """
        try:
            # التحقق من وجود الملف
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"ملف PDF غير موجود: {pdf_path}")
            
            # حساب معرف فريد للكتاب
            file_hash = self._compute_file_hash(pdf_path)
            
            # استخراج اسم الملف
            file_name = os.path.basename(pdf_path)
            base_name, _ = os.path.splitext(file_name)
            
            # مسار النسخة المحفوظة
            saved_path = os.path.join(self.books_dir, f"{file_hash}_{file_name}")
            
            # نسخ الملف إلى مجلد الكتب إذا لم يكن موجودًا بالفعل
            if not os.path.exists(saved_path):
                import shutil
                shutil.copy2(pdf_path, saved_path)
            
            # استخراج البيانات الوصفية من الملف
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            # استخراج المعلومات والعنوان
            metadata = doc.metadata
            title = metadata.get("title", base_name)
            
            # استخراج نص من الصفحات الأولى لتحسين اكتشاف المعلومات
            first_pages_text = ""
            for i in range(min(5, total_pages)):
                page = doc[i]
                first_pages_text += page.get_text()
            
            # محاولة تحسين اكتشاف العنوان والمؤلف من النص
            extracted_title = self._extract_title(first_pages_text) or title
            author = metadata.get("author", "")
            extracted_author = self._extract_author(first_pages_text) or author
            
            # إغلاق المستند
            doc.close()
            
            # إنشاء كائن معلومات الكتاب
            book_info = {
                "id": file_hash,
                "title": extracted_title,
                "author": extracted_author,
                "filename": file_name,
                "path": saved_path,
                "pages": total_pages,
                "category": category,
                "metadata": metadata,
                "processed": False,
                "chunks": 0
            }
            
            # حفظ معلومات الكتاب
            self._save_book_metadata(book_info)
            
            return book_info
        
        except Exception as e:
            print(f"خطأ في تحميل ملف PDF: {str(e)}")
            return {}
    
    def process_pdf(self, book_id: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """
        معالجة ملف PDF وتقسيمه إلى قطع نصية

        Args:
            book_id: معرف الكتاب
            chunk_size: حجم القطعة النصية
            overlap: حجم التداخل بين القطع

        Returns:
            قائمة من قطع النص المستخرجة
        """
        try:
            # تحميل بيانات الكتب
            books = self._load_books_metadata()
            
            # البحث عن الكتاب
            book_info = None
            for book in books:
                if book.get("id") == book_id:
                    book_info = book
                    break
            
            if not book_info:
                raise ValueError(f"لم يتم العثور على الكتاب بالمعرف: {book_id}")
            
            # مسار ملف الكتاب
            pdf_path = book_info.get("path")
            
            # التحقق من وجود الملف
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"ملف PDF غير موجود: {pdf_path}")
            
            # فتح المستند
            doc = fitz.open(pdf_path)
            
            # قائمة القطع النصية
            chunks = []
            
            # تقسيم النص إلى قطع
            current_chunk = ""
            current_chunk_pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                
                # تنظيف النص
                page_text = self._clean_text(page_text)
                
                # إضافة النص إلى القطعة الحالية
                if len(current_chunk) + len(page_text) <= chunk_size:
                    # يمكن إضافة الصفحة كاملة إلى القطعة الحالية
                    current_chunk += page_text
                    current_chunk_pages.append(page_num)
                else:
                    # القطعة الحالية ستتجاوز الحد، تخزينها وبدء قطعة جديدة
                    if current_chunk:
                        chunk_id = f"{book_id}_chunk_{len(chunks)}"
                        chunk = {
                            "id": chunk_id,
                            "book_id": book_id,
                            "text": current_chunk,
                            "pages": current_chunk_pages,
                            "metadata": {
                                "title": book_info.get("title"),
                                "author": book_info.get("author"),
                                "category": book_info.get("category"),
                                "source": "pdf"
                            }
                        }
                        chunks.append(chunk)
                    
                    # بدء قطعة جديدة مع النص المتداخل
                    if overlap > 0 and current_chunk:
                        # استخراج النص المتداخل من نهاية القطعة السابقة
                        overlap_text = current_chunk[-overlap:]
                        current_chunk = overlap_text + page_text
                    else:
                        current_chunk = page_text
                    
                    current_chunk_pages = [page_num]
            
            # إضافة القطعة الأخيرة إذا كانت غير فارغة
            if current_chunk:
                chunk_id = f"{book_id}_chunk_{len(chunks)}"
                chunk = {
                    "id": chunk_id,
                    "book_id": book_id,
                    "text": current_chunk,
                    "pages": current_chunk_pages,
                    "metadata": {
                        "title": book_info.get("title"),
                        "author": book_info.get("author"),
                        "category": book_info.get("category"),
                        "source": "pdf"
                    }
                }
                chunks.append(chunk)
            
            # إغلاق المستند
            doc.close()
            
            # تحديث معلومات الكتاب
            book_info["processed"] = True
            book_info["chunks"] = len(chunks)
            self._update_book_metadata(book_info)
            
            # حفظ القطع النصية
            chunks_file = os.path.join(self.extracts_dir, f"{book_id}_chunks.json")
            with open(chunks_file, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, ensure_ascii=False, indent=4)
            
            return chunks
        
        except Exception as e:
            print(f"خطأ في معالجة ملف PDF: {str(e)}")
            return []
    
    def get_book_chunks(self, book_id: str) -> List[Dict[str, Any]]:
        """
        الحصول على قطع نصية لكتاب معين

        Args:
            book_id: معرف الكتاب

        Returns:
            قائمة من قطع النص المستخرجة
        """
        try:
            # التحقق من وجود ملف القطع
            chunks_file = os.path.join(self.extracts_dir, f"{book_id}_chunks.json")
            
            if os.path.exists(chunks_file):
                with open(chunks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # إذا لم يكن الملف موجودًا، قم بمعالجة الكتاب
            return self.process_pdf(book_id)
        
        except Exception as e:
            print(f"خطأ في الحصول على قطع الكتاب: {str(e)}")
            return []
    
    def get_all_books(self) -> List[Dict[str, Any]]:
        """
        الحصول على قائمة جميع الكتب

        Returns:
            قائمة معلومات الكتب
        """
        return self._load_books_metadata()
    
    def get_books_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        الحصول على قائمة الكتب حسب الفئة

        Args:
            category: فئة الكتب

        Returns:
            قائمة معلومات الكتب في الفئة المحددة
        """
        all_books = self._load_books_metadata()
        return [book for book in all_books if book.get("category") == category]
    
    def prepare_book_embeddings(self, book_id: str) -> List[Dict[str, Any]]:
        """
        إعداد قطع كتاب للتضمين

        Args:
            book_id: معرف الكتاب

        Returns:
            قائمة من قطع النص المعدة للتضمين
        """
        chunks = self.get_book_chunks(book_id)
        
        # إعداد كل قطعة للتضمين
        embedding_data = []
        for chunk in chunks:
            embedding_record = {
                "id": chunk.get("id"),
                "text": chunk.get("text"),
                "metadata": chunk.get("metadata", {})
            }
            
            # إضافة معلومات الصفحات
            embedding_record["metadata"]["pages"] = chunk.get("pages", [])
            embedding_record["metadata"]["book_id"] = book_id
            
            embedding_data.append(embedding_record)
        
        return embedding_data
    
    def load_document(self, pdf_path: str) -> str:
        """
        تحميل مستند PDF واستخراج النص منه

        Args:
            pdf_path: مسار ملف PDF

        Returns:
            النص المستخرج من المستند
        """
        try:
            # التحقق من وجود الملف
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"ملف PDF غير موجود: {pdf_path}")
            
            # فتح المستند
            doc = fitz.open(pdf_path)
            
            # استخراج النص من جميع الصفحات
            text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
            
            # إغلاق المستند
            doc.close()
            
            # تنظيف النص المستخرج
            cleaned_text = self._clean_text(text)
            
            return cleaned_text
        
        except Exception as e:
            print(f"خطأ في تحميل المستند PDF: {str(e)}")
            return ""
    
    def _compute_file_hash(self, file_path: str) -> str:
        """
        حساب قيمة تجزئة (hash) للملف

        Args:
            file_path: مسار الملف

        Returns:
            قيمة التجزئة كسلسلة نصية
        """
        hash_md5 = hashlib.md5()
        
        with open(file_path, "rb") as f:
            # قراءة وتجزئة الملف بشكل تدريجي
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def _save_book_metadata(self, book_info: Dict[str, Any]) -> bool:
        """
        حفظ معلومات كتاب في ملف البيانات الوصفية

        Args:
            book_info: معلومات الكتاب

        Returns:
            نجاح العملية
        """
        try:
            books = self._load_books_metadata()
            
            # التحقق مما إذا كان الكتاب موجودًا بالفعل
            book_exists = False
            for i, book in enumerate(books):
                if book.get("id") == book_info.get("id"):
                    # تحديث معلومات الكتاب الموجود
                    books[i] = book_info
                    book_exists = True
                    break
            
            # إضافة الكتاب إذا لم يكن موجودًا
            if not book_exists:
                books.append(book_info)
            
            # حفظ البيانات المحدثة
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(books, f, ensure_ascii=False, indent=4)
            
            return True
        
        except Exception as e:
            print(f"خطأ في حفظ معلومات الكتاب: {str(e)}")
            return False
    
    def _update_book_metadata(self, book_info: Dict[str, Any]) -> bool:
        """
        تحديث معلومات كتاب موجود

        Args:
            book_info: معلومات الكتاب المحدثة

        Returns:
            نجاح العملية
        """
        return self._save_book_metadata(book_info)
    
    def _load_books_metadata(self) -> List[Dict[str, Any]]:
        """
        تحميل معلومات جميع الكتب

        Returns:
            قائمة معلومات الكتب
        """
        try:
            # التحقق من وجود الملف
            if not os.path.exists(self.metadata_file):
                return []
            
            # تحميل البيانات
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            print(f"خطأ في تحميل معلومات الكتب: {str(e)}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """
        تنظيف وتنسيق النص المستخرج من PDF

        Args:
            text: النص الأصلي

        Returns:
            النص المنظف
        """
        # إزالة الأسطر الفارغة المتعددة
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # إزالة المسافات الزائدة
        text = ' '.join(text.split())
        
        # استبدال المسافات المتعددة بمسافة واحدة
        text = re.sub(r' +', ' ', text)
        
        return text
    
    def _extract_title(self, text: str) -> Optional[str]:
        """
        استخراج عنوان الكتاب من النص

        Args:
            text: النص

        Returns:
            العنوان المستخرج أو None إذا لم يتم العثور عليه
        """
        # البحث عن أنماط عنوان شائعة باللغة العربية
        patterns = [
            r'كتاب\s+([^\n]+)',
            r'عنوان الكتاب[:\s]+([^\n]+)',
            r'اسم الكتاب[:\s]+([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_author(self, text: str) -> Optional[str]:
        """
        استخراج اسم المؤلف من النص

        Args:
            text: النص

        Returns:
            اسم المؤلف المستخرج أو None إذا لم يتم العثور عليه
        """
        # البحث عن أنماط اسم المؤلف الشائعة باللغة العربية
        patterns = [
            r'تأليف[:\s]+([^\n]+)',
            r'المؤلف[:\s]+([^\n]+)',
            r'إعداد[:\s]+([^\n]+)',
            r'للشيخ[:\s]+([^\n]+)',
            r'للإمام[:\s]+([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
