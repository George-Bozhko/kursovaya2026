import time
import json

import streamlit as st
import pandas as pd

from scanner import FileScanner
from extractor import TextExtractor
from artifact_detector import ArtifactDetector
from risk_assessor import RiskAssessor
from ai_analyzer import AIAnalyzer
from report_generator import ReportGenerator


def format_duration(seconds):

    seconds = int(round(seconds))

    if seconds < 60:
        return f"{seconds} с"

    minutes, sec = divmod(seconds, 60)

    if minutes < 60:
        return f"{minutes} мин {sec:02d} с"

    hours, minutes = divmod(minutes, 60)

    return f"{hours} ч {minutes:02d} мин"


def extract_ai_importance(analysis_text):

    try:
        data = json.loads(analysis_text)
        value = data.get("importance")
        return value if value else None
    except Exception:
        return None

def get_context(text, artifact, window=80):

    try:

        pos = text.lower().find(
            str(artifact).lower()
        )

        if pos == -1:
            return ""

        start = max(0, pos - window)
        end = min(
            len(text),
            pos + len(str(artifact)) + window
        )

        fragment = text[start:end]

        return fragment.replace("\n", " ")

    except Exception:
        return ""


ARTIFACT_ICONS = {
    "passwords": "🔑",
    "ips": "🌐",
    "sha256": "🔒",
    "emails": "📧",
    "phones": "📞",
    "md5": "🔒",
    "sha1": "🔒",
    "urls": "🔗",
    "domains": "🌍",
}


st.set_page_config(
    page_title="Платформа поддержки специалиста по компьютерной экспертизе",
    layout="wide"
)

st.title("🔍 Платформа поддержки специалиста по компьютерной экспертизе")

st.write(
    "Поиск документов, извлечение данных и интеллектуальный анализ."
)

with st.sidebar:

    st.header("⚙️ Параметры ИИ")

    model_choice = st.selectbox(
        "Модель Ollama",
        options=[
            "qwen3:4b-instruct-2507-q4_K_M",
            "qwen3:1.7b",
            "qwen3:8b",
            "llama3.1:8b",
        ],
        index=0,
    )

    custom_model = st.text_input(
        "…или впишите свою модель",
        value="",
        placeholder="например, gemma3:4b",
    )

    ai_model = custom_model.strip() or model_choice

    ai_num_ctx = st.number_input(
        "Размер контекста (num_ctx)",
        min_value=512,
        max_value=32768,
        value=4096,
        step=512,
    )

    ai_timeout = st.number_input(
        "Таймаут на файл (сек)",
        min_value=30,
        max_value=1800,
        value=600,
        step=30,
    )

    st.caption(f"Будет использована модель: **{ai_model}**")

    st.divider()

    st.header("📐 Методика оценки")

    st.markdown(
        "**Балл документа** = Σ (количество артефактов × вес типа)."
    )

    st.subheader("Шкала критичности")

    thresholds_df = pd.DataFrame(
        RiskAssessor.thresholds_table()
    ).rename(columns={"level": "Уровень", "range": "Баллы"})

    st.table(thresholds_df.set_index("Уровень"))

    st.subheader("Вес артефактов")

    weights_df = pd.DataFrame(
        RiskAssessor.weights_table()
    ).rename(columns={"type": "Тип артефакта", "weight": "Вес"})

    st.table(weights_df.set_index("Тип артефакта"))

folder = st.text_input(
    "Путь к каталогу",
    value="uploads"
)

search_text = st.text_input(
    "🔎 Поиск по содержимому документов"
)

artifact_search = st.text_input(
    "🔍 Поиск значения артефакта"
)

artifact_types = st.multiselect(
    "🎯 Типы артефактов",
    [
        "Пароли",
        "Логины",
        "Email",
        "IP",
        "Телефоны",
        "Домены",
        "MD5",
        "SHA1",
        "SHA256",
        "JWT",
        "API-ключи"
    ],
    default=[]
)

risk_filter = st.multiselect(
    "⚠️ Уровень риска",
    [
        "Критический",
        "Высокий",
        "Средний",
        "Низкий"
    ],
    default=[]
)

if st.button("Начать анализ"):

    scanner = FileScanner(folder)
    extractor = TextExtractor()
    detector = ArtifactDetector()
    assessor = RiskAssessor()
    analyzer = AIAnalyzer(
        model_name=ai_model,
        num_ctx=int(ai_num_ctx),
        timeout=int(ai_timeout)
    )
    generator = ReportGenerator()

    files = scanner.scan()

    st.success(f"Найдено файлов: {len(files)} · модель ИИ: {ai_model}")

    if not files:
        st.warning(
            "В указанном каталоге нет подходящих файлов "
            "(.txt, .pdf, .docx, .xlsx, .csv). Проверьте путь."
        )
        st.stop()

    analysis_results = []

    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    progress_bar = st.progress(0)
    status_text = st.empty()

    ai_durations = []
    failures = []
    total_start = time.time()

    for index, file_info in enumerate(files):

        text = extractor.extract(
            file_info["path"]
        )

        artifacts = detector.detect(text)

        risk = assessor.assess(artifacts)

        if risk["level"] == "Критический":
            critical_count += 1

        elif risk["level"] == "Высокий":
            high_count += 1

        elif risk["level"] == "Средний":
            medium_count += 1

        else:
            low_count += 1

        if ai_durations:
            avg = sum(ai_durations) / len(ai_durations)
            remaining = len(files) - index
            eta = avg * remaining

            status_text.info(
                f"⏳ Файл {index + 1} из {len(files)} · "
                f"в среднем {format_duration(avg)} на файл · "
                f"осталось примерно {format_duration(eta)}"
            )
        else:
            status_text.info(
                f"⏳ Файл {index + 1} из {len(files)} · "
                f"оценка времени появится после первого файла…"
            )

        with st.spinner(
                f"Анализируется {file_info['name']}..."
        ):
            ai_start = time.time()

            try:
                analysis = analyzer.analyze(text)
                ai_durations.append(time.time() - ai_start)
            except Exception as e:
                analysis = f"⚠️ Анализ не выполнен: {e}"
                failures.append(file_info["name"])

        ai_importance = extract_ai_importance(analysis)

        analysis_results.append(
            {
                "file_info": file_info,
                "text": text,
                "artifacts": artifacts,
                "risk": risk,
                "analysis": analysis,
                "ai_importance": ai_importance
            }
        )

        progress_bar.progress(
            (index + 1) / len(files)
        )

    total_elapsed = time.time() - total_start

    risk_priority = {
        "Критический": 4,
        "Высокий": 3,
        "Средний": 2,
        "Низкий": 1
    }

    analysis_results.sort(
        key=lambda x: (
            risk_priority.get(x["risk"]["level"], 0),
            x["risk"]["score"]
        ),
        reverse=True
    )

    reports = [
        {
            "file_name": r["file_info"]["name"],
            "file_path": r["file_info"]["path"],
            "risk_level": r["risk"]["level"],
            "risk_score": r["risk"]["score"],
            "artifacts": r["artifacts"],
            "analysis": r["analysis"],
            "ai_importance": r["ai_importance"],
        }
        for r in analysis_results
    ]

    pdf_path = generator.generate(reports, "expert_report.pdf")

    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    st.session_state["analysis_done"] = True
    st.session_state["analysis_results"] = analysis_results
    st.session_state["counts"] = {
        "Критический": critical_count,
        "Высокий": high_count,
        "Средний": medium_count,
        "Низкий": low_count,
    }
    st.session_state["pdf_bytes"] = pdf_bytes
    st.session_state["model_used"] = ai_model
    st.session_state["total_elapsed"] = total_elapsed
    st.session_state["failures"] = failures

    status_text.success(
        f"✅ Обработка завершена · файлов: {len(files)} · "
        f"общее время: {format_duration(total_elapsed)}"
    )


if st.session_state.get("analysis_done"):

    results = st.session_state["analysis_results"]
    counts = st.session_state["counts"]
    failures = st.session_state.get("failures", [])

    if failures:
        st.warning(
            "Не удалось проанализировать (показаны с пометкой об ошибке): "
            + ", ".join(failures)
        )

    st.divider()

    st.subheader("📊 Статистика")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🔴 Критические", counts["Критический"])
    col2.metric("🟠 Высокие", counts["Высокий"])
    col3.metric("🟡 Средние", counts["Средний"])
    col4.metric("🟢 Низкие", counts["Низкий"])

    st.divider()

    st.subheader("🚨 Ключевые находки")
    st.caption(
        "Наиболее значимые цифровые артефакты, обнаруженные во всех документах."
    )

    key_findings = []

    for result in results:

        risk = result["risk"]

        if risk_filter:

            if risk["level"] not in risk_filter:
                continue

        file_name = result["file_info"]["name"]
        artifacts = result["artifacts"]
        artifact_map = {
            "Пароли": "passwords",
            "Логины": "logins",
            "Email": "emails",
            "IP": "ips",
            "Телефоны": "phones",
            "Домены": "domains",
            "MD5": "md5",
            "SHA1": "sha1",
            "SHA256": "sha256",
            "JWT": "jwt_tokens",
            "API-ключи": "api_keys"
        }

        if artifact_types:

            has_match = False

            for selected_type in artifact_types:

                key = artifact_map[selected_type]

                if artifacts.get(key):
                    has_match = True
                    break

            if not has_match:
                continue

        for value in artifacts.get("passwords", []):
            key_findings.append({
                "priority": 100,
                "file": file_name,
                "type": "Пароль",
                "value": value
            })

        for value in artifacts.get("api_keys", []):
            key_findings.append({
                "priority": 95,
                "file": file_name,
                "type": "API-ключ",
                "value": value[:25] + "..."
            })

        for value in artifacts.get("jwt_tokens", []):
            key_findings.append({
                "priority": 90,
                "file": file_name,
                "type": "JWT-токен",
                "value": value[:35] + "..."
            })

        for value in artifacts.get("logins", []):
            key_findings.append({
                "priority": 85,
                "file": file_name,
                "type": "Логин",
                "value": value
            })

        for value in artifacts.get("emails", []):
            key_findings.append({
                "priority": 70,
                "file": file_name,
                "type": "Email",
                "value": value
            })

        for value in artifacts.get("ips", []):
            key_findings.append({
                "priority": 60,
                "file": file_name,
                "type": "IP-адрес",
                "value": value
            })

    key_findings.sort(
        key=lambda x: x["priority"],
        reverse=True
    )

    if key_findings:

        findings_df = pd.DataFrame(
            key_findings[:10]
        )

        findings_df = findings_df.rename(
            columns={
                "priority": "Приоритет",
                "type": "Тип",
                "value": "Значение",
                "file": "Файл"
            }
        )

        st.dataframe(
            findings_df,
            width="stretch",
            hide_index=True
        )


    else:

        st.info(

            "По выбранным фильтрам артефакты не найдены."

        )

    st.divider()

    st.subheader("📋 Единый реестр артефактов")

    registry_rows = []

    artifact_labels = {

        "passwords": "Пароль",

        "logins": "Логин",

        "emails": "Email",

        "ips": "IP",

        "phones": "Телефон",

        "domains": "Домен",

        "md5": "MD5",

        "sha1": "SHA1",

        "sha256": "SHA256",

        "jwt_tokens": "JWT",

        "api_keys": "API-ключ"

    }

    artifact_map = {

        "Пароли": "passwords",

        "Логины": "logins",

        "Email": "emails",

        "IP": "ips",

        "Телефоны": "phones",

        "Домены": "domains",

        "MD5": "md5",

        "SHA1": "sha1",

        "SHA256": "sha256",

        "JWT": "jwt_tokens",

        "API-ключи": "api_keys"

    }

    for result in results:

        file_name = result["file_info"]["name"]

        artifacts = result["artifacts"]

        for artifact_key, values in artifacts.items():

            if not isinstance(values, list):
                continue

            if artifact_types:

                allowed_types = [

                    artifact_map[x]

                    for x in artifact_types

                ]

                if artifact_key not in allowed_types:
                    continue

            for value in values:
                registry_rows.append(

                    {

                        "Тип": artifact_labels.get(

                            artifact_key,

                            artifact_key

                        ),

                        "Значение": value,

                        "Файл": file_name

                    }

                )

    if registry_rows:

        registry_df = pd.DataFrame(

            registry_rows

        )

        st.dataframe(

            registry_df,

            width="stretch",

            hide_index=True

        )


    else:

        st.info(

            "Артефакты не обнаружены."

        )

    st.divider()

    st.subheader("📂 Результаты анализа")

    active_filters = []

    if search_text:
        active_filters.append(
            f"Текст: {search_text}"
        )

    if artifact_search:
        active_filters.append(
            f"Артефакт: {artifact_search}"
        )

    if artifact_types:
        active_filters.append(
            "Типы: " + ", ".join(artifact_types)
        )

    if active_filters:
        st.info(
            "Активные фильтры: "
            + " | ".join(active_filters)
        )

    filtered_results = []

    for i, result in enumerate(results):

        text = result["text"]

        artifacts = result["artifacts"]

        risk = result["risk"]

        if risk_filter:

            if risk["level"] not in risk_filter:
                continue

        if search_text:

            if search_text.lower() not in text.lower():
                continue

        if artifact_search:

            found = False

            for values in artifacts.values():

                if not isinstance(values, list):
                    continue

                for value in values:

                    if artifact_search.lower() in str(value).lower():
                        found = True
                        break

                if found:
                    break

            if not found:
                continue

        artifact_map = {
            "Пароли": "passwords",
            "Логины": "logins",
            "Email": "emails",
            "IP": "ips",
            "Телефоны": "phones",
            "Домены": "domains",
            "MD5": "md5",
            "SHA1": "sha1",
            "SHA256": "sha256",
            "JWT": "jwt_tokens",
            "API-ключи": "api_keys"
        }

        if artifact_types:

            has_match = False

            for selected_type in artifact_types:

                key = artifact_map[selected_type]

                if artifacts.get(key):
                    has_match = True
                    break

            if not has_match:
                continue

        file_info = result["file_info"]
        artifacts = result["artifacts"]
        risk = result["risk"]
        analysis = result["analysis"]

        filtered_results.append(result)

        with st.expander(f"📄 {file_info['name']}", expanded=False):

            st.subheader("Оценка риска")

            if risk["level"] == "Критический":
                st.error(f"🔴 {risk['level']}")

            elif risk["level"] == "Высокий":
                st.warning(f"🟠 {risk['level']}")

            elif risk["level"] == "Средний":
                st.warning(f"🟡 {risk['level']}")

            else:
                st.success(f"🟢 {risk['level']}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Уровень риска", risk["level"])

            with col2:
                st.metric("Баллы риска", risk["score"])

            with col3:
                st.metric(
                    "Оценка ИИ",
                    result.get("ai_importance") or "—"
                )

            st.subheader("Как набран балл")

            if risk["breakdown"]:

                breakdown_df = pd.DataFrame(
                    risk["breakdown"]
                ).rename(columns={
                    "type": "Тип артефакта",
                    "count": "Найдено",
                    "weight": "Вес",
                    "points": "Баллы",
                })

                st.table(breakdown_df.set_index("Тип артефакта"))

                st.caption(
                    f"Сумма баллов: {risk['score']} → "
                    f"уровень «{risk['level']}»"
                )

            else:
                st.caption("Артефакты не найдены — балл 0.")

            st.subheader("Найденные артефакты")

            for art_key in RiskAssessor.WEIGHTS:

                art_label = RiskAssessor.LABELS[art_key]

                icon = ARTIFACT_ICONS.get(
                    art_key,
                    "•"
                )

                values = artifacts.get(
                    art_key,
                    []
                )

                if not values:
                    st.write(
                        f"{icon} {art_label}: —"
                    )

                    continue

                st.markdown(
                    f"### {icon} {art_label}"
                )

                for value in values:

                    st.code(
                        str(value)
                    )

                    context = get_context(
                        text,
                        value
                    )

                    if context:
                        st.caption(
                            "Контекст:"
                        )

                        st.info(
                            context
                        )

            st.subheader("ИИ-анализ")

            st.code(analysis, language="json")

            st.subheader("Фрагмент текста")

            st.text_area(
                "Содержимое документа",
                text[:2000],
                height=200,
                key=f"doc_text_{i}"
            )

    if not filtered_results:
        st.info(
            "По заданным параметрам документы не найдены."
        )

    st.divider()

    st.subheader("🧾 Итоговое заключение эксперта")

    total_files = len(results)

    total_artifacts = {
        "emails": 0,
        "passwords": 0,
        "ips": 0,
        "phones": 0,
        "domains": 0,
        "logins": 0,
        "api_keys": 0,
        "jwt_tokens": 0,
    }

    for result in results:

        artifacts = result["artifacts"]

        for key in total_artifacts:
            total_artifacts[key] += len(
                artifacts.get(key, [])
            )

    critical_docs = [
        r for r in results
        if r["risk"]["level"] == "Критический"
    ]

    high_docs = [
        r for r in results
        if r["risk"]["level"] == "Высокий"
    ]

    top_docs = sorted(
        results,
        key=lambda x: x["risk"]["score"],
        reverse=True
    )[:5]

    conclusion = f"""
    Проанализировано документов: {total_files}

    Распределение рисков:
    • Критический: {counts['Критический']}
    • Высокий: {counts['Высокий']}
    • Средний: {counts['Средний']}
    • Низкий: {counts['Низкий']}

    Обнаруженные цифровые артефакты:
    • Email: {total_artifacts['emails']}
    • Пароли: {total_artifacts['passwords']}
    • Логины: {total_artifacts['logins']}
    • IP-адреса: {total_artifacts['ips']}
    • Телефоны: {total_artifacts['phones']}
    • Домены: {total_artifacts['domains']}
    • API-ключи: {total_artifacts['api_keys']}
    • JWT-токены: {total_artifacts['jwt_tokens']}

    Наиболее рискованные документы:
    """

    for i, doc in enumerate(top_docs, start=1):
        conclusion += (
            f"\n{i}. "
            f"{doc['file_info']['name']} "
            f"(балл риска: {doc['risk']['score']}, "
            f"{doc['risk']['level']})"
        )

    if critical_docs:

        conclusion += (
            "\n\nВывод: обнаружены документы "
            "критического уровня риска, содержащие "
            "конфиденциальные цифровые артефакты. "
            "Рекомендуется проведение дополнительного "
            "экспертного исследования."
        )

    elif high_docs:

        conclusion += (
            "\n\nВывод: обнаружены документы высокого "
            "уровня риска. Рекомендуется проверка "
            "источников происхождения данных."
        )

    else:

        conclusion += (
            "\n\nВывод: критически опасных документов "
            "не выявлено. Обнаруженные артефакты "
            "требуют дополнительной оценки экспертом."
        )

    st.text_area(
        "Заключение",
        conclusion,
        height=400
    )

    st.divider()

    st.subheader("📄 Экспорт отчёта")

    st.download_button(
        label="📥 Скачать экспертный отчёт PDF",
        data=st.session_state["pdf_bytes"],
        file_name="expert_report.pdf",
        mime="application/pdf"
    )