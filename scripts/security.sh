#!/usr/bin/env bash
set -e

# Скрипт для проверки безопасности
SRC_DIR="./app"

echo "Проверка инструментов безопасности..."

# Проверка bandit
if ! poetry run bandit --version &>/dev/null; then
    echo "Ошибка: bandit не установлен"
    exit 1
fi

# Проверка safety
if ! poetry run safety check --help &>/dev/null; then
    echo "Ошибка: safety не установлен"
    exit 1
fi

# Проверка наличия исходного кода
if [ ! -d "${SRC_DIR}" ]; then
    echo "Ошибка: директория с исходным кодом не найдена"
    exit 1
fi

echo "Запуск проверки безопасности..."

# Создание директории для отчетов
report_dir="security_reports"
mkdir -p "$report_dir"

# Запуск bandit
echo "Запуск bandit..."
poetry run bandit -r ${SRC_DIR} -c pyproject.toml -f json -o "$report_dir/bandit_report.json" || {
    echo "Ошибка: найдены проблемы безопасности в коде"
    exit 1
}

# Запуск safety
echo "Запуск safety..."
if ! poetry run safety check --full-report --json > "$report_dir/safety_report.json"; then
    echo "Найдены уязвимости в зависимостях" >&2
    cat "$report_dir/safety_report.json" >&2
    exit 1
fi

echo "Проверка безопасности завершена успешно"
echo "Отчеты сохранены в директории $report_dir"