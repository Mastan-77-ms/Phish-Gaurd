"""
PhishGuard System Verification Script
Checks if all components are properly installed and configured
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check Python version"""
    print("\n[CHECK] Python Version")
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("  ✓ Python version OK (3.8+)")
        return True
    else:
        print("  ✗ Python version too old (need 3.8+)")
        return False

def check_python_packages():
    """Check required Python packages"""
    print("\n[CHECK] Python Packages")
    
    packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'tensorflow': 'TensorFlow',
        'keras': 'Keras',
        'sklearn': 'Scikit-learn',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'joblib': 'Joblib',
        'requests': 'Requests'
    }
    
    all_ok = True
    for import_name, display_name in packages.items():
        try:
            __import__(import_name)
            print(f"  ✓ {display_name}")
        except ImportError:
            print(f"  ✗ {display_name} - MISSING")
            all_ok = False
    
    return all_ok

def check_files_exist():
    """Check if required files exist"""
    print("\n[CHECK] Required Files")
    
    required_files = {
        'ml_server/ml_server/app.py': 'ML Server',
        'ml_server/ml_server/deep_learning_model.py': 'DL Model',
        'ml_server/ml_server/train_dl_model.py': 'Training Script',
        'backend/backend/server.js': 'Backend Server',
        'backend/backend/db.js': 'Database Config',
        'frontend/phish-app2/src/App.jsx': 'Frontend App',
        'ml_server/ml_server/requirements.txt': 'ML Requirements'
    }
    
    all_ok = True
    for file_path, display_name in required_files.items():
        if os.path.exists(file_path):
            print(f"  ✓ {display_name}")
        else:
            print(f"  ✗ {display_name} - NOT FOUND ({file_path})")
            all_ok = False
    
    return all_ok

def check_model_files():
    """Check if trained model files exist"""
    print("\n[CHECK] Trained Model Files")
    
    model_file = 'ml_server/ml_server/phishing_dl_model.h5'
    scaler_file = 'ml_server/ml_server/feature_scaler.pkl'
    
    model_ok = os.path.exists(model_file)
    scaler_ok = os.path.exists(scaler_file)
    
    print(f"  {'✓' if model_ok else '✗'} Deep Learning Model (phishing_dl_model.h5)")
    print(f"  {'✓' if scaler_ok else '✗'} Feature Scaler (feature_scaler.pkl)")
    
    if not (model_ok and scaler_ok):
        print("\n  ⚠ Models not trained yet!")
        print("  Run: python train_dl_model.py")
        return False
    
    return True

def check_node_version():
    """Check Node.js version"""
    print("\n[CHECK] Node.js Version")
    
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"  {version}")
        
        # Extract version number
        major_version = int(version.split('.')[0][1:])
        if major_version >= 16:
            print("  ✓ Node version OK (16+)")
            return True
        else:
            print("  ✗ Node version too old (need 16+)")
            return False
    except:
        print("  ✗ Node.js not found or not in PATH")
        return False

def check_node_packages():
    """Check Node.js packages"""
    print("\n[CHECK] Node.js Packages")
    
    dirs_to_check = [
        ('backend/backend', 'Backend'),
        ('frontend/phish-app2', 'Frontend')
    ]
    
    all_ok = True
    for dir_path, display_name in dirs_to_check:
        node_modules = os.path.join(dir_path, 'node_modules')
        if os.path.exists(node_modules):
            print(f"  ✓ {display_name} packages installed")
        else:
            print(f"  ✗ {display_name} packages not installed")
            print(f"    Run: cd {dir_path} && npm install")
            all_ok = False
    
    return all_ok

def check_ml_server_import():
    """Check if ML server can be imported"""
    print("\n[CHECK] ML Server Import")
    
    try:
        # Change to ML server directory
        original_dir = os.getcwd()
        os.chdir('ml_server/ml_server')
        
        # Try importing the main components
        try:
            from deep_learning_model import PhishingDeepLearningModel
            print("  ✓ Deep Learning Model imports OK")
        except Exception as e:
            print(f"  ✗ Deep Learning Model import failed: {e}")
        
        os.chdir(original_dir)
        return True
    except Exception as e:
        print(f"  ✗ Error checking imports: {e}")
        return False

def check_connectivity():
    """Check if services are running"""
    print("\n[CHECK] Service Connectivity")
    
    import socket
    
    services = {
        'localhost:8000': 'ML Server',
        'localhost:3000': 'Backend',
        'localhost:5173': 'Frontend'
    }
    
    any_running = False
    for service, name in services.items():
        host, port = service.split(':')
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            
            if result == 0:
                print(f"  ✓ {name} is running ({service})")
                any_running = True
            else:
                print(f"  ✗ {name} is not running ({service})")
        except:
            print(f"  ✗ {name} check failed ({service})")
    
    return any_running

def print_report(results):
    """Print verification report"""
    print("\n" + "="*70)
    print("  PHISHGUARD SYSTEM VERIFICATION REPORT")
    print("="*70)
    
    checks = [
        ("Python Version", results.get('python_version', False)),
        ("Python Packages", results.get('python_packages', False)),
        ("Required Files", results.get('files', False)),
        ("Model Files", results.get('models', False)),
        ("Node.js Version", results.get('node_version', False)),
        ("Node.js Packages", results.get('node_packages', False)),
        ("ML Server Import", results.get('ml_import', False)),
        ("Service Connectivity", results.get('connectivity', False))
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    print(f"\nResults: {passed}/{total} checks passed")
    print("\nDetailed Results:")
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {check_name}")
    
    if passed == total:
        print("\n✓ All checks passed! System is ready to use.")
        print("\nQuick Start:")
        print("  1. python train_dl_model.py (if not already done)")
        print("  2. python app.py (ML Server)")
        print("  3. npm start (Backend - in backend/backend)")
        print("  4. npm run dev (Frontend - in frontend/phish-app2)")
    elif passed >= 6:
        print("\n⚠ Most checks passed, but some issues remain.")
        print("  See above for details on what needs to be fixed.")
    else:
        print("\n✗ Several checks failed. Review errors above.")
        print("  Follow the Quick Start Guide for setup instructions.")
    
    print("\n" + "="*70 + "\n")

def main():
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║        PhishGuard - System Verification Script                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    print("\nRunning system checks...\n")
    
    results = {
        'python_version': check_python_version(),
        'python_packages': check_python_packages(),
        'files': check_files_exist(),
        'models': check_model_files(),
        'node_version': check_node_version(),
        'node_packages': check_node_packages(),
        'ml_import': check_ml_server_import(),
        'connectivity': check_connectivity()
    }
    
    print_report(results)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Verification interrupted by user")
    except Exception as e:
        print(f"\n✗ Verification error: {e}")
        import traceback
        traceback.print_exc()
