import os
import pandas as pd

def get_file_shape(cache_dir='./cache'):
    file_shapes = {}
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            if file.endswith('.pkl'):
                file_path = os.path.join(root, file)
                try:
                    data = pd.read_pickle(file_path)
                    file_shapes[file] = data.shape
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
    return file_shapes

def main():
    cache_dir = './cache'
    file_shapes = get_file_shape(cache_dir)
    for file, shape in file_shapes.items():
        print(f"{file}: {shape[0]} rows, {shape[1]} columns")

if __name__ == '__main__':
    main()
