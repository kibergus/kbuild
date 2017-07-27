import sh
import os
import sys
from os.path import join, exists

from core import Task
from utils import env, find_files

BUILD_DIR = "build"

def _create_debug_key():
    keystore = join(os.environ["HOME"], ".android/debug.keystore")
    if not exists(keystore):
        sh.Command(join(env("JAVA_HOME"), "bin/keytool"))(
            "-genkey", "-v", "-keystore", keystore,
            "-storepass", "android",
            "-alias", "androiddebugkey",
            "-keypass", "android",
            "-dname", "CN=Android Debug,O=Android,C=US")

def android(builder, api_version, build_tools_version):
    android_home = env("ANDROID_HOME")
    java_home = env("JAVA_HOME")

    source_dir = "app/src/main"
    generated_dir = join(BUILD_DIR, "generated/source")

    def build_tool(tool):
        return sh.Command(join(android_home, "build-tools", build_tools_version, tool))

    def compile_java():
        sources = find_files(source_dir, 'java')
        sources += find_files(join(generated_dir, 'r'), 'java')

        sh.Command(join(java_home, "bin/javac"))(
                "-source", "1.7", "-target", "1.7",
                "-d", join(BUILD_DIR, "obj"),
                "-g",
                "-encoding", "UTF-8",
                "-bootclasspath", join(android_home, "platforms/android-{0}".format(api_version), "android.jar"),
                "-sourcepath", join(BUILD_DIR, "emptySourcePathRef"),
                "-s", source_dir,
                "-XDuseUnsharedTable=true",
                *sources)

    builder.add(
        Task("clean", []).after(
            sh.rm, "-rf", BUILD_DIR
        )
    )

    builder.add(
        Task("resources", []).after(
            sh.mkdir, "-p", join(generated_dir, "r/release")
        ).after(
            build_tool("aapt"),
            "package", "-f", "--no-crunch",
            "-I", join(android_home, "platforms/android-{0}".format(api_version), "android.jar"),
            "-M", join(source_dir, "AndroidManifest.xml"),
            "-S", join(source_dir, "res"),
            "-m",
            "-J", join(generated_dir, "r/release"),
            "-0", "apk"
        ))

    builder.add(Task("compile", ["resources"]).after(
            sh.mkdir, "-p", join(BUILD_DIR, "obj")
        ).after(compile_java))

    builder.add(
        Task("dex", ["compile"]).after(
            sh.rm, "-rf", join(BUILD_DIR, "bin")
        ).after(
            sh.mkdir, "-p", join(BUILD_DIR, "bin")
        ).after(
            build_tool("dx"),
            "--dex", "--verbose",
            "--output=" + join(BUILD_DIR, "bin/classes.dex"),
            join(BUILD_DIR, "obj"),
            "app/libs"
        ))
    
    builder.add(
        Task("package", ["dex"]).after(
            build_tool("aapt"),
            "package", "-v", "-f",
            "-M", join(source_dir, "AndroidManifest.xml"),
            "-S", join(source_dir, "res"),
            "-I", join(android_home,  "platforms/android-{0}".format(api_version), "android.jar"),
            "-F", join(BUILD_DIR, "bin/AndroidTest.unsigned.apk"),
            join(BUILD_DIR, "bin"),
            _out=sys.stdout
        ))

    builder.add(
        Task("sign", ["package"]).after(
            _create_debug_key
        ).after(
            sh.Command(join(java_home, "bin/jarsigner")),
            "-verbose", "-keystore", join(os.environ["HOME"], ".android/debug.keystore"),
            "-storepass", "android",
 	        "-keypass", "android",
	        "-signedjar", join(BUILD_DIR, "bin/AndroidTest.signed.apk"),
            join(BUILD_DIR, "bin/AndroidTest.unsigned.apk"),
	        "androiddebugkey"
        ))

    builder.add(
        Task("zipalign", ["sign"]).after(
            build_tool("zipalign"),
            "-v", "-f", "4",
            join(BUILD_DIR, "bin/AndroidTest.signed.apk"),
            join(BUILD_DIR, "bin/AndroidTest.apk")
        ))

    builder.add(
        Task("install", ["zipalign"]).after(
            sh.Command(join(android_home, "platform-tools/adb")),
            "-d", "install", "-r", join(BUILD_DIR, "bin/AndroidTest.apk"),
            _out=sys.stdout
        ))
