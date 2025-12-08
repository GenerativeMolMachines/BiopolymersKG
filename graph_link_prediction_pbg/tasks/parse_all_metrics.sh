#!/bin/bash

# Скрипт для обработки всех eval лог-файлов и создания метрик

LOGS_DIR="logs"
METRICS_DIR="metrics"
SCRIPT_DIR="tasks"

# Создаем директорию для метрик, если её нет
mkdir -p "$METRICS_DIR"

# Обрабатываем все eval_*.log файлы
for log_file in "$LOGS_DIR"/eval_*.log; do
    if [ ! -f "$log_file" ]; then
        echo "Warning: No eval log files found in $LOGS_DIR"
        exit 1
    fi
    
    # Получаем имя файла без пути и расширения
    log_basename=$(basename "$log_file" .log)
    
    # Формируем имя выходного файла
    output_file="$METRICS_DIR/${log_basename}_metrics.json"
    
    echo "Processing $log_file -> $output_file"
    
    # Запускаем парсинг метрик
    if "$SCRIPT_DIR/awk_parse_metrics.sh" "$log_file" > "$output_file"; then
        echo "✓ Successfully created $output_file"
    else
        echo "✗ Failed to process $log_file"
        exit 1
    fi
done

echo "All metrics collected successfully!"



