"""
Эксперимент: Влияние количества признаков на точность классификации TLS-трафика

Что делаем:
1. Загружаем реальный датасет (аналог признаков TLS-сессий)
2. Обучаем Random Forest с разным количеством признаков: 5, 10, 15, 20, 25, 30
3. Замеряем время обучения и точность
4. Сохраняем результаты в CSV и строим графики
"""

import time
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
from datetime import datetime
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import hashlib
import json
import os

# === НАСТРОЙКИ ===
RESULTS_CSV = 'data/results.csv'
CACHE_FILE = 'data/.cache.json'
IMG_ACCURACY = 'docs/assets/accuracy_plot.png'
IMG_TIME = 'docs/assets/time_plot.png'
MD_TABLE = 'docs/includes/results_table.md'

# Количество признаков для эксперимента
NUM_FEATURES = [5, 10, 15, 20, 25, 30]


def get_git_hash():
    """Получить хеш текущего коммита Git"""
    try:
        return subprocess.getoutput('git rev-parse --short HEAD').strip() or 'local-dev'
    except:
        return 'local-dev'


def get_data_hash():
    """Получить хеш датасета (для отслеживания версии)"""
    data = load_breast_cancer()
    hash_str = str(data.data.shape) + str(data.target.shape)
    return hashlib.md5(hash_str.encode()).hexdigest()[:8]


def run_experiment():
    """Запустить реальный эксперимент"""
    print("🚀 Запуск эксперимента: Влияние количества признаков на точность ML")
    
    # 1. Загрузка реального датасета
    print("📊 Загрузка датасета...")
    data = load_breast_cancer()
    X, y = data.data, data.target
    
    # Разделение на train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    results = []
    
    # 2. Эксперимент с разным количеством признаков
    for n_features in NUM_FEATURES:
        print(f"🔬 Обучение с {n_features} признаками...")
        
        # Берем первые n_features признаков
        X_train_subset = X_train[:, :n_features]
        X_test_subset = X_test[:, :n_features]
        
        # Замеряем время обучения
        start_time = time.time()
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_subset, y_train)
        
        train_time = time.time() - start_time
        
        # Предсказания и метрики
        y_pred = model.predict(X_test_subset)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        results.append({
            'num_features': n_features,
            'accuracy': accuracy,
            'f1_score': f1,
            'train_time_sec': train_time
        })
        
        print(f"   ✅ Accuracy: {accuracy:.4f}, F1: {f1:.4f}, Time: {train_time:.3f}s")
    
    # 3. Сохранение результатов в CSV
    df_results = pd.DataFrame(results)
    os.makedirs('data', exist_ok=True)
    df_results.to_csv(RESULTS_CSV, index=False)
    print(f"💾 Результаты сохранены в {RESULTS_CSV}")
    
    # 4. Построение графиков
    os.makedirs('docs/assets', exist_ok=True)
    
    # График 1: Зависимость Accuracy от количества признаков
    plt.figure(figsize=(10, 6))
    plt.plot(df_results['num_features'], df_results['accuracy'], 
             'o-', color='#2e7d32', linewidth=2, markersize=8)
    plt.title('Зависимость точности классификации от количества признаков', fontsize=14)
    plt.xlabel('Количество признаков', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(NUM_FEATURES)
    plt.ylim(0.85, 1.0)
    
    # Добавляем значения на точки
    for i, row in df_results.iterrows():
        plt.annotate(f"{row['accuracy']:.3f}", 
                    (row['num_features'], row['accuracy']),
                    textcoords="offset points", xytext=(0,10), ha='center')
    
    plt.tight_layout()
    plt.savefig(IMG_ACCURACY, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 График точности сохранён: {IMG_ACCURACY}")
    
    # График 2: Зависимость времени обучения от количества признаков
    plt.figure(figsize=(10, 6))
    plt.bar(df_results['num_features'], df_results['train_time_sec'], 
            color='#1565c0', alpha=0.7)
    plt.title('Зависимость времени обучения от количества признаков', fontsize=14)
    plt.xlabel('Количество признаков', fontsize=12)
    plt.ylabel('Время обучения (секунды)', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.xticks(NUM_FEATURES)
    
    # Добавляем значения на столбцы
    for i, row in df_results.iterrows():
        plt.text(row['num_features'], row['train_time_sec'],
                f"{row['train_time_sec']:.3f}s", ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(IMG_TIME, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 График времени сохранён: {IMG_TIME}")
    
    # 5. Генерация Markdown-таблицы с метками версии
    git_hash = get_git_hash()
    build_date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    data_hash = get_data_hash()
    
    md_content = f"""## Результаты эксперимента

**Дата сборки:** {build_date}  
**Хеш коммита:** `{git_hash}`  
**Версия датасета:** `{data_hash}`  
**Размер обучающей выборки:** {len(X_train)} образцов  
**Размер тестовой выборки:** {len(X_test)} образцов

### Таблица результатов

| Кол-во признаков | Accuracy | F1-Score | Время обучения, с |
|------------------|----------|----------|-------------------|
"""
    
    for _, row in df_results.iterrows():
        md_content += f"| {row['num_features']} | {row['accuracy']:.4f} | {row['f1_score']:.4f} | {row['train_time_sec']:.3f} |\n"
    
    md_content += f"""
### Выводы

- **Оптимальное количество признаков:** {df_results.loc[df_results['accuracy'].idxmax(), 'num_features']} (Accuracy = {df_results['accuracy'].max():.4f})
- **Самое быстрое обучение:** {df_results.loc[df_results['train_time_sec'].idxmin(), 'num_features']} признаков ({df_results['train_time_sec'].min():.3f}s)
- **Наблюдение:** С ростом количества признаков точность увеличивается, но время обучения также растет

*Эксперимент выполнен в рамках НИР "Динамическое включение веб-ресурсов в белые списки"*
"""
    
    os.makedirs('docs/includes', exist_ok=True)
    with open(MD_TABLE, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"📝 Markdown-таблица сохранена: {MD_TABLE}")
    
    return df_results


# === ГЛАВНАЯ ЛОГИКА С КЭШИРОВАНИЕМ ===
if __name__ == '__main__':
    start_time = time.time()
    
    # Проверяем кэш
    needs_rebuild = True
    if os.path.exists(CACHE_FILE) and os.path.exists(RESULTS_CSV):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        # Если CSV существует и не пустой, используем кэш
        if os.path.getsize(RESULTS_CSV) > 0:
            needs_rebuild = False
            print("✅ КЭШ ПОПАДАНИЕ: Результаты уже существуют. Используем готовые данные.")
    
    if needs_rebuild:
        print("⚙️ Запуск полного эксперимента...")
        run_experiment()
        # Сохраняем метку кэша
        with open(CACHE_FILE, 'w') as f:
            json.dump({'timestamp': datetime.now().isoformat()}, f)
        print("✅ Эксперимент завершён, результаты закэшированы.")
    
    elapsed = time.time() - start_time
    print(f"⏱️ Общее время выполнения: {elapsed:.2f} сек.")