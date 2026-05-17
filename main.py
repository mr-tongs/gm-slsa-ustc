import argparse
import sys
import os
from generator.build import build_artifact
from generator.provenance import generate_dsse_envelope, save_provenance
from verifier.verify import verify_provenance

def cmd_build(args):
    source = args.source or os.getenv("CI_BUILD_SOURCE")
    output = args.output or os.getenv("CI_BUILD_OUTPUT", "demo.exe")
    provenance = args.provenance or os.getenv("CI_PROVENANCE_OUT", "provenance.json")

    if not source:
        print("Error: Source file must be provided via -s or CI_BUILD_SOURCE env var.")
        sys.exit(1)

    try:
        build_info = build_artifact(source, output)
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)
        
    builder_id = os.getenv("CI_PIPELINE_ID", "Trust-GM-Builder-01")
    envelope = generate_dsse_envelope(build_info, builder_id=builder_id)
    
    save_provenance(envelope, provenance)
    print(f"Build and provenance generation completed successfully.")

def cmd_verify(args):
    artifact = args.artifact or os.getenv("CD_ARTIFACT_PATH")
    provenance = args.provenance or os.getenv("CD_PROVENANCE_PATH")

    if not artifact or not provenance:
        print("Error: Artifact and Provenance paths must be provided.")
        sys.exit(1)

    try:
        if verify_provenance(artifact, provenance):
            pass
    except Exception as e:
        print(f"Verification failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="GM-SLSA")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    subparsers.required = True

    parser_build = subparsers.add_parser("build", help="编译源码并生成 SLSA 溯源证明")
    parser_build.add_argument("-s", "--source", help="源文件路径 (默认读取 CI_BUILD_SOURCE)")
    parser_build.add_argument("-o", "--output", help="输出可执行文件路径")
    parser_build.add_argument("-p", "--provenance", help="生成的凭证文件存储路径")
    parser_build.set_defaults(func=cmd_build)

    parser_verify = subparsers.add_parser("verify", help="验证产物及其 SLSA 证明")
    parser_verify.add_argument("-a", "--artifact", help="待验证的构建产物文件")
    parser_verify.add_argument("-p", "--provenance", help="相应的证明文件")
    parser_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()