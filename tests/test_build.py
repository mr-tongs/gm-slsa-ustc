import os

from generator.build import build

def test_build():
    # remove the output file if it exists
    output_file = "tests/demo_project/output"
    if os.path.exists(output_file):
        os.remove(output_file)
    build("tests/demo_project/test.c", "tests/demo_project/output")
    