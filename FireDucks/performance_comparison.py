import pandas as pd
import time
import numpy as np
import polars as pl
import fireducks as fd
from fireducks.fireducks_ext import FireDucksContext
from fireducks.core import get_fireducks_options, set_fireducks_option
import psutil
import gc
from typing import Callable, Dict, Any
import statistics

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def benchmark_operation(operation: Callable, name: str, num_runs: int = 3) -> Dict[str, Any]:
    """Run an operation multiple times and collect metrics."""
    gc.collect()  # Clear any garbage before starting
    initial_memory = get_memory_usage()
    times = []
    
    for _ in range(num_runs):
        start_time = time.time()
        result = operation()
        times.append(time.time() - start_time)
    
    final_memory = get_memory_usage()
    
    return {
        'mean_time': statistics.mean(times),
        'std_time': statistics.stdev(times) if len(times) > 1 else 0,
        'memory_delta': final_memory - initial_memory,
        'name': name
    }

def format_metrics(metrics: Dict[str, Any]) -> str:
    """Format metrics into a readable string."""
    return (f"{metrics['name']}: {metrics['mean_time']:.3f}s ± {metrics['std_time']:.3f}s, "
            f"Memory: {metrics['memory_delta']:.1f}MB")

# Enable FireDucks benchmark mode
get_fireducks_options().set_benchmark_mode(True)
set_fireducks_option("fireducks-version", True)

# Create sample data
size = 1000000
data = {
    'id': range(size),
    'value': np.random.rand(size),
    'category': np.random.choice(['A', 'B', 'C'], size),
    'timestamp': pd.date_range('2024-01-01', periods=size, freq='s'),
    'text': np.random.choice(['foo', 'bar', 'baz', 'qux'], size)
}

print("Testing performance across Pandas, Polars, and FireDucks...")
print(f"Dataset size: {size:,} rows")
print("\nInitializing frameworks...")

# Initialize frameworks
pd_df = pd.DataFrame(data)
pl_df = pl.DataFrame(data)
fd_context = FireDucksContext()
fd_data = {k: np.array(v) if not isinstance(v, pd.DatetimeIndex) else np.array(v.astype(np.int64)) 
          for k, v in data.items()}

frameworks = {
    'Pandas': {'df': pd_df, 'name': 'Pandas'},
    'Polars': {'df': pl_df, 'name': 'Polars'},
    'FireDucks': {'df': fd_data, 'name': 'FireDucks'}
}

# Define operations for each framework
operations = {
    'Simple GroupBy': {
        'Pandas': lambda: pd_df.groupby('category')['value'].mean(),
        'Polars': lambda: pl_df.group_by('category').agg(pl.col('value').mean()),
        'FireDucks': lambda: {cat: np.mean(fd_data['value'][fd_data['category'] == cat]) 
                            for cat in np.unique(fd_data['category'])}
    },
    'Complex GroupBy': {
        'Pandas': lambda: pd_df.groupby(['category', 'text'])
                              .agg({'value': ['mean', 'std', 'count']}),
        'Polars': lambda: pl_df.group_by(['category', 'text'])
                              .agg([
                                  pl.col('value').mean().alias('value_mean'),
                                  pl.col('value').std().alias('value_std'),
                                  pl.col('value').count().alias('value_count')
                              ]),
        'FireDucks': lambda: {
            (cat, txt): {
                'mean': np.mean(fd_data['value'][mask]),
                'std': np.std(fd_data['value'][mask]),
                'count': np.sum(mask)
            }
            for cat in np.unique(fd_data['category'])
            for txt in np.unique(fd_data['text'])
            if (mask := (fd_data['category'] == cat) & (fd_data['text'] == txt)).any()
        }
    },
    'Sort': {
        'Pandas': lambda: pd_df.sort_values(['value', 'category']),
        'Polars': lambda: pl_df.sort(['value', 'category']),
        'FireDucks': lambda: {
            k: v[np.lexsort((fd_data['category'], fd_data['value']))]
            for k, v in fd_data.items()
        }
    },
    'Filter with Computation': {
        'Pandas': lambda: pd_df[
            (pd_df['value'] > pd_df['value'].mean()) & 
            (pd_df['category'].isin(['A', 'B']))
        ],
        'Polars': lambda: pl_df.filter(
            (pl.col('value') > pl.col('value').mean()) & 
            pl.col('category').is_in(['A', 'B'])
        ),
        'FireDucks': lambda: {
            k: v[value_mask & category_mask] 
            for k, v in fd_data.items()
            if (value_mask := fd_data['value'] > np.mean(fd_data['value'])) is not None
            and (category_mask := np.isin(fd_data['category'], ['A', 'B'])) is not None
        }
    }
}

# Run benchmarks
results = {}
for op_name, op_dict in operations.items():
    print(f"\n{op_name} Operation:")
    op_results = {}
    for framework, op in op_dict.items():
        metrics = benchmark_operation(op, framework)
        print(f"  {format_metrics(metrics)}")
        op_results[framework] = metrics
    results[op_name] = op_results

# Print summary
print("\nSummary of Results:")
for op_name, op_results in results.items():
    print(f"\n{op_name}:")
    sorted_results = sorted(op_results.items(), key=lambda x: x[1]['mean_time'])
    fastest = sorted_results[0][0]
    fastest_time = sorted_results[0][1]['mean_time']
    
    for framework, metrics in sorted_results:
        speedup = metrics['mean_time'] / fastest_time
        print(f"  {framework}: {metrics['mean_time']:.3f}s " + 
              f"({'fastest' if framework == fastest else f'{speedup:.1f}x slower'})")