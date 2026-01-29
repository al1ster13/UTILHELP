import os
import shutil
import sys

def reorganize_build():
    print("=== РЕОРГАНИЗАЦИЯ СТРУКТУРЫ СБОРКИ ===")
    
    # Мы уже в корневой папке проекта благодаря bat файлу
    
    dist_path = "dist/UTILHELP"
    internal_path = os.path.join(dist_path, "_internal")
    
    if not os.path.exists(dist_path):
        print(f"❌ Папка {dist_path} не найдена!")
        print("Сначала выполните сборку: python -m PyInstaller build_scripts/utilhelp_structured.spec")
        return False
    
    if not os.path.exists(internal_path):
        print(f"❌ Папка _internal не найдена!")
        return False
    
    print(f"📁 Работаем с: {dist_path}")
    
    folders_to_move = ["assets", "data", "docs", "bat"]
    
    print("\n1. Перемещение папок из _internal в корень:")
    
    for folder in folders_to_move:
        source_path = os.path.join(internal_path, folder)
        target_path = os.path.join(dist_path, folder)
        
        if os.path.exists(source_path):
            try:
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                    print(f"   🗑️  Удалена старая папка: {folder}/")
                
                shutil.move(source_path, target_path)
                print(f"   ✅ Перемещена папка: {folder}/")
                
            except Exception as e:
                print(f"   ❌ Ошибка перемещения {folder}: {e}")
        else:
            print(f"   ⚠️  Папка {folder} не найдена в _internal")
    
    print("\n2. Перемещение отдельных файлов:")
    
    files_to_move = ["LICENSE"]  
    
    for file in files_to_move:
        source_path = os.path.join(internal_path, file)
        target_path = os.path.join(dist_path, file)
        
        if os.path.exists(source_path):
            try:
                if os.path.exists(target_path):
                    os.remove(target_path)
                
                shutil.move(source_path, target_path)
                print(f"   ✅ Перемещен файл: {file}")
                
            except Exception as e:
                print(f"   ❌ Ошибка перемещения {file}: {e}")
    
    print("\n3. Проверка итоговой структуры:")
    
    items_in_root = os.listdir(dist_path)
    
    expected_folders = ["assets", "data", "docs", "bat", "_internal"]
    expected_files = ["UTILHELP.exe", "LICENSE"]
    
    print("   Папки в корне:")
    for folder in expected_folders:
        if folder in items_in_root and os.path.isdir(os.path.join(dist_path, folder)):
            print(f"     ✅ {folder}/")
            
            if folder == "bat":
                bat_files = os.listdir(os.path.join(dist_path, folder))
                print(f"        Содержимое: {bat_files}")
            elif folder == "assets":
                assets_subfolders = os.listdir(os.path.join(dist_path, folder))
                print(f"        Подпапки: {assets_subfolders}")
            elif folder == "data":
                data_files = [f for f in os.listdir(os.path.join(dist_path, folder)) if f.endswith('.db')]
                print(f"        Базы данных: {data_files}")
        else:
            print(f"     ❌ {folder}/ - НЕ НАЙДЕНА")
    
    print("   Файлы в корне:")
    for file in expected_files:
        if file in items_in_root and os.path.isfile(os.path.join(dist_path, file)):
            print(f"     ✅ {file}")
        else:
            print(f"     ❌ {file} - НЕ НАЙДЕН")
    
    print(f"\n=== РЕОРГАНИЗАЦИЯ ЗАВЕРШЕНА ===")
    return True

if __name__ == "__main__":
    success = reorganize_build()
    if not success:
        sys.exit(1)