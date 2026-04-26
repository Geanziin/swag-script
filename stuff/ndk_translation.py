import os
import shutil
import tarfile
from stuff.general import General
from tools.helper import bcolors, get_download_dir, print_color, run

class NdkTranslation(General):
    """
    NDK Translation for AMD processors.
    Replaces libhoudini on AMD systems for better ARM app compatibility.
    """
    download_loc = get_download_dir()
    copy_dir = "./ndk_translation"
    # Local tar file (bundled with swag-script)
    tar_file_name = os.path.join(os.path.dirname(__file__), "..", "libndk_translation-13.0.0.tar")
    extract_to = "/tmp/ndktranslationunpack"
    
    init_rc_component = """
# NDK Translation for AMD processors
on early-init
    mount binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc

on property:ro.enable.native.bridge.exec=1
    copy /system/etc/binfmt_misc/arm_exe /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm_dyn /proc/sys/fs/binfmt_misc/register

on property:ro.enable.native.bridge.exec64=1
    copy /system/etc/binfmt_misc/arm64_exe /proc/sys/fs/binfmt_misc/register
    copy /system/etc/binfmt_misc/arm64_dyn /proc/sys/fs/binfmt_misc/register
"""

    def download(self):
        """Override download - we use local tar file instead"""
        print_color("Using bundled libndk_translation-13.0.0.tar ...", bcolors.GREEN)
        # No download needed, file is local
        pass

    def extract(self):
        """Extract the local tar file"""
        print_color("Extracting libndk_translation archive...", bcolors.GREEN)
        
        # Clean previous extraction
        if os.path.exists(self.extract_to):
            shutil.rmtree(self.extract_to)
        os.makedirs(self.extract_to, exist_ok=True)
        
        # Extract tar file
        tar_path = os.path.abspath(self.tar_file_name)
        if not os.path.exists(tar_path):
            raise FileNotFoundError(f"NDK Translation tar not found: {tar_path}")
        
        with tarfile.open(tar_path, "r") as tar:
            tar.extractall(path=self.extract_to)
        
        print_color(f"Extracted to {self.extract_to}", bcolors.GREEN)

    def copy(self):
        """Copy NDK Translation files to the build directory"""
        if os.path.exists(self.copy_dir):
            shutil.rmtree(self.copy_dir)
        
        print_color("Copying libndk_translation library files ...", bcolors.GREEN)
        
        # Find the prebuilts directory in extracted tar
        prebuilts_path = None
        for root, dirs, files in os.walk(self.extract_to):
            if "prebuilts" in dirs:
                prebuilts_path = os.path.join(root, "prebuilts")
                break
        
        if not prebuilts_path:
            raise FileNotFoundError("Could not find prebuilts directory in extracted tar")
        
        # Copy to ndk_translation/system
        shutil.copytree(prebuilts_path, os.path.join(self.copy_dir, "system"), dirs_exist_ok=True)
        
        # Create init.rc file
        init_path = os.path.join(self.copy_dir, "system", "etc", "init", "ndk_translation.rc")
        os.makedirs(os.path.dirname(init_path), exist_ok=True)
        with open(init_path, "w") as initfile:
            initfile.write(self.init_rc_component)
        os.chmod(init_path, 0o644)
        
        print_color("NDK Translation files copied successfully", bcolors.GREEN)
