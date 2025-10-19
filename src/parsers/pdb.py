import requests
import pandas as pd
import time
import json
import os

def search_pdb_by_sequence_rcsb(sequence, identity_cutoff=0.9, max_results=10):
    """
    Поиск в PDB через официальный RCSB REST API
    
    Args:
        sequence (str): аминокислотная последовательность
        identity_cutoff (float): порог идентичности (0.0-1.0)
        max_results (int): максимальное количество результатов
    
    Returns:
        dict: информация о найденных структурах
    """
    url = "https://search.rcsb.org/rcsbsearch/v2/query"
    
    # Формируем корректный JSON запрос
    query = {
        "query": {
            "type": "terminal",
            "service": "sequence",
            "parameters": {
                "evalue_cutoff": 1,
                "identity_cutoff": identity_cutoff,
                "target": "pdb_protein_sequence",
                "value": sequence
            }
        },
        "request_options": {
            "scoring_strategy": "sequence",
            "paginate": {
                "start": 0,
                "rows": max_results
            }
        },
        "return_type": "polymer_entity"  # Изменено для получения детальной информации
    }
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(url, json=query, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        result_set = data.get('result_set', [])
        
        # Извлекаем детальную информацию о схожести
        detailed_results = []
        for result in result_set:
            if isinstance(result, dict):
                pdb_info = {
                    'identifier': result.get('identifier', ''),
                    'score': result.get('score', 0),
                    'similarity': round(result.get('score', 0) * 100, 2)  # Процент схожести
                }
                detailed_results.append(pdb_info)
        
        # Извлекаем только PDB IDs из результатов
        pdb_ids = [result.get('identifier', '') for result in detailed_results if result.get('identifier')]
        
        return {
            'success': True,
            'found': len(pdb_ids) > 0,
            'count': len(pdb_ids),
            'pdb_ids': pdb_ids,
            'detailed_results': detailed_results,  # Добавлена детальная информация
            'raw_result': result_set,
            'error': None
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'found': False,
            'count': 0,
            'pdb_ids': [],
            'detailed_results': [],
            'raw_result': [],
            'error': f"Request error: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'found': False,
            'count': 0,
            'pdb_ids': [],
            'detailed_results': [],
            'raw_result': [],
            'error': f"Unexpected error: {str(e)}"
        }

def get_pdb_info(pdb_id):
    """
    Получение основной информации о структуре PDB
    """
    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except:
        return None

def get_sequence_similarity_details(pdb_id, similarity_score):
    """
    Получение детальной информации о схожести последовательностей
    """
    # Для более детального анализа можно использовать дополнительные API
    # Здесь возвращаем базовую информацию
    return {
        'pdb_id': pdb_id,
        'similarity_percent': similarity_score,
        'similarity_level': get_similarity_level(similarity_score),
        'match_type': 'homology' if similarity_score < 100 else 'exact'
    }

def get_similarity_level(percent):
    """
    Определение уровня схожести
    """
    if percent == 100:
        return "exact_match"
    elif percent >= 90:
        return "very_high"
    elif percent >= 80:
        return "high"
    elif percent >= 70:
        return "medium"
    elif percent >= 60:
        return "low"
    else:
        return "very_low"

def process_dataset_with_rcsb(csv_file_path, output_file=None, identity_cutoff=0.8):
    """
    Обработка датасета с использованием RCSB API
    """
    # Читаем датасет
    if not os.path.exists(csv_file_path):
        print(f"Ошибка: Файл {csv_file_path} не найден!")
        return None
    
    df = pd.read_csv(csv_file_path)
    
    # Проверяем наличие необходимых колонок
    required_columns = ['nodeid', 'name', 'content']
    for col in required_columns:
        if col not in df.columns:
            print(f"Ошибка: В датасете отсутствует колонка '{col}'")
            return None
    
    print(f"Загружено записей: {len(df)}")
    print("Начинаем поиск в базе данных PDB...")
    print("=" * 60)
    
    results = []
    
    for index, row in df.iterrows():
        print(f"\nОбработка {index + 1}/{len(df)}: {row['name']}")
        print(f"Последовательность: {row['content'][:30]}...")
        print(f"Длина: {len(row['content'])} аминокислот")
        
        # Поиск в PDB
        sequence = row['content']
        result = search_pdb_by_sequence_rcsb(sequence, identity_cutoff)
        
        # Создаем детальную информацию о схожести
        similarity_info = []
        if result['found']:
            for pdb_result in result['detailed_results']:
                pdb_id = pdb_result.get('identifier', '')
                similarity_score = pdb_result.get('similarity', 0)
                
                # Получаем дополнительную информацию о структуре
                info = get_pdb_info(pdb_id)
                pdb_details = {
                    'pdb_id': pdb_id,
                    'similarity_percent': similarity_score,
                    'similarity_level': get_similarity_level(similarity_score),
                    'title': info.get('struct', {}).get('title', 'N/A') if info else 'N/A',
                    'resolution': info.get('rcsb_entry_info', {}).get('resolution_combined', ['N/A'])[0] if info and info.get('rcsb_entry_info', {}).get('resolution_combined') else 'N/A',
                }
                similarity_info.append(pdb_details)
                
                time.sleep(0.5)  # Пауза между запросами
        
        # Добавляем информацию к результатам
        result_data = {
            'nodeid': row['nodeid'],
            'name': row['name'],
            'sequence': sequence,
            'sequence_length': len(sequence),
            'found_in_pdb': result['found'],
            'pdb_results_count': result['count'],
            'pdb_ids': ', '.join(result['pdb_ids']) if result['pdb_ids'] else 'None',
            'similarity_info': json.dumps(similarity_info, ensure_ascii=False) if similarity_info else 'None',
            'max_similarity': max([item['similarity_percent'] for item in similarity_info]) if similarity_info else 0,
            'best_match': similarity_info[0]['pdb_id'] if similarity_info else 'None',
            'error': result['error'] if result['error'] else 'None'
        }
        
        results.append(result_data)
        
        # Вывод промежуточных результатов
        status = "✓ НАЙДЕНО" if result['found'] else "✗ НЕ НАЙДЕНО"
        print(f"  {status} - {result['count']} результатов")
        if result['found'] and similarity_info:
            best_match = similarity_info[0]
            print(f"  Лучшее совпадение: {best_match['pdb_id']} ({best_match['similarity_percent']}% схожести)")
            print(f"  Уровень схожести: {best_match['similarity_level']}")
        
        # Пауза между запросами чтобы не перегружать сервер
        time.sleep(2)
    
    # Создаем DataFrame с результатами
    results_df = pd.DataFrame(results)
    
    # Сохраняем результаты если указан output_file
    if output_file:
        results_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nРезультаты сохранены в: {output_file}")
    
    return results_df

def create_detailed_similarity_report(results_df, output_file="similarity_report.csv"):
    """
    Создание детального отчета о схожести
    """
    detailed_data = []
    
    for _, row in results_df.iterrows():
        if row['found_in_pdb'] and row['similarity_info'] != 'None':
            try:
                similarity_data = json.loads(row['similarity_info'])
                for match in similarity_data:
                    detailed_data.append({
                        'nodeid': row['nodeid'],
                        'name': row['name'],
                        'query_sequence_length': row['sequence_length'],
                        'pdb_id': match['pdb_id'],
                        'similarity_percent': match['similarity_percent'],
                        'similarity_level': match['similarity_level'],
                        'title': match['title'],
                        'resolution': match['resolution']
                    })
            except:
                pass
    
    if detailed_data:
        detailed_df = pd.DataFrame(detailed_data)
        detailed_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Детальный отчет о схожести сохранен в: {output_file}")
        return detailed_df
    else:
        print("Нет данных для детального отчета о схожести")
        return None

def print_summary(results_df):
    """
    Вывод сводки результатов поиска
    """
    if results_df is None:
        return
    
    print("\n" + "="*80)
    print("СВОДКА РЕЗУЛЬТАТОВ ПОИСКА")
    print("="*80)
    
    total = len(results_df)
    found = results_df['found_in_pdb'].sum()
    
    print(f"Всего обработано последовательностей: {total}")
    print(f"Найдено в PDB: {found} ({found/total*100:.1f}%)")
    print(f"Не найдено в PDB: {total - found} ({(total-found)/total*100:.1f}%)")
    
    if found > 0:
        avg_similarity = results_df[results_df['max_similarity'] > 0]['max_similarity'].mean()
        max_similarity = results_df['max_similarity'].max()
        print(f"Средняя максимальная схожесть: {avg_similarity:.1f}%")
        print(f"Максимальная схожесть: {max_similarity:.1f}%")
    
    print("\nДетальные результаты:")
    print("-" * 80)
    
    for _, row in results_df.iterrows():
        status = "✓ НАЙДЕНО" if row['found_in_pdb'] else "✗ НЕ НАЙДЕНО"
        print(f"{row['nodeid']}: {row['name']} - {status}")
        if row['found_in_pdb']:
            print(f"  Количество результатов: {row['pdb_results_count']}")
            print(f"  Максимальная схожесть: {row['max_similarity']}%")
            print(f"  Лучшее совпадение: {row['best_match']}")
        print("-" * 40)

def main():
    """
    Основная функция для обработки датасета
    """
    # Запрос пути к файлу
    csv_file_path = input("Введите путь к CSV файлу с данными: ").strip()
    
    # Проверяем существование файла
    if not os.path.exists(csv_file_path):
        print(f"Файл {csv_file_path} не найден!")
        return
    
    # Запрос имени выходного файла
    output_file = input("Введите имя для выходного файла (или нажмите Enter для 'pdb_results.csv'): ").strip()
    if not output_file:
        output_file = "pdb_results.csv"
    
    # Запрос порога идентичности
    try:
        identity_cutoff = float(input("Введите порог идентичности (0.0-1.0, по умолчанию 0.8): ").strip() or "0.8")
        if not 0.0 <= identity_cutoff <= 1.0:
            print("Порог должен быть между 0.0 и 1.0, использую 0.8")
            identity_cutoff = 0.8
    except ValueError:
        print("Некорректное значение, использую 0.8")
        identity_cutoff = 0.8
    
    print(f"\nНастройки поиска:")
    print(f"  Файл данных: {csv_file_path}")
    print(f"  Выходной файл: {output_file}")
    print(f"  Порог идентичности: {identity_cutoff}")
    print("=" * 60)
    
    # Запускаем обработку
    results = process_dataset_with_rcsb(
        csv_file_path=csv_file_path,
        output_file=output_file,
        identity_cutoff=identity_cutoff
    )
    
    # Выводим сводку
    if results is not None:
        print_summary(results)
        
        # Создаем детальный отчет о схожести
        detailed_report = create_detailed_similarity_report(results, "detailed_similarity_report.csv")
        
        # Сохраняем также краткий отчет
        summary_file = "search_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("СВОДКА ПОИСКА В PDB\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Дата поиска: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Файл данных: {csv_file_path}\n")
            f.write(f"Порог идентичности: {identity_cutoff}\n")
            f.write(f"Всего последовательностей: {len(results)}\n")
            f.write(f"Найдено в PDB: {results['found_in_pdb'].sum()}\n")
            f.write(f"Процент найденных: {results['found_in_pdb'].sum()/len(results)*100:.1f}%\n\n")
            
            if results['found_in_pdb'].sum() > 0:
                avg_similarity = results[results['max_similarity'] > 0]['max_similarity'].mean()
                f.write(f"Средняя схожесть: {avg_similarity:.1f}%\n\n")
            
            f.write("Детальные результаты:\n")
            f.write("-" * 40 + "\n")
            for _, row in results.iterrows():
                status = "НАЙДЕНО" if row['found_in_pdb'] else "НЕ НАЙДЕНО"
                f.write(f"{row['nodeid']}: {row['name']} - {status}\n")
                if row['found_in_pdb']:
                    f.write(f"  PDB IDs: {row['pdb_ids']}\n")
                    f.write(f"  Максимальная схожесть: {row['max_similarity']}%\n")
                f.write("\n")
        
        print(f"\nКраткий отчет сохранен в: {summary_file}")

# Запуск основной функции
if __name__ == "__main__":
    main()
