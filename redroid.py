#!/usr/bin/env python3

import argparse
from stuff.litegapps import LiteGapps
from stuff.houdini import Houdini
from stuff.houdini_hack import Houdini_Hack
from stuff.ndk_translation import NdkTranslation
import tools.helper as helper
import subprocess
import platform


def is_amd_processor():
    """Detect if running on AMD processor"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read().lower()
            # Check for AMD vendor ID
            if 'authenticamd' in cpuinfo or 'vendor_id.*amd' in cpuinfo:
                return True
            # Check for AMD-specific CPU flags
            if 'svm' in cpuinfo and 'vendor_id' in cpuinfo and 'amd' in cpuinfo:
                return True
    except:
        pass
    return False


def main():
    dockerfile = ""
    tags = []
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-a', '--android-version',
                        dest='android',
                        help='Specify the Android version to build',
                        default='13.0.0',
                        choices=['13.0.0'])
    parser.add_argument('-lg', '--install-litegapps',
                        dest='litegapps',
                        help='Install LiteGapps to ReDroid',
                        action='store_true')
    parser.add_argument('-i', '--install-houdini',
                        dest='houdini',
                        help='Install houdini or ndk_translation files (auto-detects AMD)',
                        action='store_true')
    parser.add_argument('-c', '--container', 
                        dest='container',
                        default='docker',
                        help='Specify container type', 
                        choices=['docker', 'podman'])

    args = parser.parse_args()
    dockerfile = dockerfile + \
        "FROM geanswag/swagplayer:{}\n".format(
            args.android)
    tags.append(args.android)
    if args.litegapps:
        LiteGapps(args.android).install()
        dockerfile = dockerfile + "COPY litegapps /\n"
        tags.append("litegapps")
    if args.houdini:
        arch = helper.host()[0]
        if arch == "x86" or arch == "x86_64":
            # Auto-detect AMD and use NDK Translation instead of Houdini
            if is_amd_processor():
                print("\n" + "="*60)
                print("AMD processor detected - using NDK Translation")
                print("="*60)
                NdkTranslation().install()
                dockerfile = dockerfile + "COPY ndk_translation /\n"
                tags.append("ndk_translation")
            else:
                print("\n" + "="*60)
                print("Intel processor detected - using Houdini")
                print("="*60)
                Houdini(args.android).install()
                Houdini_Hack(args.android).install()
                dockerfile = dockerfile + "COPY houdini /\n"
                tags.append("houdini")
    print("\nDockerfile\n"+dockerfile)
    with open("./Dockerfile", "w") as f:
        f.write(dockerfile)
    new_image_name = "geanswag/swagplayer:"+"_".join(tags)
    subprocess.run([args.container, "build", "-t", new_image_name, "."])
    helper.print_color("Successfully built {}".format(
        new_image_name), helper.bcolors.GREEN)


if __name__ == "__main__":
    main()
