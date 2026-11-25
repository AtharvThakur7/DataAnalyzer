import json
import logging
import traceback
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)

NUMERIC_DTYPES = {'int64', 'float64', 'int32', 'float32'}

# Safe builtins for sandboxed pandas execution
_SAFE_BUILTINS = {
    'abs': abs, 'all': all, 'any': any, 'bool': bool, 'dict': dict,
    'enumerate': enumerate, 'filter': filter, 'float': float, 'format': format,
    'frozenset': frozenset, 'int': int, 'isinstance': isinstance, 'len': len,
    'list': list, 'map': map, 'max': max, 'min': min, 'print': print,
    'range': range, 'reversed': reversed, 'round': round, 'set': set,
    'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple, 'type': type,
    'zip': zip, 'True': True, 'False': False, 'None': None,
}


def _get_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def _get_model():
    return 'gpt-4o-mini'


def _build_data_context(columns_meta: dict, stats: dict, sample_rows: list) -> str:
    col_descriptions = []
    for col, meta in columns_meta.items():
        is_num = meta['dtype'] in NUMERIC_DTYPES
        desc = f"- {col} ({'numeric' if is_num else 'categorical'}, dtype={meta['dtype']}): {meta['unique_count']} unique, {meta['null_pct']}% null"
        if 'mean' in meta:
            desc += f", mean={meta['mean']}, min={meta['min']}, max={meta['max']}"
        col_descriptions.append(desc)

    return f"""Dataset Overview:
- Rows: {stats.get('shape', [0, 0])[0]}, Columns: {stats.get('shape', [0, 0])[1]}
- Total nulls: {stats.get('total_nulls', 0)}
- Duplicates: {stats.get('total_duplicates', 0)}
- Numeric columns: {', '.join(stats.get('numeric_columns', []))}
- Categorical columns: {', '.join(stats.get('categorical_columns', []))}

Columns:
{chr(10).join(col_descriptions)}

Sample data (first 5 rows):
{json.dumps(sample_rows[:5], default=str)}"""


CHART_SPEC_RULES = """CHART SPECIFICATION RULES (follow strictly):
- x_column MUST be an exact column name from the dataset
- y_column MUST be a numeric column (int64/float64) or null
- If y_column is null, the chart shows value counts of x_column
- aggregation must be one of: mean, sum, count, min, max, median — NEVER "none"
- For categorical x + numeric y: use bar/pie with mean/sum
- For numeric x without y: use histogram with count
- For two numeric columns: use scatter
- chart_type must be one of: bar, line, pie, scatter, area, histogram, donut, radar

Each chart spec JSON format:
{"title": "...", "chart_type": "bar|line|pie|scatter|area|histogram|donut|radar", "x_column": "exact_col_name", "y_column": "exact_numeric_col_name" or null, "aggregation": "mean|sum|count|min|max|median", "reason": "..."}
Wrap each in a ```chart-json ``` code block."""


def _validate_chart_specs(charts: list, columns_meta: dict) -> list:
    valid_cols = set(columns_meta.keys())
    numeric_cols = {c for c, m in columns_meta.items() if m['dtype'] in NUMERIC_DTYPES}
    validated = []
    for s in charts:
        if not isinstance(s, dict):
            continue
        if s.get('x_column') not in valid_cols:
            continue
        if s.get('y_column') and s['y_column'] not in valid_cols:
            s['y_column'] = None
        if s.get('y_column') and s['y_column'] not in numeric_cols:
            s['y_column'] = None
            s['aggregation'] = 'count'
        if s.get('aggregation') in ('none', None, ''):
            s['aggregation'] = 'count'
        validated.append(s)
    return validated


# ---------------------------------------------------------------------------
# DATA AGENT: execute pandas code against real data
# ---------------------------------------------------------------------------

def _build_column_schema(columns_meta: dict) -> str:
    lines = []
    for col, meta in columns_meta.items():
        is_num = meta['dtype'] in NUMERIC_DTYPES
        line = f"  '{col}': {meta['dtype']} ({'numeric' if is_num else 'categorical'}), {meta['unique_count']} unique"
        if 'mean' in meta:
            line += f", range [{meta['min']}, {meta['max']}]"
        lines.append(line)
    return '\n'.join(lines)


CODE_GEN_SYSTEM = """You are a pandas code generator for a data analytics platform.
Given a user question and a DataFrame schema, write Python code that computes the answer.

RULES:
- The DataFrame is already loaded as `df`. Do NOT read files or create dataframes.
- Use only pandas and numpy. No other imports.
- Store your final answer in a variable called `result` — it must be a dict with these keys:
  - "answer": a string with the computed answer (include specific numbers, not just column names)
  - "table": (optional) a list of dicts for tabular results, max 20 rows
  - "values": (optional) a dict of key computed values like {"mean_salary": 45000, "total_count": 500}
- Keep code simple and direct. Use .head(20) for large outputs.
- Handle NaN values: use dropna() before aggregations.
- For correlations, use df[numeric_cols].corr() — only on numeric columns.
- NEVER use print() as your output — always assign to `result`.
- NEVER modify df in-place (no inplace=True). Create new variables if needed.
- NEVER use exec(), eval(), __import__, open(), os, sys, subprocess, or file operations.
- If the question is vague, compute the most useful summary.

COLUMN SCHEMA:
{schema}

Dataset shape: {rows} rows × {cols} columns

Respond ONLY with a ```python code block. No explanation."""


def _generate_analysis_code(question: str, columns_meta: dict, stats: dict) -> str:
    client = _get_client()
    schema = _build_column_schema(columns_meta)
    shape = stats.get('shape', [0, 0])

    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {
                "role": "system",
                "content": CODE_GEN_SYSTEM.format(
                    schema=schema, rows=shape[0], cols=shape[1],
                ),
            },
            {"role": "user", "content": question},
        ],
        max_tokens=1500,
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()
    if '```python' in raw:
        raw = raw.split('```python', 1)[1].rsplit('```', 1)[0]
    elif '```' in raw:
        raw = raw.split('```', 1)[1].rsplit('```', 1)[0]
    return raw.strip()


def _execute_pandas_code(code: str, df) -> dict:
    import pandas as pd
    import numpy as np

    forbidden = ['__import__', 'exec(', 'eval(', 'open(', 'os.', 'sys.',
                 'subprocess', 'importlib', 'compile(', 'globals(', 'locals(',
                 'getattr(', 'setattr(', 'delattr(', '__builtins__']
    for token in forbidden:
        if token in code:
            return {'error': f'Forbidden operation detected: {token}'}

    sandbox_globals = {
        '__builtins__': _SAFE_BUILTINS,
        'pd': pd,
        'np': np,
        'df': df.copy(),
    }
    sandbox_locals = {}

    try:
        exec(code, sandbox_globals, sandbox_locals)
    except Exception as e:
        tb = traceback.format_exc().split('\n')
        short_tb = '\n'.join(tb[-4:])
        return {'error': f'{type(e).__name__}: {e}', 'traceback': short_tb}

    result = sandbox_locals.get('result')
    if result is None:
        return {'error': 'Code did not produce a `result` variable'}

    if isinstance(result, pd.DataFrame):
        result = {
            'answer': f'Query returned {len(result)} rows.',
            'table': result.head(20).to_dict('records'),
        }
    elif isinstance(result, pd.Series):
        result = {
            'answer': f'Result: {result.to_dict()}',
            'values': {str(k): _safe_value(v) for k, v in result.head(20).to_dict().items()},
        }
    elif isinstance(result, (int, float, str, bool)):
        result = {'answer': str(result)}
    elif not isinstance(result, dict):
        result = {'answer': str(result)}

    if isinstance(result, dict):
        if 'table' in result:
            result['table'] = _sanitize_table(result['table'])
        if 'values' in result:
            result['values'] = {str(k): _safe_value(v) for k, v in result['values'].items()}
        if 'answer' in result:
            result['answer'] = str(result['answer'])

    return result


def _safe_value(v):
    import numpy as np
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        f = float(v)
        if f != f or abs(f) == float('inf'):
            return 0
        return round(f, 4)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


def _sanitize_table(table):
    import numpy as np
    clean = []
    for row in (table or [])[:20]:
        if isinstance(row, dict):
            clean.append({str(k): _safe_value(v) if isinstance(v, (np.integer, np.floating, np.bool_)) else v for k, v in row.items()})
        else:
            clean.append(row)
    return clean


ANSWER_SYSTEM = """You are a senior data analyst for the Quick InSights platform.
You ran a pandas analysis on a real dataset and got actual computed results.
Now present the findings clearly and accurately to the user.

RULES:
- Use the ACTUAL computed data below — do NOT make up or approximate numbers.
- Be specific: include exact values, percentages, counts from the results.
- Use markdown formatting with headers, bold for key numbers, and bullet points.
- If a table was returned, present it in a readable markdown table.
- Keep answers focused and business-relevant.

{chart_rules}

COMPUTED RESULTS:
{results}

If the computation had an error, explain what went wrong in simple terms and suggest a rephrased question."""


def ask_question(question: str, columns_meta: dict, stats: dict, sample_rows: list, df=None) -> dict:
    if df is None:
        return _ask_question_simple(question, columns_meta, stats, sample_rows)

    # Step 1: Generate pandas code
    try:
        code = _generate_analysis_code(question, columns_meta, stats)
        logger.info("Generated analysis code:\n%s", code)
    except Exception as e:
        logger.error("Code generation failed: %s", e)
        return _ask_question_simple(question, columns_meta, stats, sample_rows)

    # Step 2: Execute against real data
    exec_result = _execute_pandas_code(code, df)

    if 'error' in exec_result:
        logger.warning("Code execution failed: %s — retrying with fix", exec_result['error'])
        retry_code = _retry_failed_code(question, columns_meta, stats, code, exec_result['error'])
        if retry_code:
            exec_result = _execute_pandas_code(retry_code, df)

    # Step 3: AI interprets real results
    client = _get_client()
    data_context = _build_data_context(columns_meta, stats, sample_rows)

    results_text = json.dumps(exec_result, default=str, indent=2)[:3000]

    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {
                "role": "system",
                "content": ANSWER_SYSTEM.format(
                    chart_rules=CHART_SPEC_RULES,
                    results=results_text,
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Dataset context:\n{data_context}\n\n"
                    f"Original question: {question}\n\n"
                    "Present the computed results clearly. Include relevant charts."
                ),
            },
        ],
        max_tokens=2000,
        temperature=0.3,
    )

    raw_content = response.choices[0].message.content
    result = _parse_response_with_charts(raw_content)
    result['charts'] = _validate_chart_specs(result['charts'], columns_meta)
    result['computed'] = exec_result
    return result


def _retry_failed_code(question: str, columns_meta: dict, stats: dict,
                       original_code: str, error: str) -> str | None:
    try:
        client = _get_client()
        schema = _build_column_schema(columns_meta)
        shape = stats.get('shape', [0, 0])

        response = client.chat.completions.create(
            model=_get_model(),
            messages=[
                {
                    "role": "system",
                    "content": CODE_GEN_SYSTEM.format(
                        schema=schema, rows=shape[0], cols=shape[1],
                    ),
                },
                {"role": "user", "content": question},
                {"role": "assistant", "content": f"```python\n{original_code}\n```"},
                {
                    "role": "user",
                    "content": (
                        f"The code above raised an error:\n{error}\n\n"
                        "Fix the code. Handle edge cases (NaN, non-numeric columns, empty results). "
                        "Respond ONLY with the corrected ```python code block."
                    ),
                },
            ],
            max_tokens=1500,
            temperature=0.1,
        )

        raw = response.choices[0].message.content.strip()
        if '```python' in raw:
            raw = raw.split('```python', 1)[1].rsplit('```', 1)[0]
        elif '```' in raw:
            raw = raw.split('```', 1)[1].rsplit('```', 1)[0]
        return raw.strip()
    except Exception:
        return None


def _ask_question_simple(question: str, columns_meta: dict, stats: dict, sample_rows: list) -> dict:
    client = _get_client()
    data_context = _build_data_context(columns_meta, stats, sample_rows)

    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior data analyst assistant for the Quick InSights platform. "
                    "Analyze datasets and provide clear, actionable business insights. "
                    "Be specific with numbers. Use markdown formatting.\n\n"
                    "When your analysis benefits from visualization, include chart specs.\n\n"
                    + CHART_SPEC_RULES +
                    "\nProvide both text analysis AND relevant charts."
                ),
            },
            {
                "role": "user",
                "content": f"Dataset context:\n\n{data_context}\n\nQuestion: {question}",
            },
        ],
        max_tokens=2000,
        temperature=0.3,
    )

    raw_content = response.choices[0].message.content
    result = _parse_response_with_charts(raw_content)
    result['charts'] = _validate_chart_specs(result['charts'], columns_meta)
    return result


def generate_insights(columns_meta: dict, stats: dict, sample_rows: list, df=None) -> dict:
    client = _get_client()

    # If we have the real dataframe, compute actual insights
    extra_context = ''
    if df is not None:
        extra_context = _compute_dataset_insights(df, columns_meta)

    data_context = _build_data_context(columns_meta, stats, sample_rows)

    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior data analyst. Analyze this dataset and provide:\n"
                    "1. **Key Findings** — 3-5 most important observations with numbers\n"
                    "2. **Data Quality** — issues and recommendations\n"
                    "3. **Business Questions** — 3 questions this data could answer\n\n"
                    "Use markdown. Include 3-5 charts.\n\n" + CHART_SPEC_RULES
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Analyze this dataset:\n\n{data_context}"
                    + (f"\n\nPre-computed data insights (use these exact numbers):\n{extra_context}" if extra_context else "")
                ),
            },
        ],
        max_tokens=2500,
        temperature=0.4,
    )

    raw_content = response.choices[0].message.content
    result = _parse_response_with_charts(raw_content)
    result['charts'] = _validate_chart_specs(result['charts'], columns_meta)
    return result


def _compute_dataset_insights(df, columns_meta: dict) -> str:
    import pandas as pd
    import numpy as np

    insights = []
    numeric_cols = [c for c, m in columns_meta.items() if m['dtype'] in NUMERIC_DTYPES and c in df.columns]
    categorical_cols = [c for c, m in columns_meta.items() if m['dtype'] not in NUMERIC_DTYPES and c in df.columns]

    if numeric_cols:
        desc = df[numeric_cols].describe().round(4)
        insights.append(f"Numeric summary:\n{desc.to_string()}")

        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr().round(4)
            strong = []
            for i in range(len(corr.columns)):
                for j in range(i + 1, len(corr.columns)):
                    val = corr.iloc[i, j]
                    if abs(val) > 0.5:
                        strong.append(f"  {corr.columns[i]} ↔ {corr.columns[j]}: {val}")
            if strong:
                insights.append(f"Strong correlations (|r| > 0.5):\n" + '\n'.join(strong))

        for col in numeric_cols[:5]:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outlier_count = ((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum()
            if outlier_count > 0:
                insights.append(f"Outliers in {col}: {outlier_count} values ({outlier_count/len(df)*100:.1f}%)")

    for col in categorical_cols[:5]:
        vc = df[col].value_counts().head(5)
        top_vals = ', '.join([f'{k}: {v} ({v/len(df)*100:.1f}%)' for k, v in vc.items()])
        insights.append(f"Top values in {col}: {top_vals}")

    null_cols = [(col, df[col].isna().sum()) for col in df.columns if df[col].isna().sum() > 0]
    if null_cols:
        null_info = ', '.join([f"{col}: {n} ({n/len(df)*100:.1f}%)" for col, n in sorted(null_cols, key=lambda x: -x[1])[:5]])
        insights.append(f"Missing values: {null_info}")

    return '\n\n'.join(insights)


def suggest_charts(columns_meta: dict, stats: dict) -> list:
    client = _get_client()

    cols_info = []
    for col, m in columns_meta.items():
        is_numeric = m['dtype'] in NUMERIC_DTYPES
        cols_info.append({
            'name': col, 'dtype': m['dtype'],
            'is_numeric': is_numeric, 'unique': m['unique_count'],
        })

    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {
                "role": "system",
                "content": (
                    "Suggest charts for a data analytics dashboard.\n\n"
                    "RULES:\n"
                    "- x_column MUST be an exact column name from the list\n"
                    "- y_column MUST be a numeric column (is_numeric=true) or null\n"
                    "- aggregation must be: mean, sum, count, min, max, median — NEVER 'none'\n"
                    "- For categorical x + numeric y: bar/pie with mean/sum\n"
                    "- For numeric without y: histogram with count\n"
                    "- For two numeric columns: scatter\n\n"
                    "Return ONLY a JSON array of 3-6 items. No markdown, no explanation.\n"
                    'Each: {"title":"...","chart_type":"bar|line|pie|scatter|area|histogram|donut|radar",'
                    '"x_column":"exact_name","y_column":"exact_numeric_name" or null,'
                    '"aggregation":"mean|sum|count","reason":"..."}'
                ),
            },
            {
                "role": "user",
                "content": f"Columns:\n{json.dumps(cols_info, indent=2)}\n\nShape: {stats.get('shape', [0, 0])}",
            },
        ],
        max_tokens=1000,
        temperature=0.3,
    )

    try:
        raw = response.choices[0].message.content.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1].rsplit('```', 1)[0].strip()
        suggestions = json.loads(raw)
        return _validate_chart_specs(suggestions, columns_meta)
    except (json.JSONDecodeError, KeyError):
        logger.error("Failed to parse chart suggestions JSON")
        return []


def generate_report_content(columns_meta: dict, stats: dict, sample_rows: list, df=None) -> dict:
    client = _get_client()
    data_context = _build_data_context(columns_meta, stats, sample_rows)

    extra_context = ''
    if df is not None:
        extra_context = _compute_dataset_insights(df, columns_meta)

    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior data analyst creating a comprehensive business report. "
                    "Generate a detailed, professional analysis with these exact sections:\n\n"
                    "## Executive Summary\n"
                    "2-3 paragraphs: what this data is about, key takeaways, overall data health.\n\n"
                    "## Data Profile\n"
                    "Column types, completeness, quality assessment. Use a markdown table.\n\n"
                    "## Statistical Analysis\n"
                    "Key distributions, correlations, outliers. Be specific with numbers.\n\n"
                    "## Key Insights\n"
                    "5-8 numbered, actionable business insights with specific data points.\n\n"
                    "## Recommendations\n"
                    "3-5 data-driven action items.\n\n"
                    "Be specific with numbers and percentages throughout. "
                    "Professional language suitable for business stakeholders.\n\n"
                    "Include 4-6 charts that best illustrate the findings.\n\n"
                    + CHART_SPEC_RULES
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate a comprehensive analysis report:\n\n{data_context}"
                    + (f"\n\nPre-computed data insights (use these exact numbers):\n{extra_context}" if extra_context else "")
                ),
            },
        ],
        max_tokens=4000,
        temperature=0.3,
    )

    raw_content = response.choices[0].message.content
    result = _parse_response_with_charts(raw_content)
    result['charts'] = _validate_chart_specs(result['charts'], columns_meta)
    return result


def _parse_response_with_charts(content: str) -> dict:
    import re
    charts = []
    text_parts = []
    last_end = 0

    for match in re.finditer(r'```chart-json\s*\n?(.*?)\n?```', content, re.DOTALL):
        text_parts.append(content[last_end:match.start()])
        last_end = match.end()
        try:
            chart = json.loads(match.group(1).strip())
            charts.append(chart)
        except json.JSONDecodeError:
            logger.warning("Failed to parse chart JSON from AI response")

    text_parts.append(content[last_end:])
    text = '\n'.join(text_parts).strip()

    return {'text': text, 'charts': charts}
