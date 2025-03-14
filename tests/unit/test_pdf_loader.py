#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وحدة لمحمل ملفات PDF
"""

import pytest
import os
import sys
import json
import tempfile
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

# إضافة المجلد الرئيسي للمشروع إلى مسار Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# استيراد الوحدة المراد اختبارها
from core.data_loaders.pdf_loader import PDFLoader


class TestPDFLoader:
    """اختبارات لمحمل ملفات PDF"""

    @pytest.fixture
    def pdf_loader(self, tmp_path):
        """إعداد محمل ملفات PDF للاختبارات"""
        # استخدام مجلد مؤقت للاختبارات
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        return PDFLoader(data_dir=str(data_dir))

    def test_initialization(self, pdf_loader):
        """اختبار تهيئة محمل ملفات PDF"""
        assert pdf_loader is not None
        assert os.path.exists(pdf_loader.books_dir)
        assert os.path.exists(pdf_loader.extracts_dir)
        assert os.path.exists(pdf_loader.metadata_file)

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('os.path.exists', return_value=True)
    @patch('fitz.open')
    @patch('shutil.copy2')
    @patch('builtins.print')
    def test_load_pdf(self, mock_print, mock_copy, mock_fitz_open, mock_path_exists, mock_file, pdf_loader):
        """اختبار تحميل ملف PDF"""
        # تجهيز المستندات المزيفة
        mock_doc = MagicMock()
        mock_doc.metadata = {
            "title": "عنوان الكتاب",
            "author": "اسم المؤلف"
        }
        mock_doc.__len__.return_value = 100  # عدد الصفحات
        
        # تجهيز صفحة مزيفة
        mock_page = MagicMock()
        mock_page.get_text.return_value = "محتوى نصي للصفحة"
        mock_doc.__getitem__.return_value = mock_page
        
        # تعيين المستند المزيف كقيمة إرجاع لـ fitz.open
        mock_fitz_open.return_value = mock_doc
        
        # تجهيز دالة _compute_file_hash المزيفة
        with patch.object(pdf_loader, '_compute_file_hash', return_value="abc123"):
            with patch.object(pdf_loader, '_extract_title', return_value="العنوان المستخرج"):
                with patch.object(pdf_loader, '_extract_author', return_value="المؤلف المستخرج"):
                    with patch.object(pdf_loader, '_save_book_metadata') as mock_save:
                        # اختبار تحميل PDF
                        book_info = pdf_loader.load_pdf("/path/to/test.pdf", category="فقه")
                        
                        # التحقق من النتائج
                        assert book_info["id"] == "abc123"
                        assert book_info["title"] == "العنوان المستخرج"
                        assert book_info["author"] == "المؤلف المستخرج"
                        assert book_info["category"] == "فقه"
                        assert book_info["pages"] == 100
                        assert book_info["processed"] == False
                        
                        # التحقق من النسخ
                        mock_copy.assert_called_once()
                        
                        # التحقق من حفظ البيانات الوصفية
                        mock_save.assert_called_once_with(book_info)

    @patch('os.path.exists', return_value=True)
    @patch('builtins.print')
    def test_load_pdf_file_not_found(self, mock_print, mock_path_exists, pdf_loader):
        """اختبار سلوك تحميل ملف PDF غير موجود"""
        # تغيير سلوك os.path.exists للإشارة إلى أن الملف غير موجود
        mock_path_exists.return_value = False
        
        # اختبار تحميل ملف غير موجود
        book_info = pdf_loader.load_pdf("/path/to/nonexistent.pdf")
        
        # التحقق من أن النتيجة فارغة
        assert book_info == {}
        
        # التحقق من طباعة الخطأ
        mock_print.assert_called_once()
        assert "FileNotFoundError" in str(mock_print.call_args)

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('os.path.exists', return_value=True)
    @patch('json.load')
    @patch('json.dump')
    @patch('builtins.print')
    def test_save_book_metadata(self, mock_print, mock_json_dump, mock_json_load, mock_path_exists, mock_file, pdf_loader):
        """اختبار حفظ البيانات الوصفية للكتاب"""
        # تجهيز بيانات كتب مزيفة
        mock_books = []
        mock_json_load.return_value = mock_books
        
        # كتاب جديد للإضافة
        new_book = {
            "id": "test123",
            "title": "كتاب اختباري",
            "author": "مؤلف اختباري"
        }
        
        # استدعاء الدالة المختبرة
        pdf_loader._save_book_metadata(new_book)
        
        # التحقق من فتح الملف
        mock_file.assert_called()
        
        # التحقق من حفظ البيانات المحدثة
        mock_json_dump.assert_called_once()
        # الحصول على البيانات المحدثة المرسلة إلى json.dump
        args, _ = mock_json_dump.call_args
        updated_books = args[0]
        assert len(updated_books) == 1
        assert updated_books[0]["id"] == "test123"

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('os.path.exists', return_value=True)
    @patch('json.load')
    @patch('fitz.open')
    @patch('builtins.print')
    def test_process_pdf(self, mock_print, mock_fitz_open, mock_json_load, mock_path_exists, mock_file, pdf_loader):
        """اختبار معالجة ملف PDF وتقسيمه إلى قطع"""
        # تجهيز بيانات كتب مزيفة
        mock_books = [{
            "id": "book123",
            "title": "عنوان الكتاب",
            "author": "اسم المؤلف",
            "path": "/path/to/book.pdf",
            "category": "تفسير"
        }]
        mock_json_load.return_value = mock_books
        
        # تجهيز المستندات المزيفة
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 3  # ثلاث صفحات للاختبار
        
        # تجهيز صفحات مزيفة بأحجام مختلفة
        page_texts = [
            "محتوى الصفحة الأولى " * 50,  # نص طويل
            "محتوى الصفحة الثانية " * 50,  # نص طويل
            "محتوى الصفحة الثالثة " * 10   # نص قصير
        ]
        
        # إعداد سلوك get_text للصفحات
        mock_pages = []
        for text in page_texts:
            mock_page = MagicMock()
            mock_page.get_text.return_value = text
            mock_pages.append(mock_page)
        
        # تعيين سلوك __getitem__ للحصول على الصفحات
        mock_doc.__getitem__.side_effect = lambda i: mock_pages[i]
        
        # تعيين المستند المزيف كقيمة إرجاع لـ fitz.open
        mock_fitz_open.return_value = mock_doc
        
        # تجهيز _clean_text المزيفة (ترجع النص كما هو)
        with patch.object(pdf_loader, '_clean_text', side_effect=lambda x: x):
            with patch.object(pdf_loader, '_save_chunks') as mock_save_chunks:
                # اختبار معالجة PDF
                chunks = pdf_loader.process_pdf("book123", chunk_size=1000, overlap=100)
                
                # التحقق من عدد القطع (يجب أن يكون على الأقل 2 بسبب حجم النصوص)
                assert len(chunks) > 0
                
                # التحقق من محتوى القطع
                for chunk in chunks:
                    assert chunk["book_id"] == "book123"
                    assert "text" in chunk
                    assert "pages" in chunk
                    assert chunk["metadata"]["title"] == "عنوان الكتاب"
                    assert chunk["metadata"]["author"] == "اسم المؤلف"
                    assert chunk["metadata"]["category"] == "تفسير"
                
                # التحقق من حفظ القطع
                mock_save_chunks.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('os.path.exists', return_value=True)
    @patch('json.load')
    @patch('builtins.print')
    def test_process_pdf_book_not_found(self, mock_print, mock_json_load, mock_path_exists, mock_file, pdf_loader):
        """اختبار معالجة ملف PDF غير موجود في قاعدة البيانات"""
        # تجهيز بيانات كتب مزيفة (لا تحتوي على الكتاب المطلوب)
        mock_books = [{
            "id": "other_book",
            "title": "كتاب آخر",
            "path": "/path/to/other.pdf"
        }]
        mock_json_load.return_value = mock_books
        
        # اختبار معالجة كتاب غير موجود
        chunks = pdf_loader.process_pdf("nonexistent_book")
        
        # التحقق من أن النتيجة فارغة
        assert chunks == []
        
        # التحقق من طباعة الخطأ
        mock_print.assert_called_once()
        assert "ValueError" in str(mock_print.call_args)

    def test_extract_title(self, pdf_loader):
        """اختبار استخراج عنوان الكتاب من النص"""
        # نص يحتوي على عناوين بتنسيقات مختلفة
        text_with_title = """
        بسم الله الرحمن الرحيم
        
        كتاب: تفسير القرآن الكريم
        
        المؤلف: الشيخ محمد
        
        المقدمة
        """
        
        # استدعاء الدالة المختبرة
        title = pdf_loader._extract_title(text_with_title)
        
        # التحقق من النتيجة
        assert title is not None
        assert "تفسير القرآن" in title

    def test_extract_author(self, pdf_loader):
        """اختبار استخراج اسم المؤلف من النص"""
        # نص يحتوي على أسماء مؤلفين بتنسيقات مختلفة
        text_with_author = """
        بسم الله الرحمن الرحيم
        
        كتاب: تفسير القرآن الكريم
        
        تأليف: الإمام ابن كثير
        
        المقدمة
        """
        
        # استدعاء الدالة المختبرة
        author = pdf_loader._extract_author(text_with_author)
        
        # التحقق من النتيجة
        assert author is not None
        assert "ابن كثير" in author

    def test_clean_text(self, pdf_loader):
        """اختبار تنظيف النص المستخرج من PDF"""
        # نص يحتوي على أخطاء شائعة في ملفات PDF
        dirty_text = """
        بسم الله الرحمن الرحيم
        
        تف سير   القرآن    الكريم
        
        صفحة 1
        
        الحمد لله                      رب العالمين
        
        - - - - - -
        """
        
        # استدعاء الدالة المختبرة
        clean_text = pdf_loader._clean_text(dirty_text)
        
        # التحقق من النتيجة
        assert clean_text is not None
        assert "  " not in clean_text  # لا توجد مسافات متعددة
        assert "تف سير" not in clean_text  # تم دمج الكلمات المقسمة
        assert "-" not in clean_text  # تمت إزالة الرموز الزائدة

    @patch('hashlib.md5')
    def test_compute_file_hash(self, mock_md5, pdf_loader):
        """اختبار حساب التشفير التجزيئي للملف"""
        # تجهيز دالة md5 المزيفة
        mock_hash = MagicMock()
        mock_hash.hexdigest.return_value = "abc123hash"
        mock_md5.return_value = mock_hash
        
        # إنشاء ملف مؤقت للاختبار
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"test content")
            temp_file.flush()
            
            # استدعاء الدالة المختبرة
            file_hash = pdf_loader._compute_file_hash(temp_file.name)
            
            # التحقق من النتيجة
            assert file_hash == "abc123hash"


if __name__ == "__main__":
    pytest.main(["-v", "test_pdf_loader.py"])
