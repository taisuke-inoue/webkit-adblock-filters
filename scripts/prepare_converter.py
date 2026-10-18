"""Explicit, version-pinned build customization: defer the count limit to splitting."""
from pathlib import Path
import sys
root = Path(sys.argv[1])
p = root / "Sources/ContentBlockerConverter/Rules/SafariVersion.swift"
s = p.read_text()
old = "return self.doubleValue >= SafariVersion.safari15.doubleValue ? 150000 : 50000"
assert s.count(old) == 1, "Converter changed; review required"
p.write_text(s.replace(old, "return Int.max // OneBar: split after full conversion"))
p = root / "Sources/ConverterTool/Commands/ConvertCommand.swift"
if not p.exists():
    matches = list(root.glob("Sources/**/ConvertCommand.swift"))
    assert len(matches) == 1
    p = matches[0]
s = p.read_text()
needle = '        Logger.log("(Convert) - Conversion done.")'
assert s.count(needle) == 1
s = s.replace(needle, needle + '\n        guard result.discardedSafariRules == 0 else { throw NSError(domain: "RuleTruncation", code: 1) }\n        print(result.description)')
p.write_text(s)
