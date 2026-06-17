# lbssb-staruml Demo

This directory contains static examples only. It does not include StarUML binaries, user `.mdj` files, or generated diagrams.

Use the examples to understand the expected manifest and verification report shape.

Commands:

```powershell
powershell -ExecutionPolicy Bypass -File lbssb-staruml/tools/check_staruml_preflight.ps1
python lbssb-staruml/tools/validate_manifest.py --manifest lbssb-staruml/demo/expected-manifest.json
python lbssb-staruml/tools/verify_deliverables.py --manifest lbssb-staruml/demo/expected-manifest.json --preflight lbssb-staruml/demo/preflight-report.example.json
```

The last command is expected to fail in a clean checkout because the example PNG and `.mdj` files are placeholders.
