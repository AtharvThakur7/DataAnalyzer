import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def read_file_to_dataframe(file_path: str, file_type: str) -> pd.DataFrame:
    if file_type == 'csv':
        return pd.read_csv(file_path)
    return pd.read_excel(file_path)


def extract_column_metadata(df: pd.DataFrame) -> dict:
    meta = {}
    for col in df.columns:
        col_data = df[col]
        info = {
            'dtype': str(col_data.dtype),
            'null_count': int(col_data.isnull().sum()),
            'null_pct': round(float(col_data.isnull().mean() * 100), 2),
            'unique_count': int(col_data.nunique()),
            'sample_values': [str(v) for v in col_data.dropna().head(5).tolist()],
        }
        if pd.api.types.is_numeric_dtype(col_data):
            desc = col_data.describe()
            info.update({
                'mean': round(float(desc.get('mean', 0)), 4),
                'std': round(float(desc.get('std', 0)), 4),
                'min': float(desc.get('min', 0)),
                'max': float(desc.get('max', 0)),
                'q25': float(desc.get('25%', 0)),
                'q50': float(desc.get('50%', 0)),
                'q75': float(desc.get('75%', 0)),
            })
        meta[col] = info
    return meta


def compute_dataset_stats(df: pd.DataFrame) -> dict:
    stats = {
        'shape': list(df.shape),
        'total_nulls': int(df.isnull().sum().sum()),
        'total_duplicates': int(df.duplicated().sum()),
        'memory_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        'dtypes': df.dtypes.astype(str).value_counts().to_dict(),
        'numeric_columns': df.select_dtypes(include='number').columns.tolist(),
        'categorical_columns': df.select_dtypes(include='object').columns.tolist(),
        'datetime_columns': df.select_dtypes(include='datetime').columns.tolist(),
    }

    numeric_df = df.select_dtypes(include='number')
    if not numeric_df.empty and len(numeric_df.columns) > 1:
        corr = numeric_df.corr()
        high_corr = []
        for i in range(len(corr.columns)):
            for j in range(i + 1, len(corr.columns)):
                val = corr.iloc[i, j]
                if abs(val) > 0.7:
                    high_corr.append({
                        'col1': corr.columns[i],
                        'col2': corr.columns[j],
                        'value': round(float(val), 4),
                    })
        stats['high_correlations'] = high_corr

    return stats


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    report = {'steps': [], 'rows_before': len(df), 'cols_before': len(df.columns)}

    threshold = len(df) * 0.5
    cols_before = len(df.columns)
    df = df.dropna(thresh=threshold, axis=1)
    dropped_cols = cols_before - len(df.columns)
    if dropped_cols:
        report['steps'].append(f'Dropped {dropped_cols} columns with >50% missing values')

    for col in df.select_dtypes(include='number').columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            skewness = df[col].skew()
            if abs(skewness) > 1:
                df[col] = df[col].fillna(df[col].median())
                report['steps'].append(f'{col}: filled {null_count} nulls with median (skewed)')
            else:
                df[col] = df[col].fillna(df[col].mean())
                report['steps'].append(f'{col}: filled {null_count} nulls with mean')

            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outliers = ((df[col] < lower) | (df[col] > upper)).sum()
            if outliers > 0:
                df[col] = np.clip(df[col], lower, upper)
                report['steps'].append(f'{col}: capped {outliers} outliers')

    dupes = df.duplicated().sum()
    if dupes:
        df = df.drop_duplicates()
        report['steps'].append(f'Removed {dupes} duplicate rows')

    report['rows_after'] = len(df)
    report['cols_after'] = len(df.columns)
    return df, report


def get_data_page(df: pd.DataFrame, page: int = 1, page_size: int = 50) -> dict:
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]

    return {
        'columns': df.columns.tolist(),
        'rows': page_df.values.tolist(),
        'total_rows': len(df),
        'page': page,
        'page_size': page_size,
        'total_pages': max(1, -(-len(df) // page_size)),
    }
