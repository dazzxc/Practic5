import { useState } from "react";
import styles from "./CheckSettings.module.css";
import { CATEGORIES, CATEGORY_ORDER } from "../utils/issueCategories";

// типы проверок колонки
const KINDS = [
  { value: "none", label: "не проверять" },
  { value: "number", label: "число" },
  { value: "email", label: "email" },
  { value: "date", label: "дата" },
  { value: "allowed", label: "список значений" },
];

// "%d.%m.%Y" -> "ДД.ММ.ГГГГ"
function formatLabel(format) {
  return format
    .replace("%Y", "ГГГГ").replace("%m", "ММ").replace("%d", "ДД")
    .replace("%H", "чч").replace("%M", "мм").replace("%S", "сс");
}

function getKind(rule) {
  if (!rule) return "none";
  if (rule.type) return rule.type;
  return rule.allowed ? "allowed" : "none";
}

function describeRule(rule) {
  if (rule.rule === "dates_order") return `«${rule.end}» не раньше «${rule.start}»`;
  if (rule.rule === "total") return `«${rule.total}» = «${rule.price}» × «${rule.quantity}»`;
  return rule.rule;
}

function CheckSettings({
  groups, onGroupsChange,
  mode, onModeChange,
  rules, onRulesChange,
  columns, dateFormats,
  rulesLoading, onReset,
}) {
  const [newRule, setNewRule] = useState({ rule: "dates_order" });
  // пересоздаёт поля списков после сброса
  const [resetKey, setResetKey] = useState(0);

  const toggleGroup = (category) => {
    onGroupsChange(groups.includes(category)
      ? groups.filter((g) => g !== category)
      : CATEGORY_ORDER.filter((g) => g === category || groups.includes(g)));
  };

  const setColumnRule = (column, rule) => {
    const invalidRules = { ...rules.invalid_rules };
    if (rule) invalidRules[column] = rule;
    else delete invalidRules[column];
    onRulesChange({ ...rules, invalid_rules: invalidRules });
  };

  const changeKind = (column, kind) => {
    if (kind === "none") setColumnRule(column, null);
    else if (kind === "date") setColumnRule(column, { type: "date", format: dateFormats[0] });
    else if (kind === "allowed") setColumnRule(column, { allowed: [] });
    else setColumnRule(column, { type: kind });
  };

  const changeLimit = (column, key, value) => {
    const rule = { ...rules.invalid_rules[column] };
    if (value === "") delete rule[key];
    else rule[key] = Number(value);
    setColumnRule(column, rule);
  };

  const toggleKey = (column) => {
    const keys = rules.key_columns || [];
    onRulesChange({
      ...rules,
      key_columns: keys.includes(column) ? keys.filter((c) => c !== column) : [...keys, column],
    });
  };

  const removeConsistency = (index) => {
    onRulesChange({
      ...rules,
      consistency_rules: rules.consistency_rules.filter((_, i) => i !== index),
    });
  };

  const newRuleReady = newRule.rule === "dates_order"
    ? newRule.start && newRule.end && newRule.start !== newRule.end
    : newRule.price && newRule.quantity && newRule.total;

  const addConsistency = () => {
    const rule = { ...newRule };
    if (rule.rule === "dates_order") {
      // формат берём из правила колонки
      const startRule = rules.invalid_rules[rule.start];
      const endRule = rules.invalid_rules[rule.end];
      if (startRule?.format) rule.start_format = startRule.format;
      if (endRule?.format) rule.end_format = endRule.format;
    }
    onRulesChange({ ...rules, consistency_rules: [...rules.consistency_rules, rule] });
    setNewRule({ rule: newRule.rule });
  };

  const columnSelect = (key, placeholder) => (
    <select
      className={styles.input}
      value={newRule[key] || ""}
      onChange={(e) => setNewRule({ ...newRule, [key]: e.target.value })}
    >
      <option value="">{placeholder}</option>
      {columns.map((c) => <option key={c} value={c}>{c}</option>)}
    </select>
  );

  return (
    <div className={styles.settings}>
      <h3 className={styles.sectionTitle}>Что искать</h3>
      <div className={styles.groups}>
        {CATEGORY_ORDER.map((category) => (
          <label key={category} className={`${styles.groupChip} ${styles[category]}`}>
            <input
              type="checkbox"
              checked={groups.includes(category)}
              onChange={() => toggleGroup(category)}
            />
            {CATEGORIES[category].label}
          </label>
        ))}
      </div>
      {groups.length === 0 && <p className={styles.warning}>Выберите хотя бы одну группу</p>}

      <h3 className={styles.sectionTitle}>Правила проверки</h3>
      <div className={styles.modes}>
        <label className={styles.mode}>
          <input type="radio" checked={mode === "auto"} onChange={() => onModeChange("auto")} />
          Подобрать автоматически
        </label>
        <label className={styles.mode}>
          <input type="radio" checked={mode === "manual"} onChange={() => onModeChange("manual")} />
          Настроить вручную
        </label>
      </div>

      {mode === "manual" && rulesLoading && <p className={styles.hint}>Читаем колонки файла...</p>}

      {mode === "manual" && rules && !rulesLoading && (
        <>
          <p className={styles.hint}>
            Ниже правила, которые программа подобрала сама. Измените то, что нужно.
            <button
              type="button"
              className={styles.linkButton}
              onClick={() => { onReset(); setResetKey(resetKey + 1); }}
            >
              Вернуть как было
            </button>
          </p>

          <div className={styles.tableWrap}>
            <table className={styles.rulesTable}>
              <thead>
                <tr>
                  <th>Колонка</th>
                  <th>Проверка</th>
                  <th>Параметры</th>
                  <th>Ключ</th>
                </tr>
              </thead>
              <tbody>
                {columns.map((column) => {
                  const rule = rules.invalid_rules[column];
                  const kind = getKind(rule);
                  return (
                    <tr key={column}>
                      <td className={styles.columnName}>{column}</td>
                      <td>
                        <select
                          className={styles.input}
                          value={kind}
                          onChange={(e) => changeKind(column, e.target.value)}
                        >
                          {KINDS.map((k) => <option key={k.value} value={k.value}>{k.label}</option>)}
                        </select>
                      </td>
                      <td>
                        {kind === "number" && (
                          <div className={styles.params}>
                            <input
                              type="number"
                              className={styles.input}
                              placeholder="от"
                              value={rule.min ?? ""}
                              onChange={(e) => changeLimit(column, "min", e.target.value)}
                            />
                            <input
                              type="number"
                              className={styles.input}
                              placeholder="до"
                              value={rule.max ?? ""}
                              onChange={(e) => changeLimit(column, "max", e.target.value)}
                            />
                          </div>
                        )}
                        {kind === "date" && (
                          <select
                            className={styles.input}
                            value={rule.format}
                            onChange={(e) => setColumnRule(column, { ...rule, format: e.target.value })}
                          >
                            {dateFormats.map((f) => <option key={f} value={f}>{formatLabel(f)}</option>)}
                          </select>
                        )}
                        {kind === "allowed" && (
                          <input
                            key={`${column}-${resetKey}`}
                            className={styles.input}
                            placeholder="через запятую"
                            defaultValue={(rule.allowed || []).join(", ")}
                            onChange={(e) => setColumnRule(column, {
                              allowed: e.target.value.split(",").map((v) => v.trim()).filter(Boolean),
                            })}
                          />
                        )}
                      </td>
                      <td className={styles.keyCell}>
                        <input
                          type="checkbox"
                          checked={(rules.key_columns || []).includes(column)}
                          onChange={() => toggleKey(column)}
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className={styles.hint}>Ключ — колонка, значения в которой не должны повторяться (например, id).</p>

          <h3 className={styles.sectionTitle}>Связи между колонками</h3>
          {rules.consistency_rules.length === 0 && <p className={styles.hint}>Связей нет</p>}
          <ul className={styles.consistencyList}>
            {rules.consistency_rules.map((rule, index) => (
              <li key={index} className={styles.consistencyItem}>
                {describeRule(rule)}
                <button type="button" className={styles.removeButton} onClick={() => removeConsistency(index)}>
                  Убрать
                </button>
              </li>
            ))}
          </ul>

          <div className={styles.addRule}>
            <select
              className={styles.input}
              value={newRule.rule}
              onChange={(e) => setNewRule({ rule: e.target.value })}
            >
              <option value="dates_order">Дата конца не раньше начала</option>
              <option value="total">Итог = цена × количество</option>
            </select>
            {newRule.rule === "dates_order" ? (
              <>
                {columnSelect("start", "дата начала")}
                {columnSelect("end", "дата конца")}
              </>
            ) : (
              <>
                {columnSelect("price", "цена")}
                {columnSelect("quantity", "количество")}
                {columnSelect("total", "итог")}
              </>
            )}
            <button type="button" className={styles.addButton} disabled={!newRuleReady} onClick={addConsistency}>
              Добавить
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default CheckSettings;
