# تصميم لوحات التحكم باستخدام Python/Streamlit

## 1. الواجهة الرئيسية (Main Dashboard)

### 1.1 هيكل الواجهة
```python
# main_dashboard.py
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List

class MainDashboard:
    def __init__(self):
        self.agent_controller = AgentController()
        self.resource_manager = ResourceManager()
    
    def render(self):
        st.set_page_config(page_title="نظام تحليل النصوص القرآنية", layout="wide")
        
        # الشريط الجانبي للتحكم العام
        with st.sidebar:
            self.render_system_controls()
        
        # تقسيم الشاشة الرئيسية
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.render_main_content()
        
        with col2:
            self.render_performance_metrics()
    
    def render_system_controls(self):
        st.header("التحكم في النظام")
        
        # زر تشغيل/إيقاف النظام
        system_running = st.toggle("تشغيل النظام", value=True)
        
        # التحكم في الموارد
        st.subheader("إدارة الموارد")
        max_memory = st.slider("الحد الأقصى للذاكرة (GB)", 1, 16, 4)
        max_cpu = st.slider("الحد الأقصى للمعالج (%)", 10, 100, 50)
        
        if st.button("تطبيق الإعدادات"):
            self.resource_manager.update_limits(max_memory, max_cpu)
```

### 1.2 عرض الأداء والمراقبة
```python
def render_performance_metrics(self):
    st.header("مؤشرات الأداء")
    
    # عرض استخدام الموارد
    metrics = self.resource_manager.get_current_metrics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("استخدام المعالج", f"{metrics['cpu_usage']}%",
                 delta=f"{metrics['cpu_change']}%")
    with col2:
        st.metric("استخدام الذاكرة", f"{metrics['memory_usage']}GB",
                 delta=f"{metrics['memory_change']}GB")
    with col3:
        st.metric("عدد العمليات", metrics['active_tasks'],
                 delta=metrics['tasks_change'])
    
    # رسم بياني للأداء
    fig = go.Figure()
    fig.add_trace(go.Line(x=metrics['timestamps'], 
                         y=metrics['response_times'],
                         name="زمن الاستجابة"))
    st.plotly_chart(fig)
```

## 2. واجهة التحكم في الوكلاء (Agent Control)

### 2.1 إدارة الوكلاء
```python
class AgentDashboard:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.agent = self.agent_controller.get_agent(agent_type)
    
    def render(self):
        st.header(f"إدارة وكيل {self.agent_type}")
        
        # حالة الوكيل
        status = self.agent.get_status()
        st.info(f"الحالة: {status['state']}")
        
        # إعدادات الوكيل
        st.subheader("إعدادات الوكيل")
        settings = self.agent.get_settings()
        
        new_settings = {}
        for key, value in settings.items():
            if isinstance(value, bool):
                new_settings[key] = st.checkbox(key, value)
            elif isinstance(value, (int, float)):
                new_settings[key] = st.number_input(key, value=value)
            else:
                new_settings[key] = st.text_input(key, value)
        
        if st.button("حفظ الإعدادات"):
            self.agent.update_settings(new_settings)
```

### 2.2 اختبار الوكيل
```python
def render_testing_interface(self):
    st.subheader("اختبار الوكيل")
    
    # إدخال نص للتحليل
    test_text = st.text_area("أدخل النص للتحليل")
    
    if st.button("تحليل"):
        with st.spinner("جاري التحليل..."):
            results = self.agent.analyze(test_text)
            
            # عرض النتائج
            st.json(results)
            
            # عرض المقاييس
            st.metric("زمن التحليل", f"{results['time']}ms")
            st.metric("درجة الثقة", f"{results['confidence']}%")
```

## 3. واجهة التعلم والتدريب (Learning Interface)

### 3.1 مراقبة التعلم
```python
class LearningDashboard:
    def render_learning_metrics(self):
        st.header("مؤشرات التعلم")
        
        # عرض منحنى التعلم
        learning_data = self.get_learning_metrics()
        fig = go.Figure()
        fig.add_trace(go.Line(x=learning_data['epochs'],
                            y=learning_data['accuracy'],
                            name="دقة التعلم"))
        st.plotly_chart(fig)
        
        # عرض الإحصائيات
        st.metric("عدد الأمثلة المتعلم منها", learning_data['examples_count'])
        st.metric("متوسط دقة التعلم", f"{learning_data['avg_accuracy']}%")
```

### 3.2 التدريب اليدوي
```python
def render_manual_training(self):
    st.subheader("التدريب اليدوي")
    
    # إدخال بيانات التدريب
    input_text = st.text_area("النص المدخل")
    expected_output = st.text_area("النتيجة المتوقعة")
    
    if st.button("تدريب"):
        with st.spinner("جاري التدريب..."):
            result = self.agent.train(input_text, expected_output)
            st.success(f"تم التدريب بنجاح! الدقة: {result['accuracy']}%")
```

## 4. التكامل مع النظام

### 4.1 إدارة الجلسات
```python
class SessionManager:
    def __init__(self):
        if 'active_agents' not in st.session_state:
            st.session_state.active_agents = set()
            
    def activate_agent(self, agent_type: str):
        st.session_state.active_agents.add(agent_type)
        
    def deactivate_agent(self, agent_type: str):
        st.session_state.active_agents.remove(agent_type)
```

### 4.2 إدارة الحالة
```python
class StateManager:
    def save_state(self):
        # حفظ حالة النظام
        state = {
            'agents': self.get_agents_state(),
            'resources': self.get_resources_state(),
            'learning': self.get_learning_state()
        }
        return state
    
    def load_state(self, state: Dict):
        # استعادة حالة النظام
        self.restore_agents_state(state['agents'])
        self.restore_resources_state(state['resources'])
        self.restore_learning_state(state['learning'])
```

## 5. تنسيقات وأنماط الواجهة

### 5.1 التنسيقات العامة
```python
def apply_styling():
    st.markdown("""
        <style>
        .main {
            font-family: 'Cairo', sans-serif;
            direction: rtl;
        }
        .stButton button {
            background-color: #2c3e50;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
```

### 5.2 مكونات مخصصة
```python
def custom_metric_card(label: str, value: str, delta: str = None):
    st.markdown(f"""
        <div class="metric-card">
            <h3>{label}</h3>
            <h2>{value}</h2>
            {f'<p class="delta">{delta}</p>' if delta else ''}
        </div>
    """, unsafe_allow_html=True)
```

## 6. التنفيذ والتشغيل

### 6.1 تشغيل التطبيق
```python
def main():
    # تطبيق التنسيقات
    apply_styling()
    
    # تهيئة مديري الحالة والجلسات
    session_manager = SessionManager()
    state_manager = StateManager()
    
    # تهيئة الداشبورد الرئيسي
    main_dashboard = MainDashboard()
    
    # عرض الواجهة
    main_dashboard.render()

if __name__ == "__main__":
    main()
```

### 6.2 تشغيل الخدمة
```bash
# تشغيل الواجهة
streamlit run main_dashboard.py --server.port 8501
``` 