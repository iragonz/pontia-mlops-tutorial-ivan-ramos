import urllib.request
from pathlib import Path

def download_data():
    """Download Adult Income dataset from UCI repository"""
    
    # URLs del dataset
    data_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
    test_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.test"
    
    # Crear directorio si no existe
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Descargar archivos
    print("Downloading adult.data...")
    urllib.request.urlretrieve(data_url, data_dir / "adult.data")
    print("Downloaded adult.data")
    
    print("Downloading adult.test...")
    urllib.request.urlretrieve(test_url, data_dir / "adult.test")
    print("Downloaded adult.test")
    
    print("Dataset downloaded successfully!")

if __name__ == "__main__":
    download_data()