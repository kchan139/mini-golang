import os
from datetime import datetime

# List of directories to scan - MODIFY THESE PATHS AS NEEDED
DIRECTORIES_TO_SCAN = [
    "MiniGo/src/main/minigo/codegen",
    "MiniGo/src/main/minigo/utils",
    "MiniGo/src/test/solutions",
]

# Output file path
OUTPUT_FILE = "file_ingest.txt"

def scan_files(directories, output_file=OUTPUT_FILE):
    """
    Scan specified directories and write the contents of all files to a text file.
    
    Args:
        directories (list): List of directory paths to scan
        output_file (str): Path to the output text file
    """
    with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
        f.write(f"File Contents Scan - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        # f.write(f"{'=' * 50}\n\n")
        
        for directory in directories:
            if not os.path.exists(directory):
                print(f"ERROR: Directory '{directory}' does not exist.")
                continue
                
            if not os.path.isdir(directory):
                print(f"ERROR: '{directory}' is not a directory.")
                continue
                
            f.write(f"Scanning files in: {os.path.abspath(directory)}\n")
            # f.write(f"{'-' * 50}\n\n")
            
            # Scan all subdirectories recursively
            for root, dirs, files in os.walk(directory):
                for file in sorted(files):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory)
                    
                    # Skip binary files and very large files
                    if is_binary_file(file_path) or os.path.getsize(file_path) > 1024 * 1024:  # Skip files > 1MB
                        continue
                    
                    f.write(f"FILE: {rel_path}\n")
                    # f.write(f"{'-' * 50}\n")
                    
                    try:
                        # Try to read the file content
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as file_handle:
                            content = file_handle.read()
                            f.write(content)
                    except Exception as e:
                        print(f"[ERROR READING FILE: {str(e)}]")
                    
                    f.write("\n")
    
    print(f"File contents scan complete. Results saved to {os.path.abspath(output_file)}")

def is_binary_file(file_path):
    """
    Check if a file is binary by reading a small chunk and looking for null bytes.
    """
    try:
        chunk_size = 1024
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            if b'\x00' in chunk:  # Check for null bytes
                return True
            
            # Additional binary detection heuristic
            text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
            return bool(chunk.translate(None, text_chars))
    except Exception:
        return True  # Consider files we can't read as binary

if __name__ == "__main__":
    scan_files(DIRECTORIES_TO_SCAN)