import pandas as pd

def query_signal(file_path='./cache/1h_extended.pkl', threshold=10):
    try:
        # Load the extended data
        data = pd.read_pickle(file_path)
        
        # Filter rows where SIGNAL <= threshold
        filtered_data = data[data['SIGNAL'] <= threshold]
        
        return filtered_data
    except Exception as e:
        print(f"Error reading or processing {file_path}: {e}")
        return pd.DataFrame()

def generate_stats(data):
    stats = {}

    print(data.head(20))
    
    for column in data.columns:
        if column == 'Ticker':
            continue
        col_data = data[column]
        stats[column] = {
            'mean': col_data.mean(),
            'std': col_data.std(),
            'min': col_data.min(),
            'max': col_data.max(),
            '25%': col_data.quantile(0.25),
            '50% (median)': col_data.median(),
            '75%': col_data.quantile(0.75),
            'missing': col_data.isnull().sum()
        }
    
    return pd.DataFrame(stats)

def main():
    file_path = './cache/1h_extended.pkl'
    threshold = 10
    filtered_data = query_signal(file_path, threshold)
    
    if not filtered_data.empty:
        stats = generate_stats(filtered_data)
        print(stats)
    else:
        print("No data found matching the criteria.")

if __name__ == '__main__':
    main()
