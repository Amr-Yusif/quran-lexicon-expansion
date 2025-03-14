# هيكل المشروع المحدث

## المكونات الرئيسية

```
project_root/
├── agents/                     # نظام الوكلاء المتعددين
│   ├── base/                  # الفئات الأساسية للوكلاء
│   ├── specialized/           # الوكلاء المتخصصون
│   │   ├── tafseer/          # وكيل التفسير
│   │   ├── fiqh/             # وكيل الفقه
│   │   ├── psychology/       # وكيل علم النفس والتربية
│   │   ├── science/          # وكيل الإعجاز العلمي
│   │   └── history/          # وكيل التاريخ والسياق
│   ├── coordinator/          # منسق الوكلاء
│   └── cache/               # نظام التخزين المؤقت للوكلاء
│
├── learning/                  # نظام التعلم النشط
│   ├── feedback/            # نظام التغذية الراجعة
│   ├── hypothesis/          # توليد وتقييم الفرضيات
│   └── patterns/           # اكتشاف الأنماط
│
├── analysis/                  # أنظمة التحليل المتخصصة
│   ├── contradictions/      # تحليل التناقضات الظاهرية
│   ├── schools/            # مقارنة المدارس الفكرية
│   └── concepts/           # الخرائط المفاهيمية
│
├── core/                      # المكونات الأساسية
│   ├── search/             # نظام البحث الدلالي
│   ├── processing/         # معالجة النصوص
│   └── storage/           # إدارة التخزين
│
├── utils/                     # أدوات مساعدة
│   ├── caching/           # إدارة التخزين المؤقت
│   ├── performance/       # أدوات تحسين الأداء
│   └── monitoring/       # مراقبة الأداء
│
├── api/                       # واجهات برمجة التطبيق
│   ├── rest/              # واجهات REST
│   └── graphql/          # واجهات GraphQL
│
├── ui/                        # واجهة المستخدم
│   ├── web/               # واجهة الويب
│   └── components/       # مكونات واجهة المستخدم
│
├── tests/                     # اختبارات
│   ├── unit/              # اختبارات الوحدات
│   ├── integration/      # اختبارات التكامل
│   └── performance/     # اختبارات الأداء
│
├── docs/                      # التوثيق
│   ├── api/               # توثيق API
│   ├── user_guide/       # دليل المستخدم
│   └── developer_guide/  # دليل المطور
│
└── config/                    # ملفات الإعداد
    ├── agents/            # إعدادات الوكلاء
    ├── performance/      # إعدادات الأداء
    └── system/           # إعدادات النظام
```

## تفاصيل المكونات الجديدة

### 1. نظام الوكلاء المتعددين (`agents/`)
- `base/`: الفئات الأساسية والواجهات للوكلاء
- `specialized/`: تنفيذات الوكلاء المتخصصين
- `coordinator/`: منسق الوكلاء ومدير التفاعلات
- `cache/`: نظام التخزين المؤقت للوكلاء

### 2. نظام التعلم النشط (`learning/`)
- `feedback/`: جمع وتحليل التغذية الراجعة
- `hypothesis/`: توليد وتقييم الفرضيات
- `patterns/`: اكتشاف وتحليل الأنماط

### 3. أنظمة التحليل المتخصصة (`analysis/`)
- `contradictions/`: تحليل وحل التناقضات الظاهرية
- `schools/`: مقارنة وتحليل المدارس الفكرية
- `concepts/`: إدارة الخرائط المفاهيمية

### 4. تحسينات الأداء (`utils/performance/`)
- نظام إدارة الذاكرة
- المعالجة المتوازية
- تحسين التخزين والشبكة

## ملفات التكوين الرئيسية

### 1. إعدادات الوكلاء (`config/agents/`)
```yaml
agents:
  tafseer:
    cache_size: 100MB
    max_concurrent_tasks: 5
  fiqh:
    cache_size: 150MB
    max_concurrent_tasks: 3
  coordinator:
    max_agents: 10
    coordination_interval: 1s
```

### 2. إعدادات الأداء (`config/performance/`)
```yaml
memory:
  max_usage: 2GB
  cleanup_threshold: 80%
  cache_size: 500MB

processing:
  max_threads: 4
  batch_size: 100
  timeout: 30s

storage:
  compression: true
  max_disk_usage: 10GB
  cleanup_interval: 24h
```

### 3. إعدادات النظام (`config/system/`)
```yaml
api:
  max_requests: 100/s
  timeout: 10s

monitoring:
  enabled: true
  interval: 5s
  alerts:
    memory_threshold: 90%
    cpu_threshold: 80%
```

## التبعيات الرئيسية

```python
# requirements.txt
numpy==1.21.0
pandas==1.3.0
networkx==2.6.0
spacy==3.1.0
camel-tools==1.0.0
pytorch==1.9.0
transformers==4.9.0
fastapi==0.68.0
pydantic==1.8.2
```

## استراتيجيات تحسين الأداء

### 1. التخزين المؤقت
- تخزين مؤقت متعدد المستويات
- تخزين مؤقت للوكلاء
- تخزين مؤقت للنتائج المتكررة

### 2. المعالجة المتوازية
- معالجة متوازية للوكلاء المستقلين
- تجميع النتائج بكفاءة
- إدارة الموارد الديناميكية

### 3. إدارة الذاكرة
- تنظيف الذاكرة التلقائي
- تحميل البيانات عند الطلب
- ضغط البيانات غير المستخدمة 