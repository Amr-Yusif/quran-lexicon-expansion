# نظام المعجم القرآني الموسع (Quran Lexicon Expansion System)

<div dir="rtl">

## نظرة عامة

نظام المعجم القرآني الموسع هو منصة متقدمة للذكاء الاصطناعي مصممة لتوسيع وتحليل المعجم القرآني باستخدام تقنيات التعلم الآلي والمعالجة اللغوية المتقدمة. يهدف المشروع إلى بناء معجم شامل للكلمات القرآنية يتضمن معلومات مفصلة عن الجذور، والأنماط، والأنواع، والمعاني، والعلاقات الدلالية.

## المميزات الرئيسية

### 1. توسيع المعجم

- **الاستخراج التلقائي**: استخراج الكلمات من القرآن الكريم والمصادر الإسلامية.
- **التصنيف الذكي**: تصنيف الكلمات حسب الجذور والأنماط الصرفية.
- **التوسع المستمر**: هدف الوصول إلى 5000 كلمة مع توصيفها اللغوي الكامل.

### 2. التحليل اللغوي المتقدم

- **استخراج الجذور**: خوارزميات متقدمة لاستخراج جذور الكلمات العربية.
- **التحليل الصرفي**: تحديد الصيغ والأوزان الصرفية للكلمات.
- **التحليل الدلالي**: فهم المعاني والعلاقات بين الكلمات.

### 3. الحقول الدلالية وشبكات المترادفات

- **بناء الحقول الدلالية**: تنظيم الكلمات في حقول دلالية متخصصة.
- **شبكات المترادفات**: إنشاء شبكات للمترادفات والمتضادات.
- **تتبع العلاقات الدلالية**: تحديد العلاقات المعنوية بين الكلمات.

### 4. تطبيقات التعلم الآلي

- **نماذج استخراج الجذور**: نماذج تعلم آلي متخصصة لاستخراج الجذور.
- **تحليل الصرف**: خوارزميات التعلم العميق لتحليل الصرف العربي.
- **التعرف على الأنماط**: نماذج للتعرف على الأنماط اللغوية.

### 5. أدوات التدقيق والتقييم

- **تدقيق المعجم**: أدوات للتدقيق والتحقق من صحة المعلومات.
- **تقييم الأداء**: نظام تقييم شامل لقياس دقة الخوارزميات.
- **تقارير مفصلة**: إنشاء تقارير تفصيلية عن عملية التوسيع والتحسين.

## المتطلبات الأساسية

- Python 3.8+
- المكتبات اللازمة موجودة في ملف `requirements.txt`
- وصول إلى الإنترنت (للتثبيت الأولي)

## التثبيت

### 1. استنساخ المشروع

```bash
git clone https://github.com/Amr-Yusif/quran-lexicon-expansion.git
cd quran-lexicon-expansion
```

### 2. إعداد البيئة الافتراضية

```bash
python -m venv venv
source venv/bin/activate  # على Linux/Mac
# أو
venv\Scripts\activate  # على Windows
```

### 3. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 4. إعداد ملف متغيرات البيئة

قم بإنشاء ملف `.env` في المجلد الرئيسي للمشروع:

```
DATA_PATH=data
OUTPUT_PATH=reports
```

## تشغيل النظام

### توسيع المعجم

```bash
python scripts/run_lexicon_expansion.py --target 1000
```

### التدقيق

```bash
python tools/lexicon_audit.py --lexicon_path data/temp_extended_lexicon.json
```

### تحسين الخوارزميات

```bash
python scripts/improve_algorithms.py
```

### إصدار التقارير

```bash
python scripts/generate_stage3_report.py
```

## المنهجية

يتبع المشروع منهجية تطوير متعددة المراحل:

1. **جمع البيانات**: استخراج الكلمات من مصادر متنوعة.
2. **المعالجة الأولية**: تنظيف وتحليل الكلمات المستخرجة.
3. **التصنيف والتوصيف**: تصنيف الكلمات وتوصيفها لغويًا.
4. **التحسين المستمر**: تطوير الخوارزميات وتحسين دقتها.
5. **التدقيق والتقييم**: تدقيق النتائج وتقييم أداء النظام.
6. **التوثيق**: توثيق المعجم وإصدار التقارير.

## المساهمة في المشروع

نرحب بمساهماتكم لتحسين النظام! لمزيد من المعلومات حول كيفية المساهمة، يرجى الاطلاع على ملف CONTRIBUTING.md.

## الترخيص

هذا المشروع مرخص بموجب ترخيص MIT - راجع ملف LICENSE للحصول على التفاصيل.

</div>

---

<div dir="ltr">

# Quran Lexicon Expansion System

## Overview

The Quran Lexicon Expansion System is an advanced AI platform designed to expand and analyze the Quranic lexicon using machine learning and advanced language processing techniques. The project aims to build a comprehensive dictionary of Quranic words that includes detailed information about roots, patterns, types, meanings, and semantic relationships.

## Key Features

### 1. Lexicon Expansion

- **Automatic Extraction**: Extracting words from the Quran and Islamic sources.
- **Intelligent Classification**: Classifying words according to roots and morphological patterns.
- **Continuous Expansion**: Aiming to reach 5000 words with complete linguistic characterization.

### 2. Advanced Linguistic Analysis

- **Root Extraction**: Advanced algorithms for extracting Arabic word roots.
- **Morphological Analysis**: Determining morphological forms and patterns of words.
- **Semantic Analysis**: Understanding meanings and relationships between words.

### 3. Semantic Fields and Synonym Networks

- **Building Semantic Fields**: Organizing words into specialized semantic fields.
- **Synonym Networks**: Creating networks for synonyms and antonyms.
- **Tracking Semantic Relationships**: Identifying meaning relationships between words.

### 4. Machine Learning Applications

- **Root Extraction Models**: Specialized machine learning models for root extraction.
- **Morphological Analysis**: Deep learning algorithms for Arabic morphological analysis.
- **Pattern Recognition**: Models for recognizing linguistic patterns.

### 5. Audit and Evaluation Tools

- **Lexicon Auditing**: Tools for auditing and verifying information accuracy.
- **Performance Evaluation**: Comprehensive evaluation system to measure algorithm accuracy.
- **Detailed Reports**: Creating detailed reports on the expansion and improvement process.

## Prerequisites

- Python 3.8+
- Required libraries in `requirements.txt`
- Internet access (for initial installation)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Amr-Yusif/quran-lexicon-expansion.git
cd quran-lexicon-expansion
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # on Linux/Mac
# or
venv\Scripts\activate  # on Windows
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root directory:

```
DATA_PATH=data
OUTPUT_PATH=reports
```

## Running the System

### Expand the Lexicon

```bash
python scripts/run_lexicon_expansion.py --target 1000
```

### Audit

```bash
python tools/lexicon_audit.py --lexicon_path data/temp_extended_lexicon.json
```

### Improve Algorithms

```bash
python scripts/improve_algorithms.py
```

### Generate Reports

```bash
python scripts/generate_stage3_report.py
```

## Methodology

The project follows a multi-stage development methodology:

1. **Data Collection**: Extracting words from various sources.
2. **Preprocessing**: Cleaning and analyzing extracted words.
3. **Classification and Characterization**: Classifying words and characterizing them linguistically.
4. **Continuous Improvement**: Developing algorithms and improving their accuracy.
5. **Auditing and Evaluation**: Auditing results and evaluating system performance.
6. **Documentation**: Documenting the lexicon and issuing reports.

## Contributing

We welcome your contributions to improve the system! For more information on how to contribute, please see the CONTRIBUTING.md file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

</div>
