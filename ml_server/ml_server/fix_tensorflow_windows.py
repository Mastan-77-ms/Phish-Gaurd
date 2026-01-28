"""
Fix TensorFlow installation on Windows
This script handles the Windows Long Path limitation issue
"""

import os
import subprocess
import sys
import shutil

def enable_long_paths_registry():
    """Enable Windows Long Path support via registry (requires admin)"""
    print("[FIX] Attempting to enable Windows Long Paths...")
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SYSTEM\CurrentControlSet\Control\FileSystem",
                            access=winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "LongPathsEnabled", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        print("✓ Long Paths enabled (restart required)")
        return True
    except Exception as e:
        print(f"✗ Cannot enable Long Paths (may need admin): {e}")
        return False

def fix_tensorflow_windows():
    """Fix TensorFlow installation on Windows"""
    print("\n" + "="*70)
    print("  TensorFlow Windows Installation Fix")
    print("="*70)
    
    print("\n[OPTION 1] Install TensorFlow with cpu variant (simpler):")
    print("  $ pip install tensorflow-cpu")
    
    print("\n[OPTION 2] Use pre-built wheel (if available):")
    print("  $ pip install --upgrade tensorflow")
    
    print("\n[OPTION 3] Install to shorter path:")
    print("  1. Create: C:\\tf_env")
    print("  2. Run: python -m venv C:\\tf_env")
    print("  3. Activate: C:\\tf_env\\Scripts\\activate")
    print("  4. Install: pip install tensorflow")
    
    print("\n[RECOMMENDED] Method for your system:")
    print("─" * 70)
    print("\nStep 1: Uninstall current TensorFlow")
    print("  $ pip uninstall tensorflow -y")
    
    print("\nStep 2: Install TensorFlow CPU (lighter, faster)")
    print("  $ pip install tensorflow-cpu --upgrade")
    
    print("\nStep 3: Test installation")
    print("  $ python -c \"import tensorflow as tf; print(tf.__version__)\"")
    
    print("\n" + "="*70)
    print("  OR Try This Quick Fix")
    print("="*70)
    
    print("\nRunning automated fix attempt...")
    
    try:
        # Try to uninstall and reinstall with no-deps
        print("\n[STEP 1] Clearing TensorFlow cache...")
        subprocess.run([sys.executable, "-m", "pip", "cache", "purge"],
                      capture_output=True)
        
        print("[STEP 2] Uninstalling TensorFlow...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", 
                       "tensorflow", "-y"],
                      capture_output=True)
        
        print("[STEP 3] Installing TensorFlow CPU (lighter)...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", 
             "tensorflow-cpu", "--upgrade"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ TensorFlow installed successfully!")
            print("\n[VERIFICATION] Testing import...")
            test_result = subprocess.run(
                [sys.executable, "-c", 
                 "import tensorflow as tf; print(f'TensorFlow {tf.__version__}')"],
                capture_output=True,
                text=True
            )
            print(test_result.stdout)
            return True
        else:
            print("✗ Installation failed")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║        TensorFlow Windows Installation Troubleshooter              ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    print("\nDiagnosing TensorFlow installation issue...")
    print("\nThe problem: Windows Long Path support is not enabled")
    print("This causes TensorFlow installation to fail with long file paths")
    
    print("\n" + "="*70)
    print("  RECOMMENDED SOLUTION")
    print("="*70)
    
    print("""
The easiest fix is to install tensorflow-cpu instead of full tensorflow:

1. Open PowerShell (as administrator)
2. Run this command:
   
   pip install tensorflow-cpu --upgrade

This is:
  ✓ Lighter (faster download)
  ✓ Uses less disk space
  ✓ Avoids long path issues
  ✓ Perfect for CPU-only inference
  ✓ Same functionality for phishing detection

3. Then verify it works:
   
   python -c "import tensorflow as tf; print(tf.__version__)"

If that works, you can then run the training:
   
   python train_dl_model.py
""")
    
    print("="*70)
    print("  ALTERNATIVE SOLUTIONS")
    print("="*70)
    
    print("""
Option A: Enable Windows Long Paths (requires admin)
  1. Run PowerShell as Administrator
  2. Run: python fix_tensorflow_windows.py
  3. Restart your computer
  4. Try again: pip install tensorflow

Option B: Use conda instead of pip
  1. Install Anaconda from: https://www.anaconda.com/download
  2. Open Anaconda Prompt
  3. Run: conda install tensorflow
  
Option C: Use Linux/WSL2
  If you have Windows Subsystem for Linux 2:
  1. Install TensorFlow in WSL2
  2. Run PhishGuard from WSL2 terminal
  
Option D: Docker
  Run PhishGuard inside Docker (avoids all Windows issues)
""")
    
    print("="*70)
    print("  QUICK COMMAND TO RUN NOW")
    print("="*70)
    print("""
Copy and paste this entire command in PowerShell:

pip uninstall tensorflow -y; pip cache purge; pip install tensorflow-cpu --upgrade; python -c "import tensorflow as tf; print(f'✓ TensorFlow {tf.__version__} installed!')"

This will:
1. Uninstall broken TensorFlow
2. Clear pip cache
3. Install tensorflow-cpu
4. Verify installation

Then you can try training again!
""")
    
    print("="*70)
    print("  Next Step")
    print("="*70)
    print("\nAfter fixing TensorFlow, run:")
    print("  python quick_start.py")
    print("\nThen choose option 2 to train the model")
    
    input("\n[Press Enter to close this window]")

if __name__ == "__main__":
    main()
