import os
import shutil
import sys

def reorganize_build():
    print("=== BUILD STRUCTURE REORGANIZATION ===")
    
    # We are already in the project root thanks to the bat file
    
    dist_path = "dist/UTILHELP"
    internal_path = os.path.join(dist_path, "_internal")
    
    if not os.path.exists(dist_path):
        print(f"❌ Folder {dist_path} not found!")
        print("First run build: python -m PyInstaller build_scripts_git/utilhelp_structured.spec")
        return False
    
    if not os.path.exists(internal_path):
        print(f"❌ _internal folder not found!")
        return False
    
    print(f"📁 Working with: {dist_path}")
    
    folders_to_move = ["assets", "data", "docs", "bat"]
    
    print("\n1. Moving folders from _internal to root:")
    
    for folder in folders_to_move:
        source_path = os.path.join(internal_path, folder)
        target_path = os.path.join(dist_path, folder)
        
        if os.path.exists(source_path):
            try:
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                    print(f"   🗑️  Removed old folder: {folder}/")
                
                shutil.move(source_path, target_path)
                print(f"   ✅ Moved folder: {folder}/")
                
            except Exception as e:
                print(f"   ❌ Error moving {folder}: {e}")
        else:
            print(f"   ⚠️  Folder {folder} not found in _internal")
    
    print("\n2. Moving individual files:")
    
    files_to_move = ["LICENSE"]  
    
    for file in files_to_move:
        source_path = os.path.join(internal_path, file)
        target_path = os.path.join(dist_path, file)
        
        if os.path.exists(source_path):
            try:
                if os.path.exists(target_path):
                    os.remove(target_path)
                
                shutil.move(source_path, target_path)
                print(f"   ✅ Moved file: {file}")
                
            except Exception as e:
                print(f"   ❌ Error moving {file}: {e}")
    
    print("\n3. Checking final structure:")
    
    items_in_root = os.listdir(dist_path)
    
    expected_folders = ["assets", "data", "docs", "bat", "_internal"]
    expected_files = ["UTILHELP.exe", "LICENSE"]
    
    print("   Folders in root:")
    for folder in expected_folders:
        if folder in items_in_root and os.path.isdir(os.path.join(dist_path, folder)):
            print(f"     ✅ {folder}/")
            
            if folder == "bat":
                bat_files = os.listdir(os.path.join(dist_path, folder))
                print(f"        Contents: {bat_files}")
            elif folder == "assets":
                assets_subfolders = os.listdir(os.path.join(dist_path, folder))
                print(f"        Subfolders: {assets_subfolders}")
            elif folder == "data":
                data_files = [f for f in os.listdir(os.path.join(dist_path, folder)) if f.endswith('.db')]
                print(f"        Databases: {data_files}")
        else:
            print(f"     ❌ {folder}/ - NOT FOUND")
    
    print("   Files in root:")
    for file in expected_files:
        if file in items_in_root and os.path.isfile(os.path.join(dist_path, file)):
            print(f"     ✅ {file}")
        else:
            print(f"     ❌ {file} - NOT FOUND")
    
    print(f"\n=== REORGANIZATION COMPLETED ===")
    return True

if __name__ == "__main__":
    success = reorganize_build()
    if not success:
        sys.exit(1)