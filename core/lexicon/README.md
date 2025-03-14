# وحدة المعجم القرآني (Quranic Lexicon)

## نظرة عامة

وحدة المعجم القرآني هي نواة النظام الجديد لمعالجة النصوص العربية، وتوفر واجهة برمجية للوصول إلى قاعدة بيانات معجمية مدققة يدوياً للقرآن الكريم. تعتمد الوحدة على مبدأ الدقة المطلقة (100%) في معالجة النصوص القرآنية من خلال استخدام قاعدة بيانات معجمية مدققة من متخصصين معتمدين.

## المكونات الرئيسية

### 1. فئة `QuranicLexicon`

الفئة الرئيسية التي توفر واجهة للوصول إلى بيانات الكلمات القرآنية واستخراج معلوماتها اللغوية مثل الجذر، النوع، الوزن الصرفي، والمعنى.

#### الطرق الرئيسية:

- `get_root(word)`: استخراج جذر الكلمة من المعجم.
- `get_word_type(word)`: تحديد نوع الكلمة (اسم، فعل، حرف، ...).
- `get_pattern(word)`: استخراج الوزن الصرفي للكلمة.
- `get_all_info(word)`: الحصول على جميع معلومات الكلمة.
- `search_by_root(root)`: البحث عن الكلمات التي تنتمي إلى جذر معين.
- `verify_word_root(word, expected_root)`: التحقق من صحة جذر كلمة.
- `add_word(word, info)`: إضافة كلمة جديدة إلى المعجم.
- `save(file_path)`: حفظ بيانات المعجم إلى ملف.

### 2. فئة `HybridProcessor`

فئة معالجة هجينة تجمع بين قاعدة البيانات المعجمية والخوارزميات لتحقيق أعلى دقة ممكنة في معالجة النصوص العربية.

#### الطرق الرئيسية:

- `extract_root(word)`: استخراج جذر الكلمة باستخدام النظام الهجين.
- `get_word_type(word)`: تحديد نوع الكلمة باستخدام النظام الهجين.
- `get_pattern(word)`: استخراج الوزن الصرفي باستخدام النظام الهجين.
- `process_word(word)`: معالجة كلمة كاملة واستخراج جميع المعلومات المتاحة عنها.
- `verify_extraction(word, expected_root)`: التحقق من صحة استخراج جذر كلمة.
- `expand_lexicon(words)`: محاولة إثراء المعجم باستخدام الخوارزميات.

## هيكل البيانات

يستخدم المعجم القرآني بنية بيانات على شكل قاموس JSON، حيث تكون الكلمات هي المفاتيح، والقيم هي قواميس تحتوي على معلومات مثل:

```json
{
  "الرحمن": {
    "root": "رحم",
    "type": "noun",
    "pattern": "فَعْلان",
    "meaning": "ذو الرحمة الواسعة التي وسعت كل شيء",
    "source": "تفسير ابن كثير"
  }
}
```

## كيفية الاستخدام

### استخدام المعجم القرآني مباشرة:

```python
from core.lexicon.quranic_lexicon import QuranicLexicon
from pathlib import Path

# تهيئة المعجم
lexicon_path = Path("data/quran_lexicon_sample.json")
lexicon = QuranicLexicon(data_path=lexicon_path)

# استخراج جذر كلمة
root = lexicon.get_root("الرحمن")  # النتيجة: "رحم"

# الحصول على معلومات كلمة
info = lexicon.get_all_info("الرحمن")
print(info["type"])  # النتيجة: "noun"
print(info["pattern"])  # النتيجة: "فَعْلان"

# البحث عن كلمات بجذر معين
words = lexicon.search_by_root("رحم")  # النتيجة: ["الرحمن", "الرحيم"]
```

### استخدام المعالج الهجين:

```python
from core.lexicon.hybrid_processor import HybridProcessor
from pathlib import Path

# تهيئة المعالج الهجين
lexicon_path = Path("data/quran_lexicon_sample.json")
processor = HybridProcessor(lexicon_path=lexicon_path)

# معالجة كلمة واستخراج معلوماتها
result = processor.process_word("الرحمن")
print(result["root"]["value"])  # النتيجة: "رحم"
print(result["root"]["confidence"])  # النتيجة: 1.0 (درجة الثقة)
print(result["root"]["source"])  # النتيجة: "lexicon" (مصدر المعلومة)

# التحقق من صحة استخراج جذر
verification = processor.verify_extraction("الرحمن", "رحم")
print(verification["is_correct"])  # النتيجة: True
```

## الأمثلة

يمكن الاطلاع على أمثلة كاملة في المجلد `examples/`:

- `lexicon_example.py`: مثال لاستخدام المعجم القرآني.
- `hybrid_processor_example.py`: مثال لاستخدام المعالج الهجين.

## المساهمة في تطوير المعجم

### إضافة كلمات جديدة إلى المعجم:

1. استخدام طريقة `add_word` لإضافة كلمة جديدة مع معلوماتها.
2. استخدام طريقة `save` لحفظ التغييرات إلى ملف.

### توسيع قاعدة البيانات المعجمية:

1. جمع البيانات من مصادر موثوقة (تفاسير القرآن، معاجم اللغة العربية، ...).
2. تدقيق البيانات ومراجعتها.
3. إضافة البيانات إلى ملف JSON بالصيغة المناسبة.
4. توثيق مصادر البيانات. 