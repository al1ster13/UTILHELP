import subprocess
import re
import platform


class HardwareDetector:
    @staticmethod
    def get_gpu_info():
        """Получает информацию о GPU через WMIC или PowerShell"""
        try:
            result = subprocess.run([
                'wmic', 'path', 'win32_VideoController', 
                'get', 'name', '/format:list'
            ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)

            if result.returncode == 0:
                gpu_names = []
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('Name=') and line != 'Name=':
                        gpu_name = line.replace('Name=', '').strip()
                        if gpu_name:
                            gpu_names.append(gpu_name)
                
                if gpu_names:
                    return gpu_names
        except FileNotFoundError:
            print("WMIC не найден, пробуем PowerShell...")
        except Exception as e:
            print(f"Ошибка WMIC: {e}")
        
        try:
            ps_command = "Get-CimInstance -ClassName Win32_VideoController | Select-Object -ExpandProperty Name"
            result = subprocess.run([
                'powershell', '-NoProfile', '-Command', ps_command
            ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            
            if result.returncode == 0:
                gpu_names = []
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    gpu_name = line.strip()
                    if gpu_name:
                        gpu_names.append(gpu_name)
                
                return gpu_names
            else:
                print(f"Ошибка PowerShell: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"Ошибка при определении GPU через PowerShell: {e}")
            return []
    
    @staticmethod
    def detect_gpu_vendor():
        gpu_names = GPUDetector.get_gpu_info()
        
        if not gpu_names:
            return 'unknown'
        
        all_gpu_text = ' '.join(gpu_names).lower()
        
        if any(keyword in all_gpu_text for keyword in ['nvidia', 'geforce', 'gtx', 'rtx', 'quadro', 'tesla']):
            return 'nvidia'
        elif any(keyword in all_gpu_text for keyword in ['amd', 'radeon', 'rx ', 'vega', 'navi', 'rdna']):
            return 'amd'
        elif any(keyword in all_gpu_text for keyword in ['intel', 'uhd', 'hd graphics', 'iris', 'xe']):
            return 'intel'
        else:
            return 'unknown'
    
    @staticmethod
    def get_recommendation_text(vendor):
        from localization import t
        recommendations = {
            'nvidia': t('status.recommended'),
            'amd': t('status.recommended'), 
            'intel': t('status.recommended'),
            'unknown': ''
        }
        
        return recommendations.get(vendor, '')
    
    @staticmethod
    def should_show_recommendation(driver_name, user_gpu_vendor):
        if user_gpu_vendor == 'unknown':
            return False
        
        driver_name_lower = driver_name.lower()
        
        cpu_only_keywords = ['ryzen', 'master', 'athlon', 'threadripper']
        is_cpu_only_driver = any(keyword in driver_name_lower for keyword in cpu_only_keywords)
        if is_cpu_only_driver:
            return False
        
        if user_gpu_vendor == 'nvidia' and any(keyword in driver_name_lower for keyword in ['nvidia', 'geforce', 'gtx', 'rtx']):
            return True
        elif user_gpu_vendor == 'amd' and any(keyword in driver_name_lower for keyword in ['amd', 'radeon', 'adrenalin']):
            return True
        elif user_gpu_vendor == 'intel':
            intel_keywords = ['intel']
            has_intel = any(keyword in driver_name_lower for keyword in intel_keywords)
            
            if has_intel:
                gpu_keywords = ['graphics', 'uhd', 'iris', 'xe', 'arc']
                universal_keywords = ['driver & support assistant', 'support assistant']
                
                has_gpu_keywords = any(keyword in driver_name_lower for keyword in gpu_keywords)
                is_universal = any(keyword in driver_name_lower for keyword in universal_keywords)
                
                return has_gpu_keywords or is_universal
        
        return False


class CPUDetector:
    @staticmethod
    def get_cpu_info():
        """Получает информацию о CPU через WMIC или PowerShell"""
        try:
            result = subprocess.run([
                'wmic', 'cpu', 'get', 'name', '/format:list'
            ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
            
            if result.returncode == 0:
                cpu_names = []
                lines = result.stdout.strip().split('\n')
                
                for line in lines:
                    if line.startswith('Name=') and line != 'Name=':
                        cpu_name = line.replace('Name=', '').strip()
                        if cpu_name:
                            cpu_names.append(cpu_name)
                
                if cpu_names:
                    return cpu_names
        except FileNotFoundError:
            print("WMIC не найден, пробуем PowerShell...")
        except Exception as e:
            print(f"Ошибка WMIC для CPU: {e}")
        
        try:
            ps_command = "Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty Name"
            result = subprocess.run([
                'powershell', '-NoProfile', '-Command', ps_command
            ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            
            if result.returncode == 0:
                cpu_names = []
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    cpu_name = line.strip()
                    if cpu_name:
                        cpu_names.append(cpu_name)
                
                return cpu_names
            else:
                print(f"Ошибка PowerShell для CPU: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"Ошибка при определении CPU через PowerShell: {e}")
            return []
    
    @staticmethod
    def detect_cpu_vendor():
        cpu_names = CPUDetector.get_cpu_info()
        
        if not cpu_names:
            return 'unknown'
        
        all_cpu_text = ' '.join(cpu_names).lower()
        
        if any(keyword in all_cpu_text for keyword in ['intel', 'core i', 'pentium', 'celeron', 'xeon']):
            return 'intel'
        elif any(keyword in all_cpu_text for keyword in ['amd', 'ryzen', 'athlon', 'fx-', 'threadripper', 'epyc']):
            return 'amd'
        else:
            return 'unknown'
    
    @staticmethod
    def should_show_cpu_recommendation(driver_name, user_cpu_vendor):
        if user_cpu_vendor == 'unknown':
            return False
        
        driver_name_lower = driver_name.lower()
        
        if user_cpu_vendor == 'intel':
            cpu_keywords = ['cpu', 'processor', 'процессор', 'chipset', 'чипсет']
            intel_keywords = ['intel', 'core', 'pentium', 'celeron']
            universal_intel = ['driver & support assistant', 'support assistant', 'intel software']
            
            has_intel = any(keyword in driver_name_lower for keyword in intel_keywords)
            has_cpu_keywords = any(keyword in driver_name_lower for keyword in cpu_keywords)
            is_universal_intel = any(keyword in driver_name_lower for keyword in universal_intel)
            
            gpu_only_keywords = ['graphics', 'uhd', 'iris', 'xe', 'arc']
            is_gpu_only = any(keyword in driver_name_lower for keyword in gpu_only_keywords) and not has_cpu_keywords
            
            return has_intel and (has_cpu_keywords or is_universal_intel) and not is_gpu_only
            
        elif user_cpu_vendor == 'amd':
            cpu_keywords = ['cpu', 'processor', 'процессор', 'chipset', 'чипсет', 'ryzen', 'master', 'athlon', 'threadripper']
            amd_keywords = ['amd', 'ryzen', 'athlon', 'threadripper']
            
            has_amd = any(keyword in driver_name_lower for keyword in amd_keywords)
            has_cpu_keywords = any(keyword in driver_name_lower for keyword in cpu_keywords)
            
            gpu_keywords = ['radeon', 'adrenalin', 'graphics']
            is_gpu_driver = any(keyword in driver_name_lower for keyword in gpu_keywords)
            
            return has_amd and has_cpu_keywords and not is_gpu_driver
        
        return False


class GPUDetector(HardwareDetector):
    pass


if __name__ == "__main__":
    gpu_detector = GPUDetector()
    cpu_detector = CPUDetector()
    
    print("=== GPU ИНФОРМАЦИЯ ===")
    gpu_list = gpu_detector.get_gpu_info()
    for gpu in gpu_list:
        print(f"  - {gpu}")
    
    gpu_vendor = gpu_detector.detect_gpu_vendor()
    print(f"Производитель GPU: {gpu_vendor}")
    
    print("\n=== CPU ИНФОРМАЦИЯ ===")
    cpu_list = cpu_detector.get_cpu_info()
    for cpu in cpu_list:
        print(f"  - {cpu}")
    
    cpu_vendor = cpu_detector.detect_cpu_vendor()
    print(f"Производитель CPU: {cpu_vendor}")
    
    print(f"\n=== РЕКОМЕНДАЦИИ ===")
    if gpu_vendor != 'unknown':
        gpu_recommendation = gpu_detector.get_recommendation_text(gpu_vendor)
        print(f"GPU рекомендация: {gpu_recommendation}")
    
    print(f"CPU рекомендация: {cpu_vendor}")