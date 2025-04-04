# FireDucks Performance Benchmarking

A comprehensive performance comparison between popular data processing frameworks: Pandas, Polars, and FireDucks. This project provides detailed benchmarks for common data operations across these frameworks, helping developers make informed decisions about which framework best suits their needs.

## Overview

This project benchmarks three popular data processing frameworks:
- **Pandas**: The widely-used data manipulation library for Python
- **Polars**: A lightning-fast DataFrames library written in Rust
- **FireDucks**: A new data processing framework built on TFRT

The benchmarks are run on a dataset of 1,000,000 rows with various data types including numeric, categorical, and timestamp data.

## Benchmark Results

### Simple GroupBy Operation
Aggregating mean values by category:
- **Polars**: 0.015s (fastest)
- **Pandas**: 0.058s (3.8x slower)
- **FireDucks**: 0.082s (5.4x slower)

Memory Usage:
- Pandas: 8.8MB
- Polars: 24.4MB
- FireDucks: ~0MB

### Complex GroupBy Operation
Aggregating multiple statistics (mean, std, count) by category and text:
- **Polars**: 0.033s (fastest)
- **Pandas**: 0.124s (3.7x slower)
- **FireDucks**: 0.480s (14.4x slower)

Memory Usage:
- Pandas: -7.3MB (memory efficient due to in-place operations)
- Polars: 16.7MB
- FireDucks: 11.7MB

### Sorting Operation
Sorting by multiple columns:
- **Polars**: 0.162s (fastest)
- **Pandas**: 0.424s (2.6x slower)
- **FireDucks**: 0.933s (5.8x slower)

Memory Usage:
- Pandas: 65.6MB
- Polars: 104.4MB
- FireDucks: 45.7MB

### Filtering with Computation
Complex filtering with mean comparison:
- **Polars**: 0.018s (fastest)
- **Pandas**: 0.050s (2.9x slower)
- **FireDucks**: 0.088s (5.0x slower)

Memory Usage:
- Pandas: 34.8MB
- Polars: 1.5MB
- FireDucks: 25.2MB

## Analysis

### Performance Characteristics

1. **Polars** consistently outperforms both Pandas and FireDucks across all operations:
   - 2.6x to 3.8x faster than Pandas
   - 5.0x to 14.4x faster than FireDucks
   - Particularly efficient in groupby and filtering operations

2. **Pandas** shows:
   - Consistent middle-ground performance
   - Good memory efficiency in groupby operations
   - Competitive performance in simple operations
   - Higher memory usage in sorting operations

3. **FireDucks** demonstrates:
   - Generally higher execution times
   - Competitive memory usage in simple operations
   - Room for optimization in complex operations
   - Best memory efficiency in simple groupby operations

### Key Findings

1. **Operation Complexity Impact**:
   - Simple operations show smaller performance gaps
   - Complex operations amplify the differences between frameworks
   - Memory usage varies significantly based on operation type

2. **Memory vs Speed Tradeoffs**:
   - Polars: Prioritizes speed with higher memory usage in some operations
   - Pandas: Balanced approach with moderate memory usage
   - FireDucks: Memory efficient in simple operations but at the cost of speed

3. **Best Use Cases**:
   - **Polars**: Best for performance-critical applications with sufficient memory
   - **Pandas**: Good for general-purpose data analysis with moderate dataset sizes
   - **FireDucks**: Suitable for memory-constrained environments with simple operations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the performance comparison:
```bash
python performance_comparison.py
```

Run the basic FireDucks test:
```bash
python fireducks_basic_test.py
```

## Technical Details

The benchmarks are conducted with the following specifications:
- Dataset Size: 1,000,000 rows
- Data Types: Numeric, Categorical, Timestamp
- Operations: GroupBy, Sort, Filter, Column Creation
- Metrics: Execution Time, Memory Usage
- Each operation is run multiple times to ensure reliable results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Pandas development team
- Polars development team
- FireDucks development team