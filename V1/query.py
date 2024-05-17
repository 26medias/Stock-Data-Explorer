import os
import pandas as pd
import traceback
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from DataFetcher import DataFetcher
from DataLoader import DataLoader
from MarketCycleExtender import MarketCycleExtender

def process_file(file, fetcher, loader):
    ticker = file.split('.')[0]
    try:
        # Load the data from the cache
        cache_file = os.path.join('./cache', file)
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                data = pd.read_pickle(f)
            print(f"Successfully loaded {ticker} from cache.")
        else:
            raise FileNotFoundError(f"Cache file for {ticker} not found.")
        
        # Ensure data is not empty
        if data.empty:
            raise ValueError(f"Data for {ticker} is empty.")
        
        # Apply transformations
        data = loader.load_data(ticker)
        if data is None or data.empty:
            raise ValueError(f"Transformed data for {ticker} is empty or None.")
        data['Ticker'] = ticker
        print(ticker, len(data))
        return data
    except Exception as exc:
        print(f'Error processing file {file} for ticker {ticker}: {exc}')
        print(traceback.format_exc())
        return None

def main(use_cache_only=True):
    fetcher = DataFetcher(use_cache_only=True)
    loader = DataLoader(fetcher, extender_class=MarketCycleExtender)
    cache_dir = './cache'
    all_data = []

    # Get list of all pkl files in the cache directory
    files = [file for file in os.listdir(cache_dir) if file.endswith('.pkl')]

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_file, file, fetcher, loader): file for file in files}

        # Use tqdm to show progress
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing cached stock data"):
            try:
                data = future.result()
                if data is not None:
                    all_data.append(data)
            except Exception as exc:
                print(f'File {futures[future]} generated an exception: {exc}')
                print(traceback.format_exc())

    # Consolidate all transformed data into a single DataFrame
    if all_data:
        consolidated_data = pd.concat(all_data, ignore_index=True)

        # Save the consolidated DataFrame to a pickle file
        consolidated_data.to_pickle('./consolidated_data.pkl')
        print("Data has been consolidated and saved.")
    else:
        print("No data to consolidate.")

if __name__ == '__main__':
    main()
