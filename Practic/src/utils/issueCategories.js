// Всё про группы ошибок в одном месте: названия, цвета и тексты советов.
// У каждой ошибки от бэкенда есть "category" (одна из 4 групп) и более точный "type".

export const CATEGORIES = {
  missing: {
    label: "Пропуски",
    title: "Пропущенные значения",
    color: "#D9444A",
    text: "В данных обнаружены пропущенные значения. Проверьте пустые ячейки и заполните их корректными значениями или удалите строки, в которых данные отсутствуют",
  },
  duplicate: {
    label: "Дубликаты",
    title: "Повторяющиеся данные",
    color: "#D7DF55",
    text: "В данных обнаружены повторяющиеся строки или ключи. Проверьте дубликаты и удалите записи, которые не должны повторяться",
  },
  invalid: {
    label: "Некорректные значения",
    title: "Некорректные значения",
    color: "#169BD5",
    text: "В данных обнаружены значения, которые не соответствуют ожидаемому типу, формату или диапазону. Проверьте их и исправьте некорректные данные",
  },
  inconsistency: {
    label: "Несогласованности",
    title: "Несогласованности",
    color: "#E17A21",
    text: "В данных обнаружены несогласованности между колонками. Проверьте связанные значения: даты начала и окончания, суммы и их составляющие",
  },
};

// В каком порядке показываем группы
export const CATEGORY_ORDER = ["missing", "duplicate", "invalid", "inconsistency"];

// Если в старом отчёте нет category, находим группу по type
const TYPE_TO_CATEGORY = {
  missing: "missing",
  duplicate_row: "duplicate",
  duplicate_key: "duplicate",
  wrong_type: "invalid",
  out_of_range: "invalid",
  wrong_format: "invalid",
  wrong_date: "invalid",
  not_allowed: "invalid",
  inconsistent: "inconsistency",
};

// Названия типов для таблицы
export const TYPE_LABELS = {
  missing: "Пропуск",
  duplicate_row: "Дубль строки",
  duplicate_key: "Повтор ключа",
  wrong_type: "Неверный тип",
  out_of_range: "Вне диапазона",
  wrong_format: "Неверный формат",
  wrong_date: "Неверная дата",
  not_allowed: "Недопустимое значение",
  inconsistent: "Несогласованность",
};

export function getCategory(issue) {
  return issue.category || TYPE_TO_CATEGORY[issue.type] || "invalid";
}

// Сколько ошибок в каждой группе: { missing: 10, duplicate: 3, ... }
export function countByCategory(issues = []) {
  const result = { missing: 0, duplicate: 0, invalid: 0, inconsistency: 0 };
  issues.forEach((issue) => {
    result[getCategory(issue)] += Number(issue.count) || 0;
  });
  return result;
}
