"""
مكونات الرسوم البيانية - للعرض المرئي للمعلومات والإحصائيات
"""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import altair as alt
import plotly.express as px

def create_category_chart(data: Dict[str, int], title: str = "توزيع حسب الفئة", 
                         x_label: str = "الفئة", y_label: str = "العدد") -> plt.Figure:
    """
    إنشاء رسم بياني للفئات

    Args:
        data: البيانات (قاموس بمفاتيح الفئات وقيم العدد)
        title: عنوان الرسم البياني
        x_label: تسمية محور x
        y_label: تسمية محور y

    Returns:
        رسم بياني matplotlib
    """
    # إنشاء الرسم البياني
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # ترتيب البيانات
    keys = list(data.keys())
    values = [data[k] for k in keys]
    
    # إنشاء الرسم البياني
    bars = ax.bar(keys, values)
    
    # تغيير اتجاه الكتابة للدعم العربي
    plt.rcParams['axes.unicode_minus'] = False
    
    # إضافة عناوين
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    
    # تدوير التسميات إذا لزم الأمر
    plt.xticks(rotation=45, ha="right")
    
    # ضبط التخطيط
    plt.tight_layout()
    
    return fig

def create_timeline_chart(data: List[Dict[str, Any]], date_field: str = "created_at", 
                         value_field: str = "value", title: str = "تطور عبر الزمن") -> alt.Chart:
    """
    إنشاء رسم بياني زمني باستخدام Altair

    Args:
        data: البيانات (قائمة من القواميس)
        date_field: حقل التاريخ
        value_field: حقل القيمة
        title: عنوان الرسم البياني

    Returns:
        رسم بياني Altair
    """
    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(data)
    
    # تحويل حقل التاريخ إذا لزم الأمر
    if date_field in df.columns:
        df[date_field] = pd.to_datetime(df[date_field])
    
    # إنشاء الرسم البياني
    chart = alt.Chart(df).mark_line().encode(
        x=alt.X(f"{date_field}:T", title="التاريخ"),
        y=alt.Y(f"{value_field}:Q", title="القيمة"),
        tooltip=[alt.Tooltip(f"{date_field}:T", title="التاريخ"),
                alt.Tooltip(f"{value_field}:Q", title="القيمة")]
    ).properties(
        title=title,
        width=600,
        height=400
    )
    
    return chart

def create_pie_chart(data: Dict[str, int], title: str = "توزيع النسب") -> plt.Figure:
    """
    إنشاء رسم بياني دائري

    Args:
        data: البيانات (قاموس بمفاتيح الفئات وقيم العدد)
        title: عنوان الرسم البياني

    Returns:
        رسم بياني matplotlib
    """
    # إنشاء الرسم البياني
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # استخراج البيانات
    labels = list(data.keys())
    values = [data[k] for k in labels]
    
    # إنشاء الرسم البياني الدائري
    wedges, texts, autotexts = ax.pie(
        values, 
        autopct='%1.1f%%',
        textprops={'color': "w", 'weight': 'bold', 'fontsize': 12},
        startangle=90
    )
    
    # إضافة وسم
    ax.legend(
        wedges, 
        labels,
        title="الفئات",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )
    
    # إضافة عنوان
    ax.set_title(title)
    
    # ضبط التخطيط
    plt.tight_layout()
    
    return fig

def create_heatmap(data: List[List[float]], row_labels: List[str], col_labels: List[str],
                 title: str = "خريطة حرارية") -> plt.Figure:
    """
    إنشاء خريطة حرارية

    Args:
        data: مصفوفة البيانات
        row_labels: تسميات الصفوف
        col_labels: تسميات الأعمدة
        title: عنوان الرسم البياني

    Returns:
        رسم بياني matplotlib
    """
    # إنشاء الرسم البياني
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # إنشاء الخريطة الحرارية
    im = ax.imshow(data, cmap="YlOrRd")
    
    # إضافة شريط الألوان
    cbar = ax.figure.colorbar(im, ax=ax)
    
    # ضبط تسميات المحاور
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)
    
    # تدوير تسميات المحور السيني
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # إضافة عنوان
    ax.set_title(title)
    
    # ضبط التخطيط
    plt.tight_layout()
    
    return fig

def create_word_cloud(text_data: List[str], title: str = "سحابة الكلمات", 
                    background_color: str = "white") -> plt.Figure:
    """
    إنشاء سحابة كلمات للنصوص

    Args:
        text_data: قائمة من النصوص
        title: عنوان الرسم البياني
        background_color: لون الخلفية

    Returns:
        رسم بياني matplotlib
    """
    # تحقق من وجود مكتبة wordcloud
    try:
        from wordcloud import WordCloud
        from bidi.algorithm import get_display
        import arabic_reshaper
    except ImportError:
        # إذا كانت المكتبة غير مثبتة، أعد رسمًا بيانيًا بديلًا
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "مكتبة WordCloud غير مثبتة. استخدم 'pip install wordcloud arabic-reshaper python-bidi'",
               ha="center", va="center")
        return fig
    
    # دمج النصوص
    all_text = " ".join(text_data)
    
    # معالجة النص العربي
    reshaped_text = arabic_reshaper.reshape(all_text)
    bidi_text = get_display(reshaped_text)
    
    # إنشاء سحابة الكلمات
    wordcloud = WordCloud(width=800, height=400, background_color=background_color,
                         font_path="arial.ttf").generate(bidi_text)
    
    # إنشاء الرسم البياني
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title)
    
    return fig

def create_interactive_chart(data: List[Dict[str, Any]], x_field: str, y_field: str,
                          color_field: Optional[str] = None, title: str = "رسم بياني تفاعلي") -> px.Figure:
    """
    إنشاء رسم بياني تفاعلي باستخدام Plotly Express

    Args:
        data: البيانات (قائمة من القواميس)
        x_field: حقل محور x
        y_field: حقل محور y
        color_field: حقل لون النقاط (اختياري)
        title: عنوان الرسم البياني

    Returns:
        رسم بياني Plotly Express
    """
    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(data)
    
    # إنشاء الرسم البياني
    if color_field and color_field in df.columns:
        fig = px.scatter(df, x=x_field, y=y_field, color=color_field, 
                        title=title, hover_data=df.columns)
    else:
        fig = px.scatter(df, x=x_field, y=y_field, 
                        title=title, hover_data=df.columns)
    
    # تحديث التخطيط
    fig.update_layout(
        title_x=0.5,
        xaxis_title=x_field,
        yaxis_title=y_field,
        legend_title=color_field if color_field else ""
    )
    
    return fig
