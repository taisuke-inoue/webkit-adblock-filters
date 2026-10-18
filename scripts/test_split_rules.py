import unittest
from split_rules import split_rules

def rule(action, match):
    return {"trigger": {"url-filter": match}, "action": {"type": action}}

def evaluate(rules, matched):
    actions = []
    for r in rules:
        if r["trigger"]["url-filter"] in matched:
            if r["action"]["type"] == "ignore-previous-rules": actions.clear()
            else: actions.append(id(r))
    return set(actions)

class SplitTests(unittest.TestCase):
    def test_ordered_exceptions_and_later_important_rules(self):
        rules = [rule("block", "a"), rule("block-cookies", "b"), rule("ignore-previous-rules", "x"),
                 rule("css-display-none", "a"), rule("ignore-previous-rules", "y"), rule("block", "b")]
        chunks = split_rules(rules, 4)
        self.assertEqual(len(chunks), 2)
        for mask in range(16):
            matched = {c for i,c in enumerate("abxy") if mask & (1 << i)}
            self.assertEqual(evaluate(rules, matched), set().union(*(evaluate(c, matched) for c in chunks)))
    def test_capacity_and_no_loss(self):
        rules = [rule("block", str(i)) for i in range(148001)] + [rule("ignore-previous-rules", "x")]
        chunks = split_rules(rules)
        self.assertEqual([len(c) for c in chunks], [148000, 3])
        self.assertEqual(sum(len(c)-1 for c in chunks), 148001)
    def test_reject_unsupported_and_exception_overflow(self):
        with self.assertRaises(ValueError): split_rules([rule("ignore-following-rules", "x")])
        with self.assertRaises(ValueError): split_rules([rule("ignore-previous-rules", "x")], 1)

if __name__ == "__main__": unittest.main()
